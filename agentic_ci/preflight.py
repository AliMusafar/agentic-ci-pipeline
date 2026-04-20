import subprocess
from pathlib import Path
from schemas.repo_profile import RepoProfile


def run_preflight(repo_clone_path: Path, profile: RepoProfile) -> tuple[bool, str]:
    for cmd in profile.commands.preflight:
        result = subprocess.run(
            cmd, shell=True, cwd=repo_clone_path,
            capture_output=True, text=True
        )
        if result.returncode != 0:
            return False, f"Preflight failed: {cmd}\n{result.stderr}"
    return True, ""


def run_deterministic_checks(repo_clone_path: Path, profile: RepoProfile) -> tuple[bool, str]:
    for cmd in profile.commands.deterministic_checks:
        result = subprocess.run(
            cmd, shell=True, cwd=repo_clone_path,
            capture_output=True, text=True
        )
        if result.returncode != 0:
            return False, f"Check failed: {cmd}\nstdout: {result.stdout}\nstderr: {result.stderr}"
    return True, ""
