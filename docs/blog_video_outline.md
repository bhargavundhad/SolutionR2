# OpenEnv Hackathon Story Outline

## Hook (15-20s)
- "Most data incidents are not single-table bugs. They are socio-technical crises."
- Introduce environment as a DataOps war-room where an agent must coordinate stakeholders under uncertainty.

## Problem Statement
- Existing RL data cleaning tasks are mostly single-agent and myopic.
- Real production incidents include hidden compliance risks, conflicting stakeholders, and delayed consequences.

## What We Built
- Collaborative DataOps Environment with:
  - multi-agent interactions,
  - long-horizon mission phases,
  - partial observability + belief updates,
  - professional incident-response mechanics.

## Demo Script
- Start with `task_hard`.
- Show hidden incidents and unknown stakeholder priorities.
- Run naive strategy -> early submit -> low score.
- Run stakeholder-first strategy -> reveal hidden risks -> critical fixes -> high score.
- Show score breakdown and event log.

## Training Evidence
- Compare random vs heuristic policy over 5 seeds x 3 tasks.
- Display mean quality uplift and reward stability curves.

## Why Judges Should Care
- Research-worthy benchmark style.
- Real enterprise task framing and transferable skills.
- Clear "before vs after" training story.

## Closing
- Mention HF Space live demo and reproducible evaluation scripts.
