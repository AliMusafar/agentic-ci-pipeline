from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime


class RunEvent(BaseModel):
    schema_version: str = "run_event/v1"
    run_id: str
    stage_id: str
    attempt: int = 1
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    actor_type: str  # system, agent
    actor_id: str
    event_type: str  # stage_transition, finding_emitted, stage_started, stage_completed, stage_failed
    status: str  # success, failure, in_progress, warning
    duration_ms: Optional[int] = None
    metadata: Dict[str, Any] = {}
