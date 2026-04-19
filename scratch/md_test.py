import re
import os

def parse_skill_md(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Extract title (First H1)
    title_match = re.search(r"^#\s+(.*)", content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else os.path.basename(os.path.dirname(file_path))
    
    # Extract summary (First non-empty paragraph after H1)
    # We'll just take the first 200 chars for the index
    summary = content.split('\n\n')[1] if '\n\n' in content else ""
    summary = re.sub(r'[#\*`>]', '', summary).strip()[:200]
    
    return {"title": title, "summary": summary, "path": file_path}

# Mock a skill file
os.makedirs("scratch/test_skill", exist_ok=True)
with open("scratch/test_skill/SKILL.md", "w") as f:
    f.write("# Brainstorming\n\nThis skill helps Jarvis plan complex SaaS products and brainstorm features.")

print(parse_skill_md("scratch/test_skill/SKILL.md"))
