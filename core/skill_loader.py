"""
core/skill_loader.py — Fault-isolated, auto-discovering skill loader.

Replaces the monolithic pool.map() in CommandProcessor with three improvements:

1. FAULT ISOLATION: Each skill loads in its own try/except.
   One broken skill cannot prevent others from loading.

2. AUTO-DISCOVERY: Scans `custom_skills/` directory automatically.
   Drop a file there, inherit from Skill → it appears in Jarvis.
   Zero code changes needed anywhere else.

3. CLEAR ERROR REPORTING: Failed skills log the full traceback
   so the user knows exactly which skill broke and why.
"""

import os
import sys
import importlib
import importlib.util
import inspect
import logging
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Any

logger = logging.getLogger(__name__)

# Path to the built-in skills directory
_BUILTIN_SKILLS_MODULE = "modules.skills"

# Hardcoded built-in skill class names (in load priority order)
# SmartThings first: it has the most specific matchers, must win ties.
_BUILTIN_SKILL_CLASSES = [
    "SmartThingsSkill",
    "InteractionSkill",
    "SystemSkill",
    "FocusSkill",
    "InternetSkill",
    "TimeSkill",
    "ReminderSkill",
    "AnalyticsSkill",
    "TranslatorSkill",
    "AlarmSkill",
    "WeatherSkill",
    "NewsSkill",
    "CalculatorSkill",
    "AppControlSkill",
    "FileSkill",
    "CommunicationSkill",
    "ShortcutsSkill",
    "ArchitectSkill",
    "MusicSkill",
    "ResearchSkill",
    "AutomationSkill",
]


def _load_one_skill(cls, app_context: dict) -> Any:
    """
    Instantiate a single skill class with full fault isolation.
    Returns the instance, or None on failure (never raises).
    """
    skill_name = getattr(cls, '__name__', str(cls))
    try:
        instance = cls(app_context)
        logger.debug(f"  ✅ {skill_name}")
        return instance
    except Exception:
        logger.error(
            f"  ❌ Skill failed to load: {skill_name}\n"
            f"{traceback.format_exc()}"
        )
        return None


def _discover_custom_skills(custom_skills_dir: str) -> List[type]:
    """
    Auto-discover skill classes in the custom_skills/ directory.

    Rules:
      - Scans all .py files in custom_skills/ (non-recursive)
      - Finds all classes that inherit from modules.skills.base.Skill
      - Skips files that raise on import (logs the error)
      - Returns list of classes in filename-alphabetical order

    To add a custom skill:
      1. Create custom_skills/my_skill.py
      2. Define a class that inherits from Skill (from modules.skills.base)
      3. Implement can_handle() and handle()
      4. Restart Jarvis — it appears automatically
    """
    if not os.path.isdir(custom_skills_dir):
        return []

    # Import base class for isinstance check
    try:
        from modules.skills.base import Skill as BaseSkill
    except ImportError:
        logger.warning("⚠️ [SkillLoader] Cannot import BaseSkill — custom skill discovery skipped.")
        return []

    discovered = []
    py_files = sorted(
        f for f in os.listdir(custom_skills_dir)
        if f.endswith(".py") and not f.startswith("_")
    )

    for fname in py_files:
        module_path = os.path.join(custom_skills_dir, fname)
        module_name = f"custom_skills.{fname[:-3]}"
        try:
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            if not spec or not spec.loader:
                continue
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            # Find all classes in this module that are concrete Skill subclasses
            for _, obj in inspect.getmembers(module, inspect.isclass):
                if (
                    obj.__module__ == module_name      # defined in this file (not imported)
                    and issubclass(obj, BaseSkill)
                    and obj is not BaseSkill
                    and not inspect.isabstract(obj)
                ):
                    discovered.append(obj)
                    logger.info(f"🔌 [SkillLoader] Custom skill discovered: {obj.__name__} ({fname})")

        except Exception:
            logger.error(
                f"❌ [SkillLoader] Failed to import custom skill file: {fname}\n"
                f"{traceback.format_exc()}"
            )

    return discovered


def load_all_skills(app_context: dict, project_root: str) -> List[Any]:
    """
    Main entry point. Load all built-in + custom skills with full fault isolation.

    - Each skill instantiation is individually protected by try/except
    - A single broken skill never prevents others from loading
    - Custom skills in custom_skills/ are auto-discovered and appended
    - Returns only the successfully loaded instances

    Args:
        app_context: The _LiveContext / app dict passed to each skill
        project_root: Project root directory (for locating custom_skills/)

    Returns:
        List of successfully instantiated skill instances
    """
    t0 = time.time()

    # ── 1. Collect built-in skill classes ────────────────────────────────────
    builtin_classes = []
    for class_name in _BUILTIN_SKILL_CLASSES:
        try:
            # SmartThingsSkill lives in its own submodule
            if class_name == "SmartThingsSkill":
                from modules.skills.smartthings_skill import SmartThingsSkill
                builtin_classes.append(SmartThingsSkill)
            else:
                mod = importlib.import_module(_BUILTIN_SKILLS_MODULE)
                cls = getattr(mod, class_name, None)
                if cls:
                    builtin_classes.append(cls)
                else:
                    logger.warning(f"⚠️ [SkillLoader] Built-in class not found: {class_name}")
        except Exception:
            logger.error(
                f"❌ [SkillLoader] Failed to import built-in skill class: {class_name}\n"
                f"{traceback.format_exc()}"
            )

    # ── 2. Discover custom skills ─────────────────────────────────────────────
    custom_dir = os.path.join(project_root, "custom_skills")
    custom_classes = _discover_custom_skills(custom_dir)
    if custom_classes:
        logger.info(f"🔌 [SkillLoader] {len(custom_classes)} custom skill(s) found: "
                    f"{[c.__name__ for c in custom_classes]}")

    all_classes = builtin_classes + custom_classes
    logger.info(f"🔧 [SkillLoader] Loading {len(all_classes)} skills "
                f"({len(builtin_classes)} built-in + {len(custom_classes)} custom)...")

    # ── 3. Parallel load with per-skill fault isolation ───────────────────────
    loaded: List[Any] = []
    failed: List[str] = []

    with ThreadPoolExecutor(max_workers=len(all_classes), thread_name_prefix="SkillLoad") as pool:
        future_to_cls = {
            pool.submit(_load_one_skill, cls, app_context): cls
            for cls in all_classes
        }
        # Collect in submission order to preserve priority
        results = {}
        for future in as_completed(future_to_cls):
            cls = future_to_cls[future]
            results[cls] = future.result()

    # Re-apply original ordering (priority matters for can_handle() resolution)
    for cls in all_classes:
        result = results.get(cls)
        if result is not None:
            loaded.append(result)
        else:
            failed.append(getattr(cls, '__name__', str(cls)))

    elapsed = time.time() - t0
    logger.info(
        f"⚡ [SkillLoader] Done in {elapsed:.2f}s — "
        f"{len(loaded)} loaded, {len(failed)} failed"
        + (f" ❌ FAILED: {failed}" if failed else "")
    )
    return loaded
