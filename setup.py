#!/usr/bin/env python3
import os
import shutil
import time

def setup_jarvis():
    print("\n🔮 Jarvis Configuration Wizard 🔮")
    print("==================================\n")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    env_example = os.path.join(base_dir, ".env.example")
    env_file = os.path.join(base_dir, ".env")
    data_dir = os.path.join(base_dir, "data")

    # 1. Create Data Directory
    if not os.path.exists(data_dir):
        print(f"📂 Creating data directory at {data_dir}...")
        os.makedirs(data_dir)
    else:
        print(f"✅ Data directory exists.")

    # 2. Handle .env file
    if not os.path.exists(env_file):
        if os.path.exists(env_example):
            print("📝 Creating .env from template...")
            shutil.copy(env_example, env_file)
        else:
            print("❌ Error: .env.example not found! Please pull the latest code.")
            return

    # 3. Interactive Configuration
    print("\n🔧 Let's configure your environment variables.")
    print("   Press ENTER to keep existing values or type new ones.\n")

    # Load current values manually to avoid dotenv dependency here if possible, 
    # but we can just read the file line by line for simplicity and robustness.
    current_config = {}
    with open(env_file, 'r') as f:
        lines = f.readlines()
        
    new_lines = []
    for line in lines:
        if "=" in line and not line.strip().startswith("#"):
            key, val = line.strip().split("=", 1)
            val = val.strip()
            
            prompt = f"👉 {key} [{val}]: "
            new_val = input(prompt).strip()
            
            if new_val:
                new_lines.append(f"{key}={new_val}\n")
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)

    # Write back
    with open(env_file, 'w') as f:
        f.writelines(new_lines)

    print("\n✅ Configuration saved to .env")
    print("🚀 You are ready to launch Jarvis!")
    print("   Run: python3 jarvis.py\n")

if __name__ == "__main__":
    setup_jarvis()
