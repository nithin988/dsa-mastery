# DSA Mastery

Pattern-based Data Structures and Algorithms revision sheets for interview preparation. One self-contained HTML page per topic, each with intuition, a step-through animation, code in Java and Python, complexity, common traps and a ladder of LeetCode problems.

**Read online:** https://nithin988.github.io/dsa-mastery/

Every page has a **Download** button (and the index has one per topic), so friends can save the HTML and read it offline.

## Topics

| # | Topic | Status |
|---|-------|--------|
| 01 | [Complexity and Problem-Solving Method](topics/01_complexity_foundations.html) | done |
| 02 | [Arrays, Hashing and Searching](topics/02_arrays.html) | done |
| 03 | [Strings](topics/03_strings.html) | done |
| 04 | [Linked Lists](topics/04_linked_list.html) | done |
| 05 | [Stacks, Queues and Deques](topics/05_stack_queue.html) | done |
| 06-19 | see [ROADMAP.md](ROADMAP.md) | planned |

## For contributors

Pages are generated from Python data, so every topic shares the same look and behaviour.

```bash
python build/build.py      # writes index.html and topics/*.html
```

- `build/lib.py`: page renderer; `build/style.css`: design; `build/engine.js`: page behaviour and the animated stepper; `build/sims.js`: the animations
- `build/arrays.py`, `build/foundations.py`, `build/strings.py`, `build/linked_list.py`, `build/stack_queue.py`: topic content (copy one as the starting point for a new topic)
- `build/build.py`: the topic catalogue and landing page
