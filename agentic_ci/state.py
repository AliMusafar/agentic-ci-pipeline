from enum import Enum
from datetime import datetime
from typing import List, Dict, Any
import json
from pathlib import Path


class RunStage(str, Enum):
    QUEUED = "queued"
    PREFLIGHT = "preflight"
    DETERMINISTIC_CHECKS = "deterministic_checks"
    IMPACT_MAPPING = "impact_mapping"
    REVIEW = "review"
    NORMALIZE_FINDINGS = "normalize_findings"
    PUBLISH = "publish"
    COMPLETED = "completed"
    FAILED = "failed"


class RunStateMachine:
    def __init__(self, run_id: str, artifacts_dir: Path):
        self.run_id = run_id
        self.artifacts_dir = artifacts_dir
        self.current_stage = RunStage.QUEUED
        self.events: List[Dict[str, Any]] = []
        self._record(RunStage.QUEUED, "in_progress")

    def transition(self, stage: RunStage, status: str = "in_progress", metadata: Dict = None):
        self.current_stage = stage
        self._record(stage, status, metadata)
        print(f"  [{stage.value}] {status}")

    def fail(self, reason: str):
        self._record(RunStage.FAILED, "failure", {"reason": reason})
        print(f"  [failed] {reason}")

    def _record(self, stage: RunStage, status: str, metadata: Dict = None):
        event = {
            "schema_version": "run_event/v1",
            "run_id": self.run_id,
            "stage_id": stage.value,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "actor_type": "system",
            "actor_id": "run_coordinator",
            "event_type": "stage_transition",
            "status": status,
            "metadata": metadata or {},
        }
        self.events.append(event)
        self._persist()

    def _persist(self):
        path = self.artifacts_dir / "run-events.json"
        path.write_text(json.dumps(self.events, indent=2), encoding="utf-8")
