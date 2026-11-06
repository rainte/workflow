import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _common import fetch_gist_file, run_task


def main() -> None:
    gist_id = os.environ["GIST_ID"]

    def mutate(work: Path) -> None:
        raw = fetch_gist_file(gist_id, "bookmark.json")
        res = json.loads(raw)["children"][::-1]
        out = work / "docs" / "bookmark.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(res), encoding="utf-8")

    run_task(
        task=Path(__file__).parent.name,
        target_repo=f"{os.environ["OWNER"]}/{Path(__file__).parent.name}",
        mutate=mutate,
    )
