import time
import importlib

skills = [
    ".system_skill", ".time_skill", ".app_control_skill", ".weather_skill",
    ".music_skill", ".news_skill", ".calculator_skill", ".communication_skill",
    ".internet_skill", ".file_skill", ".focus_skill", ".research_skill",
    ".automation_skill", ".shortcuts_skill", ".interaction_skill", ".architect_skill",
    ".reminder_skill", ".analytics_skill", ".translator_skill", ".alarm_skill"
]
with open("times.txt", "w") as f:
    for skill in skills:
        t0 = time.time()
        try:
            importlib.import_module(f"modules.skills{skill}")
        except Exception as e:
            f.write(f"Error importing {skill}: {e}\n")
        total = time.time() - t0
        f.write(f"Imported {skill:<25} in {total:.4f}s\n")
        f.flush()
