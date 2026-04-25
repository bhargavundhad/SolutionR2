"""
Plot reward/quality comparisons from evaluation outputs.
"""

import argparse
import csv
import os
from collections import defaultdict
from statistics import mean

import matplotlib.pyplot as plt


def load_rows(path: str):
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", default="artifacts/evaluation_results.csv")
    parser.add_argument("--out", default="artifacts/reward_comparison.png")
    args = parser.parse_args()

    rows = load_rows(args.csv)
    grouped = defaultdict(list)
    for row in rows:
        key = (row["policy"], row["task_id"])
        grouped[key].append(float(row["quality_score"]))

    policies = sorted(set(k[0] for k in grouped.keys()))
    tasks = ["task_easy", "task_medium", "task_hard"]

    x = list(range(len(tasks)))
    width = 0.35
    fig, ax = plt.subplots(figsize=(9, 5))

    for idx, policy in enumerate(policies):
        vals = [mean(grouped.get((policy, task), [0.0])) for task in tasks]
        shift = (idx - (len(policies) - 1) / 2) * width
        ax.bar([i + shift for i in x], vals, width=width, label=policy)

    ax.set_xticks(x)
    ax.set_xticklabels(tasks)
    ax.set_ylim(0, 1.0)
    ax.set_ylabel("Mean final quality score")
    ax.set_title("Policy comparison on Collaborative DataOps environment")
    ax.legend()
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    plt.tight_layout()
    plt.savefig(args.out, dpi=160)
    print(f"Wrote plot to {args.out}")


if __name__ == "__main__":
    main()
