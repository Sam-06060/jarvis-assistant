import ast
import os
import sys

def get_tool_metadata(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        tree = ast.parse(content)
    except Exception as e:
        return [f"Error parsing {file_path}: {e}"]
    
    metadata = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            # Check if it looks like an AgentTool
            is_tool = False
            for base in node.bases:
                if isinstance(base, ast.Name) and base.id == "AgentTool":
                    is_tool = True
                elif isinstance(base, ast.Attribute) and base.attr == "AgentTool":
                    is_tool = True
            
            if is_tool:
                name_val = None
                desc_val = ""
                for body_node in node.body:
                    if isinstance(body_node, ast.Assign):
                        for target in body_node.targets:
                            if isinstance(target, ast.Name):
                                if target.id == "name":
                                    if hasattr(body_node.value, "value"): # Python 3.8+
                                        name_val = body_node.value.value
                                    elif hasattr(body_node.value, "s"): # Python < 3.8
                                        name_val = body_node.value.s
                                elif target.id == "description":
                                    if hasattr(body_node.value, "value"):
                                        desc_val = body_node.value.value
                                    elif hasattr(body_node.value, "s"):
                                        desc_val = body_node.value.s
                if name_val:
                    metadata.append({"class": node.name, "name": name_val, "description": desc_val, "file": file_path})
    return metadata

# Test with an existing tool
print(get_tool_metadata("modules/agent_tools/communication_tools.py"))
