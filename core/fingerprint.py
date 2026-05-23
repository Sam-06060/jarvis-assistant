"""
core/fingerprint.py — Codebase fingerprinting for Jarvis boot cache.

Two levels of fingerprinting:

  1. GLOBAL fingerprint  — MD5 of ALL source files + config mtimes.
     Used as the master invalidation key. If this changes, the full
     boot cache is discarded and a cold boot runs.

  2. COMPONENT fingerprints — targeted hashes for specific subsystems.
     Allows partial cache invalidation: touching a skill file only
     re-runs skill loading, not the full init pipeline.

     Components:
       'core'     — jarvis.py, core/, utils/, config.py, .env
       'skills'   — modules/skills/, custom_skills/, modules/commands.py
       'semantic' — modules/agent_skills/_registry.json

Files included in global fingerprint:
  - All *.py files in: root, core/, modules/, utils/, custom_skills/
  - .env mtime, requirements.txt mtime

Files excluded:
  - __pycache__, .git, data/, logs/, .venv/, venv/, build/, dist/
"""

import hashlib
import os
import time
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)

# Directories to scan for .py files (relative to project root)
_SCAN_DIRS = ["core", "modules", "utils", "custom_skills", "preload.py"]
# Extra files whose mtime is included in the fingerprint
_MTIME_FILES = [".env", "requirements.txt", "config.py"]
# Directory names to skip entirely during scan
_SKIP_DIRS = {"__pycache__", ".git", "data", "logs", ".venv", "venv",
              "build", "dist", ".mypy_cache", ".pytest_cache", "node_modules"}

# ── Component scan definitions ───────────────────────────────────────────────
# Each component maps to the files/dirs whose changes should invalidate only
# that component’s cache entry, not the entire boot cache.
_COMPONENT_SCAN: Dict[str, dict] = {
    "core": {
        # Changes here invalidate everything — boot pipeline itself changed
        "files": ["jarvis.py", "config.py", "preload.py"],
        "dirs": ["core", "utils"],
        "mtime_files": [".env", "requirements.txt"],
    },
    "skills": {
        # Skill changes only invalidate skill loading — not GroqClient/SemanticRouter
        "files": ["modules/commands.py", "modules/registrar.py"],
        "dirs": ["modules/skills", "custom_skills"],
        "mtime_files": [],
    },
    "semantic": {
        # Playbook registry changes only invalidate the vector index
        "files": ["modules/agent_skills/_registry.json"],
        "dirs": [],
        "mtime_files": [],
    },
}


def compute_fingerprint(project_root: str) -> str:
    """
    Hash all source files + config mtimes under project_root.

    Returns a hex MD5 digest that changes only when code or config changes.
    Typical runtime: ~30-60ms for ~150 Python files.
    """
    t0 = time.time()
    h = hashlib.md5()

    # ── 1. Hash all .py file contents ────────────────────────────────────────
    py_files = _collect_py_files(project_root)
    py_files.sort()  # deterministic order regardless of filesystem

    for path in py_files:
        try:
            # Include the relative path so renames invalidate the cache
            rel = os.path.relpath(path, project_root)
            h.update(rel.encode())
            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(65536), b""):
                    h.update(chunk)
        except (OSError, IOError):
            # File unreadable — still include path so presence is fingerprinted
            h.update(path.encode())

    # ── 2. Include mtime of special files ───────────────────────────────────
    for rel_path in _MTIME_FILES:
        full_path = os.path.join(project_root, rel_path)
        try:
            mtime = str(os.path.getmtime(full_path))
            h.update(rel_path.encode())
            h.update(mtime.encode())
        except OSError:
            pass  # File doesn't exist — skip

    digest = h.hexdigest()
    elapsed_ms = int((time.time() - t0) * 1000)
    logger.debug(f"🔍 Fingerprint computed in {elapsed_ms}ms — {len(py_files)} files — {digest[:8]}...")
    return digest


def _collect_py_files(project_root: str) -> list[str]:
    """Walk project directories and collect all .py file paths."""
    collected: list[str] = []

    for entry in _SCAN_DIRS:
        target = os.path.join(project_root, entry)

        if os.path.isfile(target) and target.endswith(".py"):
            collected.append(target)
            continue

        if not os.path.isdir(target):
            continue

        for dirpath, dirnames, filenames in os.walk(target):
            # Prune excluded directories in-place (modifies the walk)
            dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS]
            for fname in filenames:
                if fname.endswith(".py"):
                    collected.append(os.path.join(dirpath, fname))

    # Also include root-level .py files (jarvis.py, config.py, etc.)
    try:
        for fname in os.listdir(project_root):
            if fname.endswith(".py") and os.path.isfile(os.path.join(project_root, fname)):
                full = os.path.join(project_root, fname)
                if full not in collected:
                    collected.append(full)
    except OSError:
        pass

    return collected


def fingerprint_matches(project_root: str, cached_fingerprint: Optional[str]) -> bool:
    """
    Returns True if the current codebase fingerprint matches the cached one.
    Safe to call with cached_fingerprint=None (always returns False → cold boot).
    """
    if not cached_fingerprint:
        return False
    current = compute_fingerprint(project_root)
    return current == cached_fingerprint


def compute_component_fingerprint(project_root: str, component: str) -> Optional[str]:
    """
    Compute a fingerprint for a specific component (core / skills / semantic).

    Returns None if the component name is unknown.
    Allows boot_cache.py to do targeted cache invalidation:
      - Skill file changed → invalidate 'skills' entry only
      - Core/config changed → invalidate everything
    """
    spec = _COMPONENT_SCAN.get(component)
    if not spec:
        return None

    h = hashlib.md5()
    h.update(component.encode())  # domain prefix so different components can't collide

    # Hash specific files
    for rel_path in spec.get("files", []):
        full = os.path.join(project_root, rel_path)
        # For JSON / non-py files, include mtime + size (faster than full hash)
        if rel_path.endswith(".json"):
            try:
                stat = os.stat(full)
                h.update(rel_path.encode())
                h.update(str(stat.st_mtime).encode())
                h.update(str(stat.st_size).encode())
            except OSError:
                pass
        else:
            # Full content hash for source files
            try:
                h.update(rel_path.encode())
                with open(full, "rb") as f:
                    for chunk in iter(lambda: f.read(65536), b""):
                        h.update(chunk)
            except OSError:
                pass

    # Hash all .py files in component directories
    for rel_dir in spec.get("dirs", []):
        full_dir = os.path.join(project_root, rel_dir)
        if not os.path.isdir(full_dir):
            continue
        for dirpath, dirnames, filenames in os.walk(full_dir):
            dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS]
            for fname in sorted(filenames):
                if fname.endswith(".py") or fname.endswith(".json"):
                    full_path = os.path.join(dirpath, fname)
                    rel = os.path.relpath(full_path, project_root)
                    try:
                        h.update(rel.encode())
                        with open(full_path, "rb") as f:
                            for chunk in iter(lambda: f.read(65536), b""):
                                h.update(chunk)
                    except OSError:
                        pass

    # Include mtimes of special config files
    for rel_path in spec.get("mtime_files", []):
        full = os.path.join(project_root, rel_path)
        try:
            h.update(rel_path.encode())
            h.update(str(os.path.getmtime(full)).encode())
        except OSError:
            pass

    return h.hexdigest()


def compute_all_component_fingerprints(project_root: str) -> Dict[str, str]:
    """Compute fingerprints for all known components in one pass."""
    return {
        component: compute_component_fingerprint(project_root, component)
        for component in _COMPONENT_SCAN
    }
