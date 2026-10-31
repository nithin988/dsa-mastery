# Mastery: DSA and Systems

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

## Course 2: Systems Mastery (in progress)

Linux, Git, troubleshooting, system design and interviews, kept separate from DSA (own landing page `systems.html`, own progress store, left navigation rail on every page). The plan and content policy are in [docs/COURSE2_PLAN.md](docs/COURSE2_PLAN.md).

| Module | Page | Labs |
|--------|------|------|
| S02 Linux shell | [systems/S02_linux_shell.html](systems/S02_linux_shell.html) | find-config, fix-permissions, top-ips |
| S03 Text tools and scripting | [systems/S03_text_processing_scripting.html](systems/S03_text_scripting.html) | log-forensics, backup-script, bulk-rename |
| S04 Linux internals | [systems/S04_linux_internals.html](systems/S04_linux_internals.html) | find-the-hog, links-and-inodes, disk-detective |
| S05 Git fundamentals | [systems/S05_git_fundamentals.html](systems/S05_git_fundamentals.html) | first-repo, merge-conflict, undo-mistakes |
| S06 Git in teams and recovery | [systems/S06_git_teams_recovery.html](systems/S06_git_teams_recovery.html) | recover-reflog, squash-branch, find-the-bug |

- **Every command output on these pages is real.** `python verify/sys_record.py <module-id>` runs the page's commands on real Linux (WSL Debian) as an unprivileged user and stores the output in `build/sys_outputs.json`; the build fails if a runnable command has no fresh recorded output. Output that cannot be reproduced (systemd, interactive editors) is labelled illustrative.
- **Every lab is verified:** `python verify/sys_labs.py` runs each setup script, confirms its check script fails, runs the reference solution, and confirms the check passes.
- `python verify/sys_links.py` checks that every source link still responds.
- Learners run labs either with Docker (`systems/labs/linux/Dockerfile`) or by downloading a lab script and running it with `bash`; lab scripts only touch `~/sys-lab` and refuse to touch folders they did not create.
- Hashes and dates in Git examples come from a fixed clock; learners will see different ones, with identical behaviour.
- Content: `build/sys_*.py` (one per module), `build/syscatalog.py` (catalogue), `build/lib_sys.py` (renderer), `build/sims_sys.js` (animations), `build/sysviz.py` (diagrams).

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
