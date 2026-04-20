import uuid
import shutil
import tempfile
import subprocess
from pathlib import Path
from datetime import datetime

import yaml

from agentic_ci.state import RunStateMachine, RunStage
from agentic_ci.preflight import run_preflight, run_deterministic_checks
from agentic_ci.impact import compute_diff, get_changed_files, select_review_packs, read_file_contents
from agentic_ci.reviewer import run_reviewer
from agentic_ci.ledger import normalize_and_dedupe, sort_findings
from agentic_ci.reporter import write_findings, write_report, write_manifest, sha256_file
from schemas.repo_profile import RepoProfile, Commands, Paths, Policies
from schemas.review_pack import ReviewPack, ScopeSelector
from schemas.artifact_manifest import ArtifactManifest, ArtifactEntry

REPO_ROOT = Path(__file__).parent.parent
ARTIFACTS_ROOT = REPO_ROOT / "artifacts"
CONFIG_ROOT = REPO_ROOT / ".agentic-ci"


def load_profile() -> RepoProfile:
    path = CONFIG_ROOT / "repo-profile.yaml"
    data = yaml.safe_load(path.read_text())
    return RepoProfile(**data)


def load_review_packs() -> list[ReviewPack]:
    packs_dir = CONFIG_ROOT / "review-packs"
    packs = []
    for pack_file in sorted(packs_dir.glob("*.yaml")):
        data = yaml.safe_load(pack_file.read_text())
        packs.append(ReviewPack(**data))
    return packs


def clone_repo(source_path: Path, run_id: str) -> Path:
    temp_dir = Path(tempfile.mkdtemp(prefix=f"agentic-ci-{run_id[:8]}-"))
    subprocess.run(
        ["git", "clone", "--local", str(source_path), str(temp_dir)],
        check=True, capture_output=True
    )
    return temp_dir


def get_sha(repo_path: Path, ref: str) -> str:
    result = subprocess.run(
        ["git", "rev-parse", ref],
        cwd=repo_path, capture_output=True, text=True
    )
    return result.stdout.strip() if result.returncode == 0 else ref


def run_pipeline(repo_path: str, base_ref: str = "HEAD~1", head_ref: str = "HEAD"):
    run_id = f"run_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    source = Path(repo_path).resolve()

    artifacts_dir = ARTIFACTS_ROOT / run_id
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    state = RunStateMachine(run_id, artifacts_dir)
    clone_path = None

    print(f"\n{'='*55}")
    print(f"Agentic CI  |  Run: {run_id}")
    print(f"Target:     {source}")
    print(f"Diff:       {base_ref}...{head_ref}")
    print(f"{'='*55}\n")

    try:
        # PREFLIGHT
        state.transition(RunStage.PREFLIGHT, "in_progress")
        profile = load_profile()
        print(f"  Cloning repo to isolated workspace...")
        clone_path = clone_repo(source, run_id)

        ok, err = run_preflight(clone_path, profile)
        if not ok:
            print(f"  Warning: {err}")
        state.transition(RunStage.PREFLIGHT, "success")

        # DETERMINISTIC CHECKS
        state.transition(RunStage.DETERMINISTIC_CHECKS, "in_progress")
        ok, err = run_deterministic_checks(clone_path, profile)
        status = "success" if ok else "warning"
        if not ok:
            print(f"  Warning: {err}")
            print(f"  Continuing with review despite check failures.")
        state.transition(RunStage.DETERMINISTIC_CHECKS, status)

        # IMPACT MAPPING
        state.transition(RunStage.IMPACT_MAPPING, "in_progress")
        diff = compute_diff(clone_path, base_ref, head_ref)
        changed_files = get_changed_files(clone_path, base_ref, head_ref)
        print(f"  Changed files ({len(changed_files)}): {changed_files[:5]}")

        all_packs = load_review_packs()
        selected_packs = select_review_packs(changed_files, all_packs)

        # If diff only touched non-code files, review all tracked files
        if not selected_packs:
            print("  No packs matched diff — falling back to full repo review.")
            from agentic_ci.impact import get_changed_files as _gcf
            import subprocess as _sp
            all_files_result = _sp.run(
                ["git", "ls-files"], cwd=clone_path, capture_output=True, text=True
            )
            changed_files = [f.strip() for f in all_files_result.stdout.splitlines() if f.strip()]
            selected_packs = select_review_packs(changed_files, all_packs)

        print(f"  Review packs selected: {[p.id for p in selected_packs]}")
        file_contents = read_file_contents(clone_path, changed_files)
        state.transition(RunStage.IMPACT_MAPPING, "success", {
            "changed_files_count": len(changed_files),
            "packs_selected": [p.id for p in selected_packs],
        })

        # REVIEW
        state.transition(RunStage.REVIEW, "in_progress")
        raw_findings = []
        for pack in selected_packs:
            print(f"  Running reviewer: {pack.id}...")
            findings = run_reviewer(pack, diff, file_contents)
            print(f"    -> {len(findings)} findings")
            raw_findings.extend(findings)
        state.transition(RunStage.REVIEW, "success", {"raw_findings": len(raw_findings)})

        # NORMALIZE
        state.transition(RunStage.NORMALIZE_FINDINGS, "in_progress")
        findings = normalize_and_dedupe(raw_findings)
        findings = sort_findings(findings)
        print(f"  After dedup: {len(findings)} findings (from {len(raw_findings)} raw)")
        state.transition(RunStage.NORMALIZE_FINDINGS, "success", {
            "deduplicated_findings": len(findings)
        })

        # PUBLISH
        state.transition(RunStage.PUBLISH, "in_progress")
        base_sha = get_sha(clone_path, base_ref)
        head_sha = get_sha(clone_path, head_ref)

        findings_path = write_findings(artifacts_dir, findings)
        report_path = write_report(artifacts_dir, findings, run_id, source.name, base_ref, head_ref)

        manifest = ArtifactManifest(
            run_id=run_id,
            repo=source.name,
            base_ref=base_ref,
            head_ref=head_ref,
            base_sha=base_sha,
            head_sha=head_sha,
            status="completed",
            published_output_kind="report_only",
            artifacts=[
                ArtifactEntry(path="findings.json", sha256=sha256_file(findings_path)),
                ArtifactEntry(path="report.md", sha256=sha256_file(report_path)),
                ArtifactEntry(path="run-events.json"),
            ],
        )
        write_manifest(artifacts_dir, manifest)
        state.transition(RunStage.PUBLISH, "success")
        state.transition(RunStage.COMPLETED, "success")

        # Print summary
        by_sev = {s: sum(1 for f in findings if f.severity == s)
                  for s in ("critical", "high", "medium", "low")}
        print(f"\n{'='*55}")
        print(f"Run complete: {run_id}")
        print(f"Findings: {len(findings)}  |  "
              f"Critical: {by_sev['critical']}  High: {by_sev['high']}  "
              f"Medium: {by_sev['medium']}  Low: {by_sev['low']}")
        print(f"Artifacts: {artifacts_dir}")
        print(f"{'='*55}\n")

        return run_id, findings

    except Exception as e:
        state.fail(str(e))
        raise
    finally:
        if clone_path and clone_path.exists():
            shutil.rmtree(clone_path, ignore_errors=True)
