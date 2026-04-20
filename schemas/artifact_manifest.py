from pydantic import BaseModel
from typing import List, Dict, Optional


class ArtifactEntry(BaseModel):
    path: str
    sha256: Optional[str] = None


class ArtifactManifest(BaseModel):
    schema_version: str = "artifact_manifest/v1"
    run_id: str
    repo: str
    base_ref: str
    head_ref: str
    base_sha: Optional[str] = None
    head_sha: Optional[str] = None
    status: str  # completed, failed, partial
    published_output_kind: str  # report_only, verified_fix_branch, unverified_patch_bundle
    schema_versions: Dict[str, str] = {
        "repo_profile": "repo_profile/v1",
        "review_pack": "review_pack/v1",
        "finding": "finding/v1",
        "run_event": "run_event/v1",
        "artifact_manifest": "artifact_manifest/v1",
    }
    artifacts: List[ArtifactEntry] = []
