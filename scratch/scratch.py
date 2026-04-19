import json
import uuid

# Simulate the tool execution context bounds
command_output = "A" * 500_000 # 500kb string
print("Length of output:", len(command_output))

# Let's write a truncation logic
if len(command_output) > 4000:
    command_output = command_output[:2000] + "\n...[OUTPUT TRUNCATED]...\n" + command_output[-2000:]
    
print("New Length:", len(command_output))
