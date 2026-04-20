import os
import sys
from dotenv import load_dotenv

load_dotenv()

from agentic_ci.run import run_pipeline

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Agentic CI Pipeline")
    parser.add_argument("--repo", default=".", help="Path to target git repo")
    parser.add_argument("--base", default="HEAD~1", help="Base ref for diff (default: HEAD~1)")
    parser.add_argument("--head", default="HEAD", help="Head ref for diff (default: HEAD)")
    args = parser.parse_args()

    if not os.getenv("LLM_API_KEY"):
        sys.exit("ERROR: Set LLM_API_KEY in your .env file before running.")

    run_pipeline(repo_path=args.repo, base_ref=args.base, head_ref=args.head)
