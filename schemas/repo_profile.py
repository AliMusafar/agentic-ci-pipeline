from pydantic import BaseModel
from typing import List, Optional


class Commands(BaseModel):
    preflight: List[str] = []
    deterministic_checks: List[str] = []
    final_checks: List[str] = []


class Paths(BaseModel):
    editable: List[str] = []
    protected: List[str] = []


class Policies(BaseModel):
    max_files_per_batch: int = 10
    max_net_lines_per_batch: int = 400
    allow_external_review: bool = False


class RepoProfile(BaseModel):
    schema_version: str = "repo_profile/v1"
    repo_name: str
    base_branch: str = "main"
    commands: Commands = Commands()
    paths: Paths = Paths()
    docs_index: Optional[str] = None
    services_registry: Optional[str] = None
    policies: Policies = Policies()
