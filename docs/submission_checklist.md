# Submission Checklist

- [x] `openenv.yaml` present and valid entry point.
- [x] OpenEnv server implements `/reset`, `/step`, `/state`, `/health`.
- [x] Environment supports deterministic `seed` behavior.
- [x] Multi-task curriculum (`task_easy`, `task_medium`, `task_hard`) defined.
- [x] Reward function is dense + terminal, with anti-gaming penalties.
- [x] Baseline inference script runs locally and on HF Space.
- [x] Evaluation script compares at least two policies.
- [x] Plot utility produces visual training evidence.
- [x] Demo trajectories included for narrative presentation.
- [x] README explains innovation, mechanics, and reproducibility.
- [x] Dockerfile compatible with HF Spaces.
- [x] Artifacts paths standardized under `artifacts/`.
