"""Run every offline check. Exit code is non-zero if anything fails."""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STEPS = [
    ("syntax (Python + Java)", ["check_syntax.py"]),
    ("dead code", ["check_deadcode.py"]),
    ("Java types", ["check_java_types.py"]),
    ("Python behaviour", ["run_tests.py", "tests_1", "tests_2", "tests_3"]),
    ("Java behaviour", ["java_tests.py"]),
]


def main():
    failed = []
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    for name, cmd in STEPS:
        print("=" * 8, name)
        r = subprocess.run([sys.executable] + cmd, cwd=HERE, capture_output=True, text=True, env=env)
        out = (r.stdout + r.stderr).strip()
        print(out[-1500:])
        bad = r.returncode != 0
        # scripts that only print findings: treat any finding line as a failure
        if name == "dead code" and ("html P" in out):
            bad = True
        if name == "syntax (Python + Java)" and ("failures: 0" not in out or "FAIL" in out):
            bad = bad or "failures: 0 (parsed" not in out
        if name == "Java types" and "real type errors in 0 snippets" not in out:
            bad = True
        if bad:
            failed.append(name)
    print()
    print("ALL CHECKS PASSED" if not failed else "FAILED: " + ", ".join(failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
