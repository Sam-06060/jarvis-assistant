import json
import os
import re
from typing import Dict, List, Any

def generate_catalog():
    registry_path = "modules/agent_skills/_registry.json"
    output_path = "modules/agent_skills/ultimateskillinfo.md"
    
    if not os.path.exists(registry_path):
        print(f"Error: Registry not found at {registry_path}")
        return

    with open(registry_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    tools = data.get("tools", {})
    playbooks = data.get("playbooks", {})
    
    lines = []
    lines.append("# JARVIS Ultimate Skill Info Catalog")
    lines.append("\nThis document provides a concise reference for all core tools and expert playbooks available in Jarvis Agentic Mode.")
    
    # 1. Core Tools
    lines.append("\n## 🛠️ Core Agentic Tools")
    lines.append("These are Python-based capabilities that give Jarvis 'hands' to interact with your system.")
    for name, meta in sorted(tools.items()):
        lines.append(f"- **{name}**: {meta['description']}")
    
    # 2. Playbooks grouped by category
    lines.append("\n## 🧠 Expert Playbooks (@id)")
    lines.append("These are cognitive guidelines that give Jarvis 'brains' for specific expert roles. Mention the `@id` in your prompt to activate them.")
    
    categories = {}
    for id, meta in playbooks.items():
        # Infer category from path
        # Example: modules/agent_skills/awesome-skills/playbooks/coding/python-expert/SKILL.md
        path = meta["path"]
        parts = path.split("/")
        
        category = "General"
        if "playbooks" in parts:
            p_idx = parts.index("playbooks")
            if len(parts) > p_idx + 2:
                # Part immediately after 'playbooks' is the category
                category = parts[p_idx + 1].replace("-", " ").title()
        
        if category not in categories:
            categories[category] = []
        categories[category].append((id, meta))

    # Table of Contents
    lines.append("\n### Table of Contents")
    for cat in sorted(categories.keys()):
        anchor = cat.lower().replace(" ", "-")
        lines.append(f"- [{cat}](#{anchor})")

    # Catalog Content
    for cat in sorted(categories.keys()):
        lines.append(f"\n### {cat}")
        for id, meta in sorted(categories[cat], key=lambda x: x[1]['title']):
            title = meta['title']
            summary = meta['summary'].strip().replace("\n", " ")
            # Ensure summary is 1-2 lines (truncate if needed)
            if len(summary) > 250:
                summary = summary[:247] + "..."
            
            lines.append(f"- **{title} (@{id})**: {summary}")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    
    print(f"✅ Catalog successfully generated at {output_path}")

if __name__ == "__main__":
    generate_catalog()
