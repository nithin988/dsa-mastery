"""Run the planner scheduler tests (node) against the real topic data."""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "build"))
import build  # noqa: E402

with tempfile.TemporaryDirectory() as d:
    path = os.path.join(d, "planner-data.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(build.planner_data(), f)
    r = subprocess.run(["node", os.path.join(HERE, "test_planner.js"), path], capture_output=True, text=True, encoding="utf-8")
    print((r.stdout + r.stderr).strip())
    sys.exit(r.returncode)
