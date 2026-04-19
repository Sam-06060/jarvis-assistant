import subprocess
import time

try:
    print("Starting sleep process...")
    # This simulates a background process like 'npm start'
    result = subprocess.run("sleep 5", shell=True, capture_output=True, text=True, timeout=2)
    print("Finished:", result.stdout)
except subprocess.TimeoutExpired:
    print("Timeout triggered!")
