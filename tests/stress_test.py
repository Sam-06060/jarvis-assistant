
import sys
import os
import time
import random
import unittest.mock as mock

# Ensure modules can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock Dependencies to prevent side effects
mock_speech = mock.Mock()
mock_speech.speak = mock.Mock()
mock_brain = mock.Mock()
mock_visuals = mock.Mock()
mock_system = mock.Mock()
# Explicitly mock check_network to return True so we don't hit the "offline" error immediately on some commands
mock_system.check_network = mock.Mock(return_value=True)

# Import COMMANDS using strict mocks for the rest
with mock.patch.dict('sys.modules', {
    'modules.cursor_control': mock.Mock(),
    'modules.mimic': mock.Mock(),
    'modules.dead_drop': mock.Mock(),
    'modules.content_assassin': mock.Mock(),
    'modules.ghost_hand': mock.Mock(),
    'pywhatkit': mock.Mock(), # Disable YouTube for test
    'wikipedia': mock.Mock()
}):
    from modules.commands import CommandProcessor

def run_stress_test(duration_seconds=60):
    print(f"🔥 STARTING CHAOS MONKEY STRESS TEST ({duration_seconds}s)...")
    
    # Initialize Processor with Mocks
    processor = CommandProcessor(
        speech_engine=mock_speech,
        ai_brain=mock_brain,
        file_manager=mock.Mock(),
        system_info=mock_system
    )
    
    # Configure Mocks to return valid types
    mock_speech.listen_command.return_value = "mock response"
    
    # Configure Ghost Hand Mock
    if processor.ghost:
        processor.ghost.get_selected_text.return_value = "Simulated text content for reading"
        processor.ghost.get_window_content.return_value = "Window content"
        processor.ghost.click_button.return_value = "Clicked"
        
    # Configure Contacts Mock
    if processor.contacts:
        processor.contacts.get_email.return_value = "test@example.com"
        processor.contacts.add_email_contact.return_value = "Contact added"
        processor.contacts.call_contact.return_value = "Calling..."
        processor.contacts.message_contact.return_value = "Message sent"
        processor.contacts.search_contact.return_value = "Found contact"

    # Configure Brain
    mock_brain.ask.return_value = "This is a simulated AI response."
    
    # Configure Calculator
    if processor.calculator:
        processor.calculator.parse_and_calculate.return_value = "The answer is 42"
        processor.calculator.calculate_tip.return_value = "Tip: $5"

    # Inject Mock Visuals (because they are instantiated inside __init__)
    processor.visuals = mock_visuals

    test_commands = [
        "what time is it",
        "play music",
        "calculate 5 plus 5",
        "search google for entropy",
        "system scan",
        "volume up",
        "brightness 50",
        "open calculator",
        "tell me a joke",
        "weather in Tokyo",
        "send email to test@test.com saying hello",
        "unknown command xyz",
        "", # Empty command
        "   ", # Whitespace
        "play " * 100, # Spam
        "shutdown", # Verify it doesn't actually kill the test script (mocked)
        "toggle vad",
        "analyze system",
        "news tech",
        "read this",
        "click send"
    ]
    
    start_time = time.time()
    commands_processed = 0
    errors = 0
    
    while (time.time() - start_time) < duration_seconds:
        cmd = random.choice(test_commands)
        try:
            # print(f"⚡️ Executing: {cmd[:20]}...")
            processor.process(cmd)
            commands_processed += 1
        except Exception as e:
            print(f"❌ CRASH DETECTED on '{cmd}': {e}")
            errors += 1
            
        # Tiny sleep to prevent 100% CPU lock, but still fast (100ms)
        time.sleep(0.01)
        
    print("-" * 40)
    print(f"🏁 TEST COMPLETE")
    print(f"⏱️ Duration: {duration_seconds}s")
    print(f"✅ Commands Processed: {commands_processed}")
    print(f"❌ Errors/Crashes: {errors}")
    print("-" * 40)
    
    if errors == 0:
        print("🎉 STATUS: PASSED (STABLE)")
        exit(0)
    else:
        print("⚠️ STATUS: UNSTABLE")
        exit(1)

if __name__ == "__main__":
    # Run for roughly 45 seconds to match the user's "10:33" deadline logic
    run_stress_test(45)
