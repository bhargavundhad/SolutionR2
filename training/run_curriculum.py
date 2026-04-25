"""
Curriculum trajectory generator for RL/SFT pipelines.

This script collects transitions from the heuristic policy and exports:
- step-level reward traces
- episode summaries
- trajectory JSONL suitable for TRL/Unsloth preprocessing
"""

import json
import os
from typing import Dict, List

import requests

from inference import choose_heuristic_action


ENV_URL = os.environ.get("ENV_URL", "http://localhost:7860")
TASKS = [("task_easy", 8), ("task_medium", 8), ("task_hard", 10)]
SEEDS = [100, 101, 102, 103, 104]


def env_reset(task_id: str, seed: int) -> Dict:
    r = requests.post(f"{ENV_URL}/reset", json={"task_id": task_id, "seed": seed}, timeout=30)
    r.raise_for_status()
    return r.json()


def env_step(action: Dict) -> Dict:
    r = requests.post(f"{ENV_URL}/step", json={"action": action}, timeout=30)
    r.raise_for_status()
    return r.json()


def main() -> None:
    os.makedirs("artifacts", exist_ok=True)
    traces: List[Dict] = []
    episode_rows: List[Dict] = []
    jsonl_path = os.path.join("artifacts", "trajectories.jsonl")
    with open(jsonl_path, "w", encoding="utf-8") as out_jsonl:
        for task_id, max_override in TASKS:
            for seed in SEEDS:
                obs = env_reset(task_id, seed)
                done = False
                step = 0
                total_reward = 0.0
                episode_trace = []
                while not done and step < max_override:
                    action = choose_heuristic_action(obs)
                    next_obs = env_step(action)
                    reward = float(next_obs.get("reward", 0.0) or 0.0)
                    done = bool(next_obs.get("done", False))
                    quality = float(next_obs.get("observation", {}).get("metadata", {}).get("quality_score", 0.0))
                    row = {
                        "task_id": task_id,
                        "seed": seed,
                        "step": step + 1,
                        "action": action,
                        "reward": round(reward, 4),
                        "quality_score": round(quality, 4),
                        "done": done,
                    }
                    traces.append(row)
                    episode_trace.append(row)
                    total_reward += reward
                    obs = next_obs
                    step += 1
                final_quality = float(obs.get("observation", {}).get("metadata", {}).get("quality_score", 0.0))
                episode_rows.append(
                    {
                        "task_id": task_id,
                        "seed": seed,
                        "steps": step,
                        "total_reward": round(total_reward, 4),
                        "final_quality": round(final_quality, 4),
                    }
                )
                out_jsonl.write(
                    json.dumps(
                        {
                            "task_id": task_id,
                            "seed": seed,
                            "trajectory": episode_trace,
                            "summary": episode_rows[-1],
                        }
                    )
                    + "\n"
                )
    with open(os.path.join("artifacts", "reward_traces.json"), "w", encoding="utf-8") as f:
        json.dump(traces, f, indent=2)
    with open(os.path.join("artifacts", "episode_summaries.json"), "w", encoding="utf-8") as f:
        json.dump(episode_rows, f, indent=2)
    print("Saved artifacts/trajectories.jsonl, artifacts/reward_traces.json, artifacts/episode_summaries.json")


if __name__ == "__main__":
    main()
