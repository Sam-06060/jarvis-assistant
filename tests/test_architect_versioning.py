import os
import shutil
import unittest
from unittest.mock import MagicMock
import sys
import datetime

# Add modules path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.skills.architect_skill import ArchitectSkill

class TestArchitectVersioning(unittest.TestCase):
    def setUp(self):
        # Setup mock app context
        self.mock_app = MagicMock()
        self.mock_app.get.return_value = MagicMock() # For brain, speech, etc.
        
        self.skill = ArchitectSkill(self.mock_app)
        
        # Setup dummy builds dir
        self.builds_dir = os.path.expanduser("~/Desktop/Jarvis_Builds_Test")
        if os.path.exists(self.builds_dir):
            shutil.rmtree(self.builds_dir)
        os.makedirs(self.builds_dir)
        
        # Override _generate_project_name to be deterministic
        self.skill._generate_project_name = MagicMock(return_value="TestProject")
        
        # Monkey patch os.path.expanduser to use our test dir
        # Actually easier to just mock where _build_project looks for builds? 
        # _build_project uses hardcoded ~/Desktop/Jarvis_Builds if not iteration.
        # But for iteration, it uses self.last_project_path.
        
    def tearDown(self):
        if os.path.exists(self.builds_dir):
            shutil.rmtree(self.builds_dir)

    def test_atomic_versioning(self):
        print("\n🧪 Testing Atomic Folder Versioning...")
        
        # 1. Create Initial Project (v1) manually
        v1_path = os.path.join(self.builds_dir, "TestProject_v1")
        os.makedirs(v1_path)
        
        with open(os.path.join(v1_path, "index.html"), "w") as f:
            f.write("<h1>Hello World v1</h1>")
        with open(os.path.join(v1_path, "style.css"), "w") as f:
            f.write("body { color: black; }")
            
        # Set context
        self.skill.last_project_path = v1_path
        
        # 2. Simulate Update (Update style.css to blue)
        # The LLM response should return ONLY the updated file.
        llm_response = """
<file name="style.css">
body { color: blue; }
</file>
"""
        print(f"   ℹ️ Current Path: {v1_path}")
        print("   🚀 Triggering Update...")
        
        # Call _build_project
        self.skill._build_project(llm_response, "Make it blue", source="test", is_iteration=True)
        
        # 3. Verify v2 Created
        v2_path = os.path.join(self.builds_dir, "TestProject_v2")
        self.assertTrue(os.path.exists(v2_path), "v2 folder not created!")
        
        # 4. Verify Content (Atomic Snapshot)
        # index.html should be COPIED from v1 (since LLM didn't return it)
        with open(os.path.join(v2_path, "index.html"), "r") as f:
            content = f.read()
            self.assertIn("Hello World v1", content, "index.html was not copied from v1!")
            
        # style.css should be UPDATED
        with open(os.path.join(v2_path, "style.css"), "r") as f:
            content = f.read()
            self.assertIn("color: blue", content, "style.css was not updated!")
            
        # 5. Verify Context Update
        self.assertEqual(self.skill.last_project_path, v2_path, "Context path not updated to v2!")
        
        print("✅ PASS: Atomic Versioning verified.")

if __name__ == '__main__':
    unittest.main()
