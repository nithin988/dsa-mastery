# System design, redesigned: one story, twenty pages

## 1. What was wrong

The first system design course had **37 modules, 140+ lessons, and a reader that shows one small step at a time**. Feedback from using it:

- Opening a topic felt confusing: section after section, with no sense of where you were or why it mattered.
- Too many topics. Nobody can hold 37 modules in their head, and most of them were not what interviews or jobs need first.
- Too much data per topic and too few pictures and stories. Facts were correct and verified, but they did not build a feeling for how real systems grow.
- Interview questions were attached to lessons, not the other way round. Learners could not see "what will they ask me, and how do I answer?" on one screen.

The content itself (real experiments, recorded output, model answers) is good. The **shape** is wrong. So we keep the verified material as a reference library and put a new, small, story-driven course on top of it.

## 2. What strong courses and real interviews have in common (research notes)

Looked at: the public frameworks used by interview-prep sites (Hello Interview's delivery framework, RESHADED, and similar), and lists of the questions candidates report from Meta, Google, Amazon and Microsoft. These are third-party summaries, not official company data, and the course labels them that way.

- Every framework converges on the same flow: **requirements, numbers (only when they change the design), API and data, high-level design, deep dive, trade-offs and failures**. Senior-level signal is scored in the deep dive, so time must be left for it.
- The questions that recur across companies are a short list: **URL shortener, rate limiter, news feed, chat, video streaming, file storage (Drive/Dropbox), ride hailing and nearby search, search and autocomplete, notifications, booking and payments, and key-value store or cache**. Meta leans on feeds and messaging; Google on search, maps and storage-style problems; Amazon on e-commerce, rate limiting, and operational depth; Microsoft more on classic object design.
- Good teaching ties each building block to a **pain**: you add a cache because the database is melting, not because a list of components says so.

Sources used: [Hello Interview delivery framework](https://www.hellointerview.com/learn/courses/system-design/lesson/orientation/delivery), [framework comparison](https://handbook-hld.pages.dev/curriculum/interview-framework/frameworks-compared/), [FAANG question lists](https://prachub.com/resources/system-design-interview-questions-faang-2026), [Design Gurus overview](https://www.designgurus.io/blog/system-design-interviews-at-google-meta-amazon).

## 3. The redesign

**One course, one story, 20 pages.** System design becomes its own focused course. The Linux, Git, networking and troubleshooting modules stay as a separate "Engineering toolkit" and are no longer mixed into it.

### The story: ShopKart grows up

A two-person startup sells things online. Part 1 follows its growth. Each chapter opens with a real incident (what broke, when, who noticed) and the building block is the way out of it.

| # | Chapter | The pain that introduces it |
|---|---|---|
| 1 | Think in numbers | "How big will this get?" before any box is drawn |
| 2 | One server is not enough | Launch day: the only server falls over |
| 3 | Make it fast | Black Friday: the database melts under repeat questions |
| 4 | Where the data lives | A slow query, a lost order, two buyers for one item |
| 5 | When one database is not enough | Writes and size outgrow one machine |
| 6 | Do not make people wait | Signup sends email, resizes photos, takes 4 seconds |
| 7 | When things fail | A timeout that charges the card twice |
| 8 | Keep it up | A bad release at 3 p.m., a dead zone at 3 a.m. |
| 9 | Keep it safe | A guessable id shows someone else's invoice |

Part 2 is **ten whiteboard problems** with one template each: the question, what to ask, the numbers, a first design, the hard part, how it scales and fails, then "say it in two minutes". URL shortener, rate limiter, news feed, chat, video streaming, file storage, ride hailing, search and autocomplete, notifications, booking and payments.

Part 3 is **the interview playbook**: how to run the 45 minutes, how to explain trade-offs, and what the big companies are reported to emphasise.

### What a chapter page looks like

One page, read top to bottom, no stepper. Eight sections, the same every time, so the page is familiar after the first one:

1. **The story**: the incident, in plain words, with a three-panel picture (before, breaking, after).
2. **The idea**: one master picture and a few sentences.
3. **How it works**: three or four numbered steps, each with a small diagram.
4. **See it for real**: one or two experiments with real recorded output, read line by line.
5. **How it breaks**: the four or five failure modes that bite in production.
6. **How real companies do it**: short, sourced, hedged where uncertain.
7. **In the interview**: the questions people report, how to think, how to say it, likely follow-ups.
8. **Remember**: a recap card and quick checks. A "Go deeper" link opens the verified reference lessons.

### What happens to the old 37 modules

Nothing is deleted. The Engineering toolkit (S01 to S14) is unchanged. The deep system design modules (S15 to S27) become the **reference library**: each chapter links to the matching reference lessons for people who want every experiment, lab and edge case. The main path no longer asks anyone to read them in order.

### How it is built

- `build/sd2kit.py`: a small SVG illustration kit (people, servers, databases, caches, queues, clouds, gauges, three-panel story strips) so every picture shares one look and works in light and dark.
- `build/sd2.py`: the page renderer and the course landing page (a map, not a list).
- `build/sd2_content/*.py`: one small file per chapter. Experiments and model answers are **picked from the verified modules by reference**, so the recorded real output is reused and checked, not retyped.
- Output goes to `design/`, linked from the left rail as **System design**.

## 4. Plan and order of work

1. Write this plan. Done.
2. Build the kit, the renderer and the landing page.
3. **Pilot two pages**: Chapter 3 (caching) and Problem 1 (URL shortener), one of each kind, so the format can be judged before the rest is written.
4. After the format is approved: the remaining 7 chapters, 9 problems and the playbook, reusing the existing verified experiments and answers. Estimated at about one chapter or problem per hour, since the content already exists and only needs reshaping and illustrating.
5. Update the home page and README, and retire the 37-module list from the main navigation.

## 5. How we will know it is better

- A new learner can say, after opening any page, what problem it solves, in one sentence.
- No page needs more than one scroll direction; there is no "next section" button for small steps.
- Every page ends with the questions asked at top companies and a model answer, on the same screen.
- Page count in the main path drops from 37 to 20, and every page has at least three pictures.

## 6. Status

All 20 pages are written and built: 9 chapters, 10 problems and the playbook. Experiments and model answers are picked from the verified reference modules; real-company notes carry source links that the link check verifies. Figures are audited in a browser for clipped or overlapping text.
