import subprocess
import time
import os

try:
    print("Spawning a subshell with a background sleep...")
    # 'sleep 100' runs in the shell.
    # The timeout hits at 2 seconds.
    result = subprocess.run("sleep 60", shell=True, capture_output=True, text=True, timeout=2)
except subprocess.TimeoutExpired:
    print("Timeout triggered!")

# Check if 'sleep 60' is still running
time.sleep(1)
ps_res = subprocess.run("ps aux | grep 'sleep 60' | grep -v 'grep'", shell=True, capture_output=True, text=True)
print("Processes still running:\n", ps_res.stdout)
