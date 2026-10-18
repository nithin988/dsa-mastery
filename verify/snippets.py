"""Shared helper: yield every (topic, pattern title, snippet label, java, python) from the build content."""
import importlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "build"))

MODULES = ["arrays", "foundations", "strings", "linked_list", "stack_queue", "sorting_intervals",
           "recursion_backtracking", "bit_math", "trees", "heaps", "tries", "graphs", "graphs_advanced",
           "greedy", "dp1", "dp2", "adv_ds", "design"]


def topics():
    for m in MODULES:
        yield importlib.import_module(m).TOPIC


def snippets():
    for t in topics():
        for pi, p in enumerate(t["patterns"], 1):
            for ci, (label, java, py) in enumerate(p["code"], 1):
                yield {"topic": t["id"], "file": t["file"], "pattern": pi, "title": p["title"],
                       "idx": ci, "label": label, "java": java, "py": py}
