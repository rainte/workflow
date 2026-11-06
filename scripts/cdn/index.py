import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from _common import run_task
from singbox import Singbox


def main() -> None:
    sb = Singbox()
    run_task(
        task=Path(__file__).parent.name,
        target_repo=f"{os.environ["OWNER"]}/{Path(__file__).parent.name}",
        mutate=sb.mutate,
    )
