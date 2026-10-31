"""Verify every Systems Mastery lab: the check must FAIL right after setup and PASS after the solution.

  python verify/sys_labs.py
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "build"))
sys.path.insert(0, HERE)
import sys_runner  # noqa: E402
from sys_record import live_modules, LABS  # noqa: E402


def main():
    if sys_runner.backend() is None:
        print("SKIPPED: no Linux backend available (WSL Debian or Docker needed to verify labs).")
        return 0
    failed = 0
    total = 0
    for m in live_modules():
        for lab in m.get("labs", []):
            total += 1
            name, kind = lab["script"], lab["kind"]
            files = {
                "setup.sh": sys_runner.read(os.path.join(LABS, kind, name + ".sh")),
                "solution.sh": sys_runner.read(os.path.join(LABS, kind, name + ".solution.sh")),
            }
            if lab.get("depends"):
                for dep in lab["depends"]:
                    files[dep] = sys_runner.read(os.path.join(LABS, kind, dep))
            driver = (
                "export LC_ALL=C TZ=UTC\nD=\"$(dirname \"$0\")\"\n"
                + "".join(f'echo "== pre: {p}"\n' for p in lab.get("pre", []))
                + 'bash "$D/setup.sh" > /dev/null 2>&1; echo "SETUP_RC=$?"\n'
                f'bash "$HOME/sys-lab/check-{name}.sh" > /dev/null 2>&1; echo "BEFORE_RC=$?"\n'
                'bash "$D/solution.sh" > /dev/null 2>&1; echo "SOLUTION_RC=$?"\n'
                f'bash "$HOME/sys-lab/check-{name}.sh" 2>&1; echo "AFTER_RC=$?"\n'
                + "".join(f"{c}\n" for c in lab.get("cleanup", []))
            )
            files["driver.sh"] = driver
            rc, out = sys_runner.run_bash(files, "driver.sh", timeout=300)
            g = lambda k: (re.search(k + r"=(\d+)", out) or [None, "?"])[1]
            ok = g("SETUP_RC") == "0" and g("BEFORE_RC") not in ("0", "?") and g("AFTER_RC") == "0"
            print(f"{'OK  ' if ok else 'FAIL'} {m['id']}/{name}: setup={g('SETUP_RC')} check-before={g('BEFORE_RC')} (must be non-zero) check-after={g('AFTER_RC')} (must be 0)")
            if not ok:
                failed += 1
                print(out[-600:])
    print(f"lab checks: {total - failed}/{total} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
