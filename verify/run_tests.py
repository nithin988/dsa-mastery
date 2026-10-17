import sys, importlib, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import harness
for m in sys.argv[1:] or ["tests_1"]:
    importlib.import_module(m)
sys.exit(1 if harness.run_all() else 0)
