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
| 06 | [Sorting and Intervals](topics/06_sorting_intervals.html) | done |
| 07 | [Recursion and Backtracking](topics/07_recursion_backtracking.html) | done |
| 08 | [Bit Manipulation and Math](topics/08_bit_math.html) | done |
| 09 | [Binary Trees and BSTs](topics/09_trees.html) | done |
| 10 | [Heaps and Priority Queues](topics/10_heap_priority_queue.html) | done |
| 11 | [Tries](topics/11_trie.html) | done |
| 12 | [Graph Traversal](topics/12_graphs_traversal.html) | done |
| 13 | [Advanced Graphs](topics/13_graphs_advanced.html) | done |
| 14 | [Greedy Algorithms](topics/14_greedy.html) | done |
| 15 | [Dynamic Programming I](topics/15_dp_1d_2d.html) | done |
| 16 | [Dynamic Programming II](topics/16_dp_advanced.html) | done |
| 17 | [Advanced Data Structures](topics/17_advanced_ds.html) | done |
| 18 | [Design Problems](topics/18_design_problems.html) | done |
| 19 | [Interview Playbook](topics/19_interview_playbook.html) | done |

## For contributors

Pages are generated from Python data, so every topic shares the same look and behaviour.

```bash
python build/build.py      # writes index.html and topics/*.html
```

- `build/lib.py`: page renderer; `build/style.css`: design; `build/engine.js`: page behaviour and the animated stepper; `build/sims.js`: the animations
- `build/arrays.py`, `build/foundations.py`, `build/strings.py`, `build/linked_list.py`, `build/stack_queue.py`, `build/sorting_intervals.py`, `build/recursion_backtracking.py`, `build/bit_math.py`, `build/trees.py`, `build/heaps.py`, `build/graphs.py`, `build/graphs_advanced.py`, `build/tries.py`, `build/greedy.py`, `build/dp1.py`: topic content (copy one as the starting point for a new topic)
- `build/build.py`: the topic catalogue and landing page

## Study planner (`plan.html`)

A page that builds a day-by-day study plan from the learner's time and the topics they pick, with a chat coach to adjust it.

- **The schedule is computed by code** (`build/planner_core.js`), not by an AI: hours per day, rest day, level, depth, spaced reviews, weekly checkpoints and a final mock. If the time is not enough it trims in a fixed order (depth, secondary patterns) and says what it cut, or says how many more weeks are needed.
- **The coach** (`build/planner.js`) works in two modes. With no key it understands simple requests ("6 weeks, 2 hours a day, only graphs and DP"). With a **Gemini API key that each learner pastes in themselves** it holds a normal conversation and changes the plan settings; the app recomputes the plan and shows exact dates and hours.
- **The key is never in the repo or the site.** It is stored only in the learner's browser (`localStorage`, or in memory if they untick "Remember") and is sent only to Google. Never commit a key; the site is public.
- Progress ticked in the plan is also written to the same progress store the topic pages use, so the landing page and topic menu stay in sync.

Test the scheduler with `python verify/check_planner.py` (also part of `check_all.py`).

## Changing the look of every page

Every topic page is generated from the same three shared files, so one edit restyles all of them:

- `build/style.css`: colours, spacing, cards, tables, animation styling
- `build/engine.js`: page behaviour (theme toggle, progress ticks, download button, the animated stepper)
- `build/lib.py`: the page structure (top bar, hero, sidebar, pattern cards) and the shared icon set
- `build/home.js` and `build/build.py`: the landing page (learning path, progress summary, search and filters)

The tokens and components follow the Kimaru Platform design system; see [docs/DESIGN_SYSTEM.md](docs/DESIGN_SYSTEM.md).

After editing any of them run `python build/build.py` and commit the regenerated `index.html` and `topics/*.html`. Each page embeds the CSS and JS so it still works as a single downloaded file.

## Verification

`python verify/check_all.py` runs the offline checks (see [verify/README.md](verify/README.md)): every Python and Java snippet is syntax-checked, Java is type-checked, 73 Python test groups and 30 Java classes run the published code against known answers, and `verify/link_check.js` validates every LeetCode link (number, difficulty, premium status) from inside a real LeetCode page.
