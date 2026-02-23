import unittest
from unittest.mock import MagicMock
import sys
import os

# Add modules path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.skills.architect_skill import ArchitectSkill

class TestArchitectMissingFiles(unittest.TestCase):
    def setUp(self):
        self.mock_app = MagicMock()
        self.mock_brain = MagicMock()
        self.mock_app.get.return_value = self.mock_brain
        
        self.skill = ArchitectSkill(self.mock_app)
        
    def test_ensure_critical_files_triggers_generation(self):
        print("\n🧪 Testing Missing File Guard...")
        
        # Scenario: LLM returns CSS and JS, but NO HTML
        matches = [
            ("style.css", "body { color: red; }"),
            ("script.js", "console.log('hello');")
        ]
        
        # Mock the Brain's response to the emergency prompt
        self.mock_brain.generate_code.return_value = """
<file name="index.html">
<html><body><h1>Fixed!</h1></body></html>
</file>
"""
        
        print("   ⚠️ Simulating missing index.html...")
        
        # Call the method
        updated_matches = self.skill._ensure_critical_files(matches, "Create a website")
        
        # Assertions
        # 1. Brain should have been called to generate index.html
        self.mock_brain.generate_code.assert_called_once()
        print("   ✅ Brain was called for emergency generation.")
        
        # 2. Matches should now include index.html
        filenames = [m[0] for m in updated_matches]
        self.assertIn("index.html", filenames)
        print("   ✅ index.html was added to the file list.")
        
        # 3. Content verification
        html_content = next((m[1] for m in updated_matches if m[0] == "index.html"), "")
        self.assertIn("Fixed!", html_content)

    def test_no_trigger_if_present(self):
        print("\n🧪 Testing Normal Case (HTML Present)...")
        matches = [
            ("style.css", "body {}"),
            ("index.html", "<html></html>")
        ]
        
        self.skill._ensure_critical_files(matches, "cmd")
        self.mock_brain.generate_code.assert_not_called()
        print("   ✅ Brain was NOT called (correctly).")

    def test_fallback_on_brain_failure(self):
        print("\n🧪 Testing Fallback on Brain Failure...")
        matches = [("style.css", "body{}")]
        
        # Simulate Brain Crash
        self.mock_brain.generate_code.side_effect = Exception("Timeout")
        
        updated = self.skill._ensure_critical_files(matches, "cmd")
        
        # Check if index.html was added anyway
        filenames = [m[0] for m in updated]
        self.assertIn("index.html", filenames)
        
        # Check content is the fallback
        html = next(m[1] for m in updated if m[0] == "index.html")
        self.assertIn("Emergency Mode", html)
        print("   ✅ Fallback HTML deployed successfully.")

if __name__ == '__main__':
    unittest.main()
