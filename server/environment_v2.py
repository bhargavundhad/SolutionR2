"""
Collaborative DataOps Crisis Environment (OpenEnv-compatible).

This environment targets hackathon-grade innovation by combining:
- Multi-agent interactions (stakeholders with hidden priorities)
- Long-horizon planning (phased mission with delayed effects)
- Professional world modeling (DataOps incident response workflow)
- Partial observability and belief tracking
"""

import random
import uuid
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from models import DataCleaningAction, DataCleaningObservation, DataCleaningState
from openenv.core.env_server.interfaces import Environment


@dataclass
class Incident:
    incident_id: str
    title: str
    severity: str
    table: str
    category: str
    hidden: bool
    resolved: bool = False
    revealed_by: str = ""
    dependency: Optional[str] = None


def _clip01(x: float) -> float:
    return max(0.0, min(1.0, x))


SCENARIOS: Dict[str, Dict[str, Any]] = {
    "task_easy": {
        "name": "Retail Promo DataOps Triage",
        "difficulty": "easy",
        "max_steps": 20,
        "tables": ["orders", "customers", "pricing"],
        "stakeholders": {
            "data_engineer": {"priority": "schema_stability", "trust": 0.62, "workload": 0.45},
            "product_manager": {"priority": "delivery_speed", "trust": 0.55, "workload": 0.40},
            "compliance_officer": {"priority": "auditability", "trust": 0.58, "workload": 0.35},
        },
        "incidents": [
            ("INC-001", "Duplicate order payloads from retry loop", "high", "orders", "duplicates", False, None),
            ("INC-002", "Missing loyalty identifiers", "medium", "customers", "missingness", False, None),
            ("INC-003", "Currency string parsing failures", "medium", "pricing", "type", False, None),
            ("INC-004", "Silent date format divergence", "low", "orders", "format", True, "INC-001"),
        ],
    },
    "task_medium": {
        "name": "Healthcare Claims Reliability Sprint",
        "difficulty": "medium",
        "max_steps": 28,
        "tables": ["claims", "providers", "patients", "billing"],
        "stakeholders": {
            "data_engineer": {"priority": "pipeline_resilience", "trust": 0.60, "workload": 0.58},
            "ops_lead": {"priority": "sla_adherence", "trust": 0.50, "workload": 0.64},
            "compliance_officer": {"priority": "phi_safety", "trust": 0.54, "workload": 0.47},
            "finance_manager": {"priority": "revenue_accuracy", "trust": 0.48, "workload": 0.55},
        },
        "incidents": [
            ("INC-101", "Provider identifiers are duplicated", "high", "providers", "duplicates", False, None),
            ("INC-102", "PII masking inconsistency in patient notes", "critical", "patients", "compliance", True, None),
            ("INC-103", "Delayed claim ingest causes stale snapshots", "high", "claims", "timeliness", False, None),
            ("INC-104", "Billing code typos degrade adjudication", "medium", "billing", "typos", False, "INC-101"),
            ("INC-105", "Null adjudication_status spikes", "high", "claims", "missingness", False, None),
        ],
    },
    "task_hard": {
        "name": "Global Supply Chain Data Crisis",
        "difficulty": "hard",
        "max_steps": 36,
        "tables": ["shipments", "inventory", "vendors", "customs", "forecast"],
        "stakeholders": {
            "data_engineer": {"priority": "schema_consistency", "trust": 0.56, "workload": 0.68},
            "ops_lead": {"priority": "on_time_delivery", "trust": 0.47, "workload": 0.72},
            "compliance_officer": {"priority": "trade_compliance", "trust": 0.50, "workload": 0.61},
            "regional_manager": {"priority": "local_exceptions", "trust": 0.46, "workload": 0.66},
            "finance_manager": {"priority": "margin_protection", "trust": 0.45, "workload": 0.57},
        },
        "incidents": [
            ("INC-201", "Shipment duplicates from multi-region replay", "high", "shipments", "duplicates", False, None),
            ("INC-202", "Customs tariff codes missing for APAC records", "critical", "customs", "compliance", True, None),
            ("INC-203", "Vendor score drift after schema migration", "high", "vendors", "drift", False, None),
            ("INC-204", "Negative inventory bursts in edge warehouses", "critical", "inventory", "outlier", False, None),
            ("INC-205", "Forecast horizon misalignment", "medium", "forecast", "timeliness", True, "INC-203"),
            ("INC-206", "Currency normalization mismatch", "medium", "shipments", "format", False, "INC-201"),
        ],
    },
}


class CollaborativeDataOpsEnvironment(Environment):
    SUPPORTS_CONCURRENT_SESSIONS = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._task_id = "task_easy"
        self._task_config = SCENARIOS["task_easy"]
        self._rng = random.Random(42)
        self._episode_id = ""
        self._step_count = 0
        self._max_steps = 20
        self._done = False
        self._reward = 0.0
        self._prev_score = 0.0
        self._last_action_success = True
        self._last_action_msg = ""
        self._actions_taken: List[str] = []
        self._mission_phase = "triage"
        self._plan_quality = 0.15
        self._delivery_confidence = 0.35
        self._hidden_risk_pressure = 0.65
        self._compliance_risk = 0.70
        self._memory_bank: Dict[str, str] = {}
        self._narrative_events: List[str] = []
        self._stakeholders: Dict[str, Dict[str, Any]] = {}
        self._table_health: Dict[str, Dict[str, float]] = {}
        self._incidents: List[Incident] = []

    def reset(
        self,
        seed: Optional[int] = None,
        episode_id: Optional[str] = None,
        task_id: Optional[str] = None,
        **kwargs,
    ) -> DataCleaningObservation:
        if seed is None:
            seed = random.randint(0, 2**31)
        self._rng = random.Random(seed)
        self._task_id = task_id or kwargs.get("task_id", "task_easy")
        if self._task_id not in SCENARIOS:
            self._task_id = "task_easy"
        self._task_config = SCENARIOS[self._task_id]
        self._episode_id = episode_id or str(uuid.uuid4())
        self._step_count = 0
        self._max_steps = self._task_config["max_steps"]
        self._done = False
        self._reward = 0.0
        self._prev_score = 0.0
        self._last_action_success = True
        self._last_action_msg = "Mission reset: start with triage and stakeholder alignment."
        self._actions_taken = []
        self._mission_phase = "triage"
        self._plan_quality = 0.12
        self._delivery_confidence = 0.33
        self._hidden_risk_pressure = 0.72 if self._task_id == "task_hard" else 0.58
        self._compliance_risk = 0.74 if self._task_id == "task_hard" else 0.61
        self._memory_bank = {}
        self._narrative_events = [
            f"War-room opened for scenario: {self._task_config['name']}",
            "Agent must coordinate stakeholders before final incident closeout.",
        ]
        self._stakeholders = {}
        for name, payload in self._task_config["stakeholders"].items():
            self._stakeholders[name] = {
                "priority": payload["priority"],
                "known_priority": False,
                "trust": payload["trust"],
                "workload": payload["workload"],
                "last_engaged_step": -1,
            }
        self._table_health = {}
        for table in self._task_config["tables"]:
            self._table_health[table] = {
                "completeness": self._rng.uniform(0.42, 0.68),
                "consistency": self._rng.uniform(0.40, 0.70),
                "timeliness": self._rng.uniform(0.45, 0.72),
                "drift": self._rng.uniform(0.25, 0.62),
            }
        self._incidents = []
        for iid, title, sev, table, category, hidden, dep in self._task_config["incidents"]:
            self._incidents.append(
                Incident(
                    incident_id=iid,
                    title=title,
                    severity=sev,
                    table=table,
                    category=category,
                    hidden=hidden,
                    dependency=dep,
                )
            )
        return self._build_observation()

    def step(self, action: DataCleaningAction, timeout_s: Optional[float] = None, **kwargs) -> DataCleaningObservation:
        if self._done:
            return self._build_observation()
        self._step_count += 1
        self._actions_taken.append(action.action_type)
        try:
            self._execute_action(action)
            self._last_action_success = True
        except Exception as exc:
            self._last_action_success = False
            self._last_action_msg = f"Action failed: {exc}"
            self._reward = -0.04
        current_score = self._compute_mission_score()
        delta = current_score - self._prev_score
        step_cost = 0.008 + (0.004 if self._task_id == "task_hard" else 0.0)
        self._reward = max(-0.5, min(0.5, (delta * 1.5) - step_cost))
        if action.action_type == "submit":
            self._done = True
            unresolved_critical = self._unresolved_critical_count()
            submit_penalty = 0.20 * unresolved_critical
            final_score = max(0.0, current_score - submit_penalty)
            bonus = 0.15 if unresolved_critical == 0 and self._stakeholder_alignment() > 0.60 else -0.10
            self._reward = final_score + bonus
            self._last_action_msg = (
                f"Mission submitted. Final score={final_score:.4f}; "
                f"critical_unresolved={unresolved_critical}; bonus={bonus:.3f}"
            )
        if self._step_count >= self._max_steps and not self._done:
            self._done = True
            timeout_score = self._compute_mission_score() * 0.82
            self._reward = timeout_score
            self._last_action_msg = f"Step budget exhausted. Auto-submitted with penalized score {timeout_score:.4f}."
        self._prev_score = current_score
        return self._build_observation()

    @property
    def state(self) -> DataCleaningState:
        return DataCleaningState(
            episode_id=self._episode_id,
            step_count=self._step_count,
            task_id=self._task_id,
            current_step=self._step_count,
            max_steps=self._max_steps,
            is_done=self._done,
            current_score=self._compute_mission_score(),
            actions_taken=self._actions_taken,
            mission_phase=self._mission_phase,
            unresolved_critical_incidents=self._unresolved_critical_count(),
            stakeholder_alignment=self._stakeholder_alignment(),
            compliance_risk=self._compliance_risk,
        )

    def _compute_mission_score(self) -> float:
        avg_integrity = 0.0
        if self._table_health:
            for metrics in self._table_health.values():
                avg_integrity += (
                    metrics["completeness"] * 0.35
                    + metrics["consistency"] * 0.35
                    + metrics["timeliness"] * 0.20
                    + (1.0 - metrics["drift"]) * 0.10
                )
            avg_integrity /= len(self._table_health)
        alignment = self._stakeholder_alignment()
        compliance = 1.0 - self._compliance_risk
        unresolved_ratio = self._unresolved_ratio()
        execution = _clip01(1.0 - unresolved_ratio * 0.85)
        efficiency = _clip01(1.0 - (self._step_count / max(1, self._max_steps)))
        score = (
            0.35 * avg_integrity
            + 0.20 * alignment
            + 0.20 * compliance
            + 0.15 * execution
            + 0.10 * efficiency
        )
        score += 0.05 * self._plan_quality
        score -= 0.05 * self._hidden_risk_pressure
        return round(_clip01(score), 4)

    def _stakeholder_alignment(self) -> float:
        if not self._stakeholders:
            return 0.0
        return sum(v["trust"] for v in self._stakeholders.values()) / len(self._stakeholders)

    def _unresolved_ratio(self) -> float:
        if not self._incidents:
            return 0.0
        unresolved = sum(1 for i in self._incidents if not i.resolved)
        return unresolved / len(self._incidents)

    def _unresolved_critical_count(self) -> int:
        return sum(1 for i in self._incidents if not i.resolved and i.severity == "critical")

    def _severity_weight(self, severity: str) -> float:
        return {"low": 0.03, "medium": 0.06, "high": 0.10, "critical": 0.14}.get(severity, 0.05)

    def _execute_action(self, action: DataCleaningAction) -> None:
        atype = action.action_type
        params = action.params or {}
        if atype in {"remove_duplicates", "fill_missing", "standardize_format", "fix_outliers", "convert_type", "correct_typos"}:
            self._action_run_cleaning_tool(atype, action.column, params)
        elif atype == "drop_column":
            self._action_reduce_drift(action.column)
        elif atype == "rename_column":
            self._action_repair_schema(action.column, params.get("new_name"))
        elif atype == "inspect_table":
            self._action_inspect_table(action.column or params.get("table"))
        elif atype == "query_stakeholder":
            self._action_query_stakeholder(params.get("stakeholder") or action.column)
        elif atype == "delegate_task":
            self._action_delegate_task(params.get("stakeholder"), params.get("objective", "generic_fix"))
        elif atype == "run_validation_suite":
            self._action_run_validation_suite(params.get("suite", "integrity"))
        elif atype == "propose_plan":
            self._action_propose_plan(params.get("milestones", []))
        elif atype == "negotiate_tradeoff":
            self._action_negotiate_tradeoff(params.get("stakeholder"), params.get("concession", "status_update"))
        elif atype == "update_memory":
            key = str(params.get("key", "")).strip()
            value = str(params.get("value", "")).strip()
            if not key:
                raise ValueError("update_memory requires params.key")
            self._memory_bank[key] = value[:240]
            self._plan_quality = _clip01(self._plan_quality + 0.02)
            self._last_action_msg = f"Memory updated: {key}"
        elif atype == "submit":
            pass
        else:
            raise ValueError(f"Unknown action_type '{atype}'")
        self._advance_phase()
        self._apply_dynamics()

    def _action_inspect_table(self, table: Optional[str]) -> None:
        if not table:
            raise ValueError("inspect_table requires a table")
        if table not in self._table_health:
            raise ValueError(f"Unknown table '{table}'")
        reveal_candidates = [i for i in self._incidents if i.table == table and i.hidden and not i.resolved]
        if reveal_candidates:
            chosen = self._rng.choice(reveal_candidates)
            chosen.hidden = False
            chosen.revealed_by = "inspect_table"
            self._hidden_risk_pressure = _clip01(self._hidden_risk_pressure - 0.08)
            self._last_action_msg = f"Inspection revealed hidden incident {chosen.incident_id} on {table}."
        else:
            self._last_action_msg = f"Inspection complete for {table}; no new hidden incidents found."
        self._table_health[table]["consistency"] = _clip01(self._table_health[table]["consistency"] + 0.03)

    def _action_query_stakeholder(self, stakeholder: Optional[str]) -> None:
        if not stakeholder:
            raise ValueError("query_stakeholder requires stakeholder")
        if stakeholder not in self._stakeholders:
            raise ValueError(f"Unknown stakeholder '{stakeholder}'")
        s = self._stakeholders[stakeholder]
        first_time = not s["known_priority"]
        s["known_priority"] = True
        s["trust"] = _clip01(s["trust"] + 0.05)
        s["workload"] = _clip01(s["workload"] - 0.04)
        s["last_engaged_step"] = self._step_count
        if first_time:
            self._plan_quality = _clip01(self._plan_quality + 0.05)
            self._hidden_risk_pressure = _clip01(self._hidden_risk_pressure - 0.04)
        self._last_action_msg = f"{stakeholder} shared priority='{s['priority']}'. Trust improved."

    def _action_delegate_task(self, stakeholder: Optional[str], objective: str) -> None:
        if not stakeholder or stakeholder not in self._stakeholders:
            raise ValueError("delegate_task requires a valid stakeholder")
        s = self._stakeholders[stakeholder]
        if s["workload"] > 0.85:
            s["trust"] = _clip01(s["trust"] - 0.05)
            self._last_action_msg = f"Delegation to {stakeholder} failed due to overload."
            return
        s["workload"] = _clip01(s["workload"] + 0.08)
        s["trust"] = _clip01(s["trust"] + 0.03)
        unresolved = [i for i in self._incidents if not i.resolved and not i.hidden]
        if unresolved:
            target = self._rng.choice(unresolved)
            target.resolved = True
            self._delivery_confidence = _clip01(self._delivery_confidence + 0.07)
            self._compliance_risk = _clip01(self._compliance_risk - (0.05 if target.category == "compliance" else 0.02))
            self._last_action_msg = f"{stakeholder} delegated '{objective}' and resolved {target.incident_id}."
        else:
            self._last_action_msg = f"{stakeholder} delegated '{objective}', but no visible incidents remained."

    def _action_propose_plan(self, milestones: List[str]) -> None:
        quality_gain = 0.03
        if milestones and len(milestones) >= 3:
            quality_gain += 0.05
        known = sum(1 for s in self._stakeholders.values() if s["known_priority"])
        quality_gain += min(0.05, known * 0.01)
        self._plan_quality = _clip01(self._plan_quality + quality_gain)
        self._delivery_confidence = _clip01(self._delivery_confidence + 0.04)
        self._last_action_msg = f"Plan drafted with {len(milestones)} milestones. Plan quality now {self._plan_quality:.2f}."

    def _action_negotiate_tradeoff(self, stakeholder: Optional[str], concession: str) -> None:
        if not stakeholder or stakeholder not in self._stakeholders:
            raise ValueError("negotiate_tradeoff requires valid stakeholder")
        s = self._stakeholders[stakeholder]
        shift = 0.06 if concession in {"latency_budget", "scope_reduction", "status_update"} else 0.03
        s["trust"] = _clip01(s["trust"] + shift)
        self._delivery_confidence = _clip01(self._delivery_confidence + 0.03)
        self._last_action_msg = f"Negotiated with {stakeholder} via concession '{concession}'."

    def _action_run_validation_suite(self, suite: str) -> None:
        suite = suite or "integrity"
        found = [i for i in self._incidents if i.hidden and not i.resolved]
        reveal_count = 0
        if found:
            sample_n = min(len(found), 2 if suite == "compliance" else 1)
            for inc in self._rng.sample(found, sample_n):
                inc.hidden = False
                inc.revealed_by = "run_validation_suite"
                reveal_count += 1
        self._hidden_risk_pressure = _clip01(self._hidden_risk_pressure - (0.06 + 0.02 * reveal_count))
        if suite == "compliance":
            self._compliance_risk = _clip01(self._compliance_risk - 0.06)
        self._last_action_msg = f"Validation suite '{suite}' executed; revealed {reveal_count} hidden incidents."

    def _action_repair_schema(self, column: Optional[str], new_name: Optional[str]) -> None:
        del column, new_name
        for t in self._table_health.values():
            t["consistency"] = _clip01(t["consistency"] + 0.04)
            t["drift"] = _clip01(t["drift"] - 0.06)
        self._delivery_confidence = _clip01(self._delivery_confidence + 0.03)
        self._last_action_msg = "Schema contract repaired across tables."

    def _action_reduce_drift(self, column: Optional[str]) -> None:
        del column
        for t in self._table_health.values():
            t["drift"] = _clip01(t["drift"] - 0.05)
        self._last_action_msg = "Legacy/noisy feature removed; drift reduced."

    def _action_run_cleaning_tool(self, tool_type: str, column: Optional[str], params: Dict[str, Any]) -> None:
        del column, params
        visible_open = [i for i in self._incidents if not i.resolved and not i.hidden]
        if visible_open:
            target = self._rng.choice(visible_open)
            target.resolved = True
            w = self._severity_weight(target.severity)
            table_metrics = self._table_health[target.table]
            table_metrics["completeness"] = _clip01(table_metrics["completeness"] + w * 0.7)
            table_metrics["consistency"] = _clip01(table_metrics["consistency"] + w * 0.8)
            if target.category in {"timeliness"}:
                table_metrics["timeliness"] = _clip01(table_metrics["timeliness"] + w)
            if target.category in {"drift", "format"}:
                table_metrics["drift"] = _clip01(table_metrics["drift"] - w * 0.8)
            if target.category == "compliance":
                self._compliance_risk = _clip01(self._compliance_risk - w)
            self._delivery_confidence = _clip01(self._delivery_confidence + 0.02 + w * 0.2)
            self._last_action_msg = f"{tool_type} resolved {target.incident_id} ({target.title})."
        else:
            for t in self._table_health.values():
                t["consistency"] = _clip01(t["consistency"] + 0.01)
            self._last_action_msg = f"{tool_type} executed; no visible incident directly resolved."

    def _advance_phase(self) -> None:
        unresolved_ratio = self._unresolved_ratio()
        if self._step_count < max(4, self._max_steps * 0.2):
            self._mission_phase = "triage"
        elif unresolved_ratio > 0.35:
            self._mission_phase = "stabilize"
        elif unresolved_ratio > 0.12:
            self._mission_phase = "optimize"
        else:
            self._mission_phase = "release"

    def _apply_dynamics(self) -> None:
        if self._step_count % 4 == 0:
            self._hidden_risk_pressure = _clip01(self._hidden_risk_pressure + 0.03)
        if self._mission_phase in {"triage", "stabilize"} and self._plan_quality < 0.25:
            self._delivery_confidence = _clip01(self._delivery_confidence - 0.02)
        for stakeholder in self._stakeholders.values():
            if stakeholder["last_engaged_step"] >= 0 and self._step_count - stakeholder["last_engaged_step"] > 7:
                stakeholder["trust"] = _clip01(stakeholder["trust"] - 0.02)
            stakeholder["workload"] = _clip01(stakeholder["workload"] + 0.005)
        if self._step_count % 5 == 0:
            unresolved_critical = self._unresolved_critical_count()
            self._compliance_risk = _clip01(self._compliance_risk + unresolved_critical * 0.02)
        self._narrative_events.append(
            f"Step {self._step_count}: phase={self._mission_phase}, score={self._compute_mission_score():.3f}"
        )
        self._narrative_events = self._narrative_events[-8:]

    def _build_observation(self) -> DataCleaningObservation:
        visible_incidents = []
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for inc in self._incidents:
            if not inc.hidden and not inc.resolved:
                severity_counts[inc.severity] = severity_counts.get(inc.severity, 0) + 1
                visible_incidents.append(
                    {
                        "incident_id": inc.incident_id,
                        "title": inc.title,
                        "severity": inc.severity,
                        "table": inc.table,
                        "category": inc.category,
                        "dependency": inc.dependency,
                    }
                )
        detected_issues = []
        for inc in visible_incidents:
            detected_issues.append(f"[{inc['severity']}] {inc['incident_id']} @ {inc['table']}: {inc['title']}")
        for sev, count in severity_counts.items():
            if count > 0:
                detected_issues.append(f"{count} unresolved {sev} incidents")
        hidden_unresolved = sum(1 for i in self._incidents if i.hidden and not i.resolved)
        if hidden_unresolved > 0:
            detected_issues.append("Potential hidden incidents remain; gather more evidence.")

        stakeholder_status: Dict[str, Dict[str, Any]] = {}
        for name, payload in self._stakeholders.items():
            stakeholder_status[name] = {
                "trust": round(payload["trust"], 3),
                "workload": round(payload["workload"], 3),
                "known_priority": payload["known_priority"],
                "priority": payload["priority"] if payload["known_priority"] else "unknown",
            }
        mission_score_breakdown = {
            "data_integrity": round(
                sum(
                    (
                        t["completeness"] * 0.35
                        + t["consistency"] * 0.35
                        + t["timeliness"] * 0.20
                        + (1.0 - t["drift"]) * 0.10
                    )
                    for t in self._table_health.values()
                )
                / max(1, len(self._table_health)),
                4,
            ),
            "stakeholder_alignment": round(self._stakeholder_alignment(), 4),
            "compliance_safety": round(1.0 - self._compliance_risk, 4),
            "delivery_confidence": round(self._delivery_confidence, 4),
            "plan_quality": round(self._plan_quality, 4),
            "hidden_risk_penalty": round(self._hidden_risk_pressure, 4),
            "mission_score": self._compute_mission_score(),
        }
        hints = []
        if hidden_unresolved > 0:
            hints.append("Run validation suites to discover latent failures.")
        if any(not s["known_priority"] for s in self._stakeholders.values()):
            hints.append("Unqueried stakeholders likely hide conflicting priorities.")
        if self._unresolved_critical_count() > 0:
            hints.append("Critical incidents unresolved: submission now is risky.")

        sample_data = []
        for table, metrics in self._table_health.items():
            sample_data.append(
                {
                    "table": table,
                    "completeness": round(metrics["completeness"], 3),
                    "consistency": round(metrics["consistency"], 3),
                    "timeliness": round(metrics["timeliness"], 3),
                    "drift": round(metrics["drift"], 3),
                }
            )
        missing_value_counts = {
            t: int(round((1.0 - m["completeness"]) * 100))
            for t, m in self._table_health.items()
        }
        column_stats = {
            "mission": {
                "mean": round(sum(mission_score_breakdown.values()) / len(mission_score_breakdown), 3),
                "std": 0.0,
                "min": round(min(mission_score_breakdown.values()), 3),
                "max": round(max(mission_score_breakdown.values()), 3),
                "count": len(mission_score_breakdown),
            }
        }
        metadata = {
            "quality_score": self._compute_mission_score(),
            "episode_id": self._episode_id,
            "scenario_name": self._task_config["name"],
            "hidden_unresolved_count": hidden_unresolved,
        }
        return DataCleaningObservation(
            done=self._done,
            reward=self._reward,
            num_rows=len(self._incidents),
            num_columns=len(self._table_health),
            column_names=list(self._table_health.keys()),
            column_types={k: "table_health_vector" for k in self._table_health.keys()},
            missing_value_counts=missing_value_counts,
            duplicate_row_count=severity_counts.get("high", 0),
            sample_data=sample_data[:5],
            column_stats=column_stats,
            detected_issues=detected_issues,
            last_action_success=self._last_action_success,
            last_action_message=self._last_action_msg,
            task_id=self._task_id,
            task_description=(
                f"{self._task_config['name']} | Multi-agent DataOps mission with partial observability."
            ),
            max_steps=self._max_steps,
            current_step=self._step_count,
            metadata=metadata,
            mission_phase=self._mission_phase,
            visible_incidents=visible_incidents,
            hidden_risks_hint=hints,
            stakeholder_status=stakeholder_status,
            table_health=self._table_health,
            memory_bank=self._memory_bank,
            mission_score_breakdown=mission_score_breakdown,
            narrative_event_log=self._narrative_events,
        )
