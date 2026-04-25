---
title: Collaborative DataOps Crisis Env
emoji: 🧭
colorFrom: purple
colorTo: blue
sdk: docker
app_port: 7860
---

# Collaborative DataOps Crisis Environment

OpenEnv environment for training LLM agents on realistic **multi-agent, long-horizon incident response** in enterprise data platforms.

## Why This Is Hackathon-Strong

- **Environment innovation first:** not a toy cleaning loop; this is a socio-technical war-room simulation.
- **Hybrid themes:** multi-agent interaction + long-horizon planning + professional world modeling.
- **Judge-friendly storytelling:** hidden risks, stakeholder conflict, and phase-based mission progression.
- **Measurable reward gains:** built-in evaluation compares random vs strategy-aware policies.

## Core Concept

The agent is a mission lead during a high-stakes DataOps outage. It must:
- discover hidden incidents under partial observability,
- align multiple stakeholders with conflicting priorities,
- orchestrate cleaning/validation/delegation actions over many steps,
- submit only after critical and compliance risks are under control.

## Theme Coverage

- **Theme 1 - Multi-Agent Interactions:** stakeholder trust/workload/priority dynamics.
- **Theme 2 - Long-Horizon Planning:** mission phases (`triage -> stabilize -> optimize -> release`) and delayed penalties.
- **Theme 3 - World Modeling / Professional Tasks:** enterprise incidents, compliance pressure, SLA-risk tradeoffs.
- **Theme 4 - Self-Improvement (optional):** memory updates and plan revision actions improve policy consistency.

## Action Space

Legacy cleaning actions remain supported and now act as tool primitives:
- `remove_duplicates`, `fill_missing`, `standardize_format`, `fix_outliers`, `convert_type`, `correct_typos`, `rename_column`, `drop_column`, `submit`

New strategic actions:
- `inspect_table`
- `query_stakeholder`
- `delegate_task`
- `run_validation_suite`
- `propose_plan`
- `negotiate_tradeoff`
- `update_memory`

## Reward Design

Dense shaping + terminal objective:

- **Step reward:** mission score delta minus step cost.
- **Submit reward:** final mission score, with penalties for unresolved critical incidents.
- **Timeout:** auto-submit with reduction.

Mission score composition:
- data integrity (35%)
- stakeholder alignment (20%)
- compliance safety (20%)
- execution confidence (15%)
- efficiency (10%)

Adjustments:
- bonus for coherent planning and risk discovery
- penalty for hidden unresolved risk pressure

## Observation Design

Every step returns:
- visible incidents and severity mix
- hidden-risk hints
- stakeholder state (`trust`, `workload`, discovered priorities)
- table health vectors (`completeness`, `consistency`, `timeliness`, `drift`)
- mission score breakdown for explainability
- narrative event log for demo storytelling
- memory bank for long-horizon policy state

## Tasks

- `task_easy`: Retail promo data triage
- `task_medium`: Healthcare claims reliability sprint
- `task_hard`: Global supply chain data crisis

Each task changes stakeholder graph, hidden incidents, and step budget.

## Quickstart

```bash
pip install -r requirements.txt
python server/app.py
```

```bash
curl -X POST http://localhost:7860/reset -H "Content-Type: application/json" -d "{\"task_id\":\"task_hard\",\"seed\":42}"
curl -X POST http://localhost:7860/step -H "Content-Type: application/json" -d "{\"action\":{\"action_type\":\"propose_plan\",\"column\":null,\"params\":{\"milestones\":[\"triage\",\"stabilize\",\"optimize\",\"release\"]}}}"
```

## Baseline Inference

Heuristic policy (default):
```bash
set POLICY_MODE=heuristic
set ENV_URL=http://localhost:7860
python inference.py
```

LLM policy:
```bash
set POLICY_MODE=llm
set API_BASE_URL=https://api.openai.com/v1
set MODEL_NAME=gpt-4o-mini
set OPENAI_API_KEY=your_key
python inference.py
```

## Training / Evaluation / Plotting

```bash
python training/run_curriculum.py
python evaluation/evaluate_policies.py
python utils/plot_rewards.py --csv artifacts/evaluation_results.csv --out artifacts/reward_comparison.png
```

Outputs:
- `artifacts/trajectories.jsonl`
- `artifacts/reward_traces.json`
- `artifacts/episode_summaries.json`
- `artifacts/evaluation_results.csv`
- `artifacts/reward_comparison.png`

## HF Space Hosting Plan

- Keep `openenv.yaml` entry point as `server.app:app`
- Build via provided `Dockerfile`
- Run validator script before submission
- Include `docs/blog_video_outline.md` and `demo/demo_trajectories.json` in submission assets

## Repository Layout

- `server/environment_v2.py` — collaborative long-horizon environment
- `server/app.py` — OpenEnv HTTP server
- `models.py` — typed models with mission-centric fields
- `inference.py` — heuristic or LLM policy runner
- `hackathon_benchmark.py` — full 3-policy benchmark (random / heuristic / trained)
- `training/run_curriculum.py` — trajectory generation
- `evaluation/evaluate_policies.py` — policy comparison script
- `utils/plot_rewards.py` — visual evidence plotter
- `demo/demo_trajectories.json` — demo story trajectories
- `docs/architecture_summary.md` — system architecture diagrams
- `docs/judge_presentation.md` — benchmark results & competitive analysis
- `docs/submission_checklist.md` — final verification checklist
- `docs/blog_video_outline.md` — presentation structure

## License

BSD 3-Clause License
