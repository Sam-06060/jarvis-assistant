import pytest
import sys
import os
import json
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import config
from jarvis import JarvisApp
from modules.agent_core import AgentCore, AgentMaxIterationsError

@pytest.fixture
def mock_registry():
    registry = MagicMock()
    registry.get.return_value = MagicMock()
    return registry

@pytest.fixture
def app():
    with patch('jarvis.logger'), patch('jarvis.play_sound'):
        from core.registry import ServiceRegistry
        mock_speech = MagicMock()
        ServiceRegistry.register("speech", mock_speech)
        hud_queue = MagicMock()
        return JarvisApp(hud_queue)

def test_safety_isolation():
    """Assert no agent_core in sys.modules when agentic mode is OFF."""
    if "modules.agent_core" in sys.modules:
        del sys.modules["modules.agent_core"]
    
    config.ENABLE_AGENTIC_MODE = False
    hud_queue = MagicMock()
    app = JarvisApp(hud_queue)
    
    assert app.agent is None
    assert "modules.agent_core" not in sys.modules

def test_toggle_signal_activation(app):
    """Mock __UPDATE_CONFIG__ IPC message and verify activation."""
    with patch.object(app, '_update_atomic_config'), \
         patch('modules.agent_core.AgentCore') as MockAgent:
        
        command = '__UPDATE_CONFIG__:{"key": "ENABLE_AGENTIC_MODE", "value": true}'
        app._process_internal_config_update(command)
        
        assert config.ENABLE_AGENTIC_MODE is True
        assert app.agent is not None
        
        from core.registry import ServiceRegistry
        speech = ServiceRegistry.get("speech")
        speech.speak.assert_any_call("Switched to agentic mode, sir")

def test_react_loop_iteration_cap():
    """Verify AgentMaxIterationsError after cap reached."""
    mock_reg = MagicMock()
    mock_brain = MagicMock()
    # Mock LLM to always return a Thought/Action, never Final Answer
    mock_brain.ask.return_value = "Thought: Still thinking...\nAction: web_search\nAction Input: {\"query\": \"test\"}"
    mock_reg.get.return_value = mock_brain
    
    agent_cfg = config.AgentConfig(enabled=True, max_iterations=3)
    agent = AgentCore(mock_reg, agent_cfg)
    
    result = agent.run("Perform a task that never ends")
    assert "hit my planning limit" in result
    assert mock_brain.ask.call_count == 3

def test_tool_confirmation_protocol():
    """Verify Tier 2 tools trigger confirmation."""
    mock_cp = MagicMock()
    mock_speech = MagicMock()
    mock_cp.registry.get.return_value = mock_speech
    
    # Mock a Tier 2 tool
    class GatedTool:
        name = "gated_action"
        tier = 2
        def run(self, params): return "Done"
    
    mock_cp.tools = {"gated_action": GatedTool()}
    
    # Test Denied
    mock_speech.listen_confirmation.return_value = False
    from modules.commands import CommandProcessor
    # We need to use the real execute_tool logic or mock it accurately
    # For simplicity, we'll patch the CommandProcessor's execute_tool logic if it was a standalone test
    # but here we just want to verify the logic flow in CommandProcessor.execute_tool
    
    with patch('modules.commands.logger'):
        # Using real method on mock object
        res = CommandProcessor.execute_tool(mock_cp, "gated_action", {})
        assert res == "Action cancelled by user."
        mock_speech.listen_confirmation.assert_called()

if __name__ == "__main__":
    pytest.main([__file__])
