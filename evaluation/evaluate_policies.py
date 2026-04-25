"""
Policy evaluation for Collaborative DataOps Environment.

Generates quantitative evidence for reward improvement:
- random policy baseline
- heuristic policy (long-horizon + stakeholder-aware)
"""

import csv
import os
import random
import sys
from typing import Dict, List

import requests

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from ..inference import choose_heuristic_action
except ImportError:
    # When run as a script, use absolute import
    from inference import choose_heuristic_action


ENV_URL = os.environ.get("ENV_URL", "http://localhost:7860")
SEEDS = [11, 22, 33, 44, 55]
TASKS = ["task_easy", "task_medium", "task_hard"]
MAX_STEPS_CAP = 50


def env_reset(task_id: str, seed: int) -> Dict:
    r = requests.post(f"{ENV_URL}/reset", json={"task_id": task_id, "seed": seed}, timeout=30)
    r.raise_for_status()
    return r.json()


def env_step(action: Dict) -> Dict:
    r = requests.post(f"{ENV_URL}/step", json={"action": action}, timeout=30)
    r.raise_for_status()
    return r.json()


def random_action(obs: Dict, rng: random.Random) -> Dict:
    o = obs.get("observation", obs)
    tables = list(o.get("table_health", {}).keys()) or o.get("column_names", [])
    stakeholders = list(o.get("stakeholder_status", {}).keys())
    candidates: List[Dict] = [
        {"action_type": "propose_plan", "column": None, "params": {"milestones": ["triage", "fix", "submit"]}},
        {"action_type": "run_validation_suite", "column": None, "params": {"suite": rng.choice(["integrity", "compliance"])}},
        {"action_type": "submit", "column": None, "params": {}},
    ]
    if tables:
        t = rng.choice(tables)
        candidates.extend(
            [
                {"action_type": "inspect_table", "column": t, "params": {}},
                {"action_type": "remove_duplicates", "column": t, "params": {}},
                {"action_type": "fill_missing", "column": t, "params": {"strategy": "mode"}},
                {"action_type": "fix_outliers", "column": t, "params": {"strategy": "clip"}},
            ]
        )
    if stakeholders:
        s = rng.choice(stakeholders)
        candidates.extend(
            [
                {"action_type": "query_stakeholder", "column": None, "params": {"stakeholder": s}},
                {"action_type": "delegate_task", "column": None, "params": {"stakeholder": s, "objective": "incident_fix"}},
                {"action_type": "negotiate_tradeoff", "column": None, "params": {"stakeholder": s, "concession": "status_update"}},
            ]
        )
    return rng.choice(candidates)


def rollout(task_id: str, seed: int, policy: str) -> Dict:
    rng = random.Random(seed + hash(policy) % 1000)
    obs = env_reset(task_id, seed)
    total_reward = 0.0
    steps = 0
    done = False
    while not done and steps < MAX_STEPS_CAP:
        if policy == "heuristic":
            action = choose_heuristic_action(obs)
        else:
            action = random_action(obs, rng)
        obs = env_step(action)
        total_reward += float(obs.get("reward", 0.0) or 0.0)
        done = bool(obs.get("done", False))
        steps += 1
    quality = float(obs.get("observation", {}).get("metadata", {}).get("quality_score", 0.0))
    return {
        "policy": policy,
        "task_id": task_id,
        "seed": seed,
        "steps": steps,
        "total_reward": round(total_reward, 4),
        "quality_score": round(quality, 4),
    }


def main() -> None:
    os.makedirs("artifacts", exist_ok=True)
    rows: List[Dict] = []
    for task in TASKS:
        for seed in SEEDS:
            rows.append(rollout(task, seed, "random"))
            rows.append(rollout(task, seed, "heuristic"))
    out_path = os.path.join("artifacts", "evaluation_results.csv")
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["policy", "task_id", "seed", "steps", "total_reward", "quality_score"],
        )
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote evaluation results to {out_path}")


if __name__ == "__main__":
    main()
