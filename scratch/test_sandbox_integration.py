import json
import uuid
import threading
import subprocess
import time
import os

# ----------------------------------------------------
# 1. MOCKING THE ENVIRONMENT
# ----------------------------------------------------
class MockClient:
    def __init__(self):
        self.sent_data = []
    def sendall(self, data):
        self.sent_data.append(data.decode('utf-8'))

class MockSocketServer:
    def __init__(self):
        self.clients = [MockClient()]
        self.approval_events = {}
        self.approval_results = {}

class MockCommandProcessor:
    def __init__(self):
        self.app_context = {'socket_server': MockSocketServer()}

class MockTerminalExecutorTool:
    def __init__(self):
        self.cp = MockCommandProcessor()
    
    # Core logic copied from the actual Tool for standalone testing
    def run(self, inp: dict):
        command = inp.get('command', '')
        desc = inp.get('description', 'No desc')
        risk = inp.get('risk_level', 'Medium')
        
        if not command: return "Error: No command"
        
        req_id = str(uuid.uuid4())
        server = self.cp.app_context.get('socket_server')
        
        event = threading.Event()
        server.approval_events[req_id] = event
        
        payload_data = json.dumps({
            "type": "approval_request",
            "header": req_id,
            "data": json.dumps({"command": command, "description": desc, "risk": risk})
        }) + "\n"
        
        for c in server.clients:
            c.sendall(payload_data.encode('utf-8'))
            
        event.wait(timeout=2) # Shorter timeout for testing
        approved = server.approval_results.get(req_id, False)
        server.approval_events.pop(req_id, None)
        
        if not approved:
            return "CRITICAL ERROR: Execution EXPLICITLY REJECTED"
            
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=2)
            output = result.stdout
            if result.stderr: output += f"\nErrors:\n{result.stderr}"
            if len(output) > 4000:
                output = output[:2000] + "\n...TRUNCATED...\n" + output[-2000:]
            if not output.strip(): return "Command executed successfully"
            return output
        except Exception as e:
            return f"Execution Error: {str(e)}"

# ----------------------------------------------------
# 2. RUNNING THE TEST SUITE
# ----------------------------------------------------
def run_tests():
    print("🚀 [Google QA] Initializing Unit Test Suite...")
    tool = MockTerminalExecutorTool()
    server = tool.cp.app_context['socket_server']
    
    # TEST 1: Payload Broadcast Routing
    print("\n[Test 1] Socket Broadcast Encoding")
    inp = {'command': 'echo "Hello"', 'description': 'Test', 'risk_level': 'Low'}
    
    # Simulate async Approval UI Click via thread
    def simulate_ui_click(approve=True):
        time.sleep(0.5)
        req_id = list(server.approval_events.keys())[0] if server.approval_events else None
        if req_id:
            server.approval_results[req_id] = approve
            server.approval_events[req_id].set()

    threading.Thread(target=simulate_ui_click, args=(True,)).start()
    res1 = tool.run(inp)
    assert "Hello" in res1, "Test 1 Failed: Execution didn't return stdout"
    
    sent_payload = server.clients[0].sent_data[-1]
    parsed_socket = json.loads(sent_payload)
    assert parsed_socket['type'] == 'approval_request', "Test 1 Failed: Bad type"
    
    parsed_inner = json.loads(parsed_socket['data'])
    assert parsed_inner['command'] == 'echo "Hello"', "Test 1 Failed: Bad inner nested JSON"
    print("✅ PASS: Correct JSON Packet transmitted to UI")

    # TEST 2: Active Rejection Circuit Breaker
    print("\n[Test 2] Active UX Rejection Branch")
    threading.Thread(target=simulate_ui_click, args=(False,)).start()
    res2 = tool.run({'command': 'rm -rf /', 'description': 'Nuke system', 'risk_level': 'Critical'})
    assert "CRITICAL ERROR: Execution EXPLICITLY REJECTED" in res2, "Test 2 Failed: Did not halt on reject"
    print("✅ PASS: Safety Halt Protocol successfully overrides command injection.")

    # TEST 3: Context Truncation Algorithm
    print("\n[Test 3] Context Limit Explosion Threat (Large Output)")
    threading.Thread(target=simulate_ui_click, args=(True,)).start()
    # Generate 5,000 character output
    res3 = tool.run({'command': 'python3 -c "print(\'A\' * 5000)"', 'description': 'Big payload', 'risk_level': 'Low'})
    assert len(res3) < 4100, f"Test 3 Failed: Output length is {len(res3)} which breaks LLM"
    assert "TRUNCATED" in res3, "Test 3 Failed: Truncation marker missing"
    print("✅ PASS: Token Limits successfully protected via slicing.")
    
    print("\n🎯 ALL TESTS PASSED.")

if __name__ == '__main__':
    run_tests()
