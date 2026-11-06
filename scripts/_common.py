import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Callable
from urllib.request import Request, urlopen


def fetch_gist_file(gist_id: str, filename: str) -> str:
    req = Request(
        f"https://api.github.com/gists/{gist_id}",
        headers={
            "Authorization": f"Bearer {os.environ["GIST_TOKEN"]}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2026-03-10",
        },
    )
    with urlopen(req, timeout=30) as resp:
        files = json.load(resp).get("files", {})
    if filename not in files:
        raise KeyError(f"gist {gist_id} 中找不到 {filename}，现有: {list(files)}")
    return files[filename]["content"]


def _git(work: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=work, check=check, text=True, capture_output=True
    )


def _clone(work: Path, repo: str) -> None:
    if work.exists():
        shutil.rmtree(work)
    subprocess.run(
        [
            "git", "clone",
            f"https://x-access-token:{os.environ["GIT_TOKEN"]}@github.com/{repo}.git",
            "-b", "main", "--depth", "1", str(work),
        ],
        check=True,
    )


def run_task(
    *,
    task: str,
    target_repo: str,
    mutate: Callable[[Path], None],
) -> None:
    work = Path(f"target-repo-{task}")

    _clone(work, target_repo)
    mutate(work)

    _git(work, "add", "-A")

    commit = _git(work, "commit", "-m", "commit", check=False)
    if commit.returncode != 0:
        if "nothing to commit" in commit.stdout + commit.stderr:
            print(f"[{task}] no changes")
            return
        raise RuntimeError(f"[{task}] git commit failed:\n{commit.stderr}")

    _git(work, "push")
    print(f"[{task}] pushed")
