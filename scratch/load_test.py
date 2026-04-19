import importlib.util
import os
import sys

def load_tool_from_path(file_path, class_name):
    # This is a test to see if we can load a class from an arbitrary path
    module_name = os.path.basename(file_path).replace(".py", "")
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    
    # We might need to handle dependencies by adding the directory to sys.path
    # but for a simple drop zone, we assume the files are self-contained or use project modules.
    
    # Mocking AgentTool so it doesn't fail on inheritance check
    class AgentTool: pass
    
    try:
        spec.loader.exec_module(module)
        cls = getattr(module, class_name)
        print(f"Successfully loaded {cls} from {file_path}")
        return cls
    except Exception as e:
        print(f"Failed to load: {e}")
        return None

# Adding root to sys.path so imports like 'from .base import AgentTool' might work 
# (though that specific relative import would fail in dynamically loaded modules)
sys.path.append(os.getcwd())

# Test with a tool (we'll need to mock the environment for a real test)
load_tool_from_path("modules/agent_tools/system_tools.py", "ScreenshotTool")
