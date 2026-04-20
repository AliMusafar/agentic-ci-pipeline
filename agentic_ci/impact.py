import subprocess
import fnmatch
from pathlib import Path
from typing import List
from schemas.review_pack import ReviewPack


def _run_git(args: list, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        args, cwd=cwd, capture_output=True,
        text=True, encoding="utf-8", errors="replace"
    )


def compute_diff(repo_path: Path, base_ref: str, head_ref: str) -> str:
    result = _run_git(["git", "diff", f"{base_ref}...{head_ref}"], repo_path)
    if result.returncode == 0 and result.stdout and result.stdout.strip():
        return result.stdout

    # Fallback: uncommitted changes
    result = _run_git(["git", "diff", "HEAD"], repo_path)
    return result.stdout or ""


def get_changed_files(repo_path: Path, base_ref: str, head_ref: str) -> List[str]:
    result = _run_git(["git", "diff", "--name-only", f"{base_ref}...{head_ref}"], repo_path)
    if result.returncode == 0 and result.stdout and result.stdout.strip():
        return [f.strip() for f in result.stdout.splitlines() if f.strip()]

    # Fallback: uncommitted changes
    result = _run_git(["git", "diff", "--name-only", "HEAD"], repo_path)
    if result.stdout and result.stdout.strip():
        return [f.strip() for f in result.stdout.splitlines() if f.strip()]

    # Final fallback: all tracked files
    result = _run_git(["git", "ls-files"], repo_path)
    return [f.strip() for f in (result.stdout or "").splitlines() if f.strip()]


def select_review_packs(changed_files: List[str], all_packs: List[ReviewPack]) -> List[ReviewPack]:
    selected = []
    for pack in all_packs:
        for f in changed_files:
            if _matches_pack(f, pack):
                selected.append(pack)
                break
    return selected


def _matches_pack(filepath: str, pack: ReviewPack) -> bool:
    for pattern in pack.scope_selector.include_paths:
        if pattern == "**":
            return True
        if fnmatch.fnmatch(filepath, pattern):
            return True
        if fnmatch.fnmatch(Path(filepath).name, pattern.lstrip("**/").lstrip("**/")):
            return True
    return False


def read_file_contents(repo_path: Path, files: List[str], max_bytes: int = 8000) -> dict:
    contents = {}
    for f in files:
        fpath = repo_path / f
        if fpath.exists() and fpath.is_file():
            try:
                text = fpath.read_text(encoding="utf-8", errors="replace")
                contents[f] = text[:max_bytes]
            except Exception:
                contents[f] = "[unreadable]"
    return contents
