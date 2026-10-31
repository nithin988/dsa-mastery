# Verification tools

These scripts check that what is published is correct. Run them after editing any content in `build/`.

```bash
python verify/check_all.py
```

| Check | Script | What it proves |
|-------|--------|----------------|
| Syntax | `check_syntax.py` | Every Python snippet parses; every Java snippet parses as a class body or method body |
| Dead code | `check_deadcode.py` | No snippet has unreachable code after a top-level `return` (a sign two algorithms were pasted together) |
| Java types | `check_java_types.py` | javac type-checks every Java snippet (errors other than "cannot find symbol", which excerpts are expected to produce) |
| Python behaviour | `run_tests.py tests_1 tests_2 tests_3 tests_4` | The published Python code returns the right answers on known inputs and on randomised inputs compared with brute force |
| Java behaviour | `java_tests.py` | The self-contained Java classes and methods run and return the right answers |
| Planner | `check_planner.py` | The study-plan scheduler respects daily capacity and rest days, places reviews after learning, trims honestly when time is short, and parses assistant replies safely |
| Systems output | `sys_record.py`, build step | Every runnable command on a Systems page has fresh output recorded from real Linux |
| Systems labs | `sys_labs.py` | Each lab's check fails after setup and passes after the reference solution |
| Systems links | `sys_links.py` | Every source link on Systems pages responds |
| LeetCode links | `link_check.js` | Every problem slug exists, the number and difficulty match, and the problem is not premium-only |

`link_check.js` must run inside a real `leetcode.com` page (LeetCode blocks scripts): open any problem page,
paste the contents of the file into the browser console and read the result. The slug list it checks is in
`compact_slugs.txt` (regenerate it with `python verify/make_slug_list.py`).

Not covered: the animations are checked by stepping each one to its end state in a browser, and the prose
(intuition, traps, complexity claims) is reviewed by reading, not by tests.
