import time
from core.registry import ServiceRegistry
from modules.commands import CommandProcessor

t0 = time.time()
print("Starting CP instantiation...")
try:
    cp = CommandProcessor(ServiceRegistry)
    print("Done in", time.time() - t0)
except Exception as e:
    print("Failed", e)
