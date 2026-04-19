import os
import ast
import json
import logging
import re
import threading
import time
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class SkillRegistrar:
    def __init__(self, skills_dir: str):
        self.skills_dir = skills_dir
        self.cache_path = os.path.join(skills_dir, "_registry.json")
        self.tools = {}      # {name: {path, description, type: "python"}}
        self.playbooks = {}   # {name: {path, summary, type: "markdown"}}
        self._scan_complete = threading.Event()

    # ──────────────────────────────────────────────────────────────────
    # CACHE-FIRST: Load from _registry.json instantly (~5ms)
    # Then schedule a background rescan to keep cache fresh.
    # ──────────────────────────────────────────────────────────────────

    def scan_and_index(self, force: bool = False):
        """
        Cache-first scan: loads from _registry.json instantly.
        Only falls back to full filesystem walk if cache is missing/corrupt.
        Background thread rescans to keep cache fresh.
        """
        if not force and self._try_load_cache():
            logger.info(f"⚡ Registrar: Loaded from cache — {len(self.tools)} tools, {len(self.playbooks)} playbooks (instant)")
            self._scan_complete.set()
            # Background: rescan filesystem and update cache if stale
            threading.Thread(target=self._background_rescan, daemon=True).start()
            return

        # Cache miss or forced — full scan (slow path)
        logger.info(f"🔍 Registrar: Cache miss — performing full scan of {self.skills_dir}...")
        self._full_scan()
        self._scan_complete.set()

    def _try_load_cache(self) -> bool:
        """Attempt to load tools and playbooks from _registry.json cache."""
        try:
            if not os.path.exists(self.cache_path):
                return False

            with open(self.cache_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            cached_tools = data.get("tools", {})
            cached_playbooks = data.get("playbooks", {})

            if not cached_tools and not cached_playbooks:
                return False

            cached_mtime = data.get("last_updated")
            current_mtime = os.path.getmtime(self.skills_dir)
            if cached_mtime and current_mtime > float(cached_mtime):
                logger.info("🔄 Registrar: Cache is stale — rebuilding tool/playbook index")
                return False

            self.tools = cached_tools
            self.playbooks = cached_playbooks
            return True

        except Exception as e:
            logger.warning(f"⚠️ Registrar: Cache load failed ({e}) — will do full scan")
            return False

    def _background_rescan(self):
        """Rescan the filesystem in background and update cache if content changed."""
        try:
            # Removed time.sleep(5) for Nuclear Startup speed
            old_tools_count = len(self.tools)
            old_playbooks_count = len(self.playbooks)

            self._full_scan()

            new_t = len(self.tools)
            new_p = len(self.playbooks)
            if new_t != old_tools_count or new_p != old_playbooks_count:
                logger.info(f"🔄 Registrar: Background rescan updated — {new_t} tools, {new_p} playbooks")
            else:
                logger.debug("✅ Registrar: Background rescan — cache was up to date")
        except Exception as e:
            logger.warning(f"⚠️ Registrar: Background rescan failed: {e}")

    def _full_scan(self):
        """Full filesystem walk — the original slow path."""
        # Directories to skip — these contain third-party example scripts
        # and template files, not AgentTool classes.
        _SKIP_DIRS = {"scripts", "templates", "assets", "references", "resources", "ooxml"}

        new_tools = {}
        new_playbooks = {}

        for root, dirs, files in os.walk(self.skills_dir):
            # ── Prune walk: don't descend into known non-tool directories ──
            dirs[:] = [d for d in dirs if d not in _SKIP_DIRS]

            for file in files:
                if file.startswith("_"): continue

                path = os.path.join(root, file)

                # 1. Handle Python Tools
                if file.endswith(".py"):
                    tools_in_file = self._parse_python_tools_bulk(path)
                    for t_name, t_meta in tools_in_file.items():
                        new_tools[t_name] = {
                            "path": path,
                            "description": t_meta["description"],
                            "type": "python",
                            "class_name": t_meta["class_name"]
                        }

                # 2. Handle Markdown Playbooks
                elif file.endswith(".md") or file == "SKILL.md":
                    if file.upper() in ["README.MD", "LICENSE", "CONTRIBUTING.MD", "SECURITY.MD"]:
                        continue
                    playbook_meta = self._parse_markdown_playbook(path)
                    if playbook_meta:
                        name = playbook_meta["name"].lower().replace(" ", "-")
                        new_playbooks[name] = {
                            "path": path,
                            "title": playbook_meta["name"],
                            "summary": playbook_meta["summary"],
                            "risk": playbook_meta.get("risk", "unknown"),
                            "type": "markdown"
                        }

        self.tools = new_tools
        self.playbooks = new_playbooks
        self._save_cache()
        logger.info(f"✅ Registrar: Indexed {len(self.tools)} tools and {len(self.playbooks)} playbooks.")


    def _parse_python_tools_bulk(self, path: str) -> Dict[str, Dict[str, str]]:
        """Uses AST to extract all tool names and descriptions from a file."""
        found_tools = {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read())
                
            for node in tree.body:
                if isinstance(node, ast.ClassDef):
                    t_name = None
                    t_description = None
                    
                    for item in node.body:
                        if isinstance(item, ast.Assign):
                            for target in item.targets:
                                if isinstance(target, ast.Name):
                                    if target.id == "name" and isinstance(item.value, ast.Constant):
                                        t_name = item.value.value
                                    if target.id == "description" and isinstance(item.value, ast.Constant):
                                        t_description = item.value.value
                    
                    if t_name and t_description:
                        found_tools[t_name] = {
                            "description": t_description, 
                            "class_name": node.name
                        }
        except Exception as e:
            logger.error(f"❌ Registrar: Error parsing Python tool {path}: {e}")
        return found_tools

    def _parse_markdown_playbook(self, path: str) -> Optional[Dict[str, str]]:
        """
        Extracts metadata from SKILL.md. 
        Supports YAML frontmatter and H1 fallback.
        """
        try:
            import yaml
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                
            # 1. Try YAML Frontmatter
            frontmatter_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
            if frontmatter_match:
                try:
                    meta = yaml.safe_load(frontmatter_match.group(1))
                    if isinstance(meta, dict):
                        return {
                            "name": meta.get("name", os.path.basename(os.path.dirname(path))).replace("-", " ").title(),
                            "summary": meta.get("description", "Expert playbook."),
                            "risk": meta.get("risk", "unknown")
                        }
                except Exception as ye:
                    # Silently skip template files with {{HANDLEBARS}} placeholders
                    logger.debug(f"Registrar: skipping template playbook {os.path.basename(path)}: {ye}")


            # 2. Fallback to H1 and first paragraph
            h1_match = re.search(r"^#\s+(.*)$", content, re.MULTILINE)
            title = h1_match.group(1).strip() if h1_match else os.path.basename(path)
            
            lines = content.split("\n")
            summary = ""
            for line in lines:
                line = line.strip()
                if not line or line.startswith("#"): continue
                summary = line
                if len(summary) > 200: summary = summary[:197] + "..."
                break
                
            return {"name": title, "summary": summary}
        except Exception as e:
            logger.error(f"❌ Registrar: Error parsing Playbook {path}: {e}")
        return None

    def _save_cache(self):
        try:
            with open(self.cache_path, "w", encoding="utf-8") as f:
                json.dump({
                    "tools": self.tools,
                    "playbooks": self.playbooks,
                    "last_updated": os.path.getmtime(self.skills_dir)
                }, f, indent=4)
        except Exception as e:
            logger.error(f"❌ Registrar: Failed to save cache: {e}")

    def get_playbooks(self) -> Dict[str, Dict[str, Any]]:
        return self.playbooks

    def get_tools(self) -> Dict[str, Dict[str, Any]]:
        return self.tools
