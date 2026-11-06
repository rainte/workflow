import importlib.util
import os
import sys
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).parent
ENTRY = "index.py"
MAX_WORKERS = int(os.environ.get("MAX_WORKERS", "4"))


def _load(path: Path):
    spec = importlib.util.spec_from_file_location(path.parent.name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _run_one(sub: Path) -> str:
    entry = sub / ENTRY
    if not entry.exists():
        return f"[skip] {sub.name}: no {ENTRY}"
    mod = _load(entry)
    if not hasattr(mod, "main"):
        raise RuntimeError(f"{entry} 缺少 main()")
    mod.main()
    return f"[ok] {sub.name}"


def main() -> None:
    dirs = sorted(p for p in ROOT.iterdir() if p.is_dir())
    failed: list[str] = []
    logs: dict[str, str] = {}

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(_run_one, d): d.name for d in dirs}
        for fut in as_completed(futures):
            name = futures[fut]
            try:
                logs[name] = fut.result()
            except Exception:
                logs[name] = "[fail]\n" + traceback.format_exc()
                failed.append(name)

    for name in sorted(logs):
        print(f"::group::{name}")
        print(logs[name].rstrip())
        print("::endgroup::")

    if failed:
        sys.exit(f"[error] failed: {', '.join(failed)}")


if __name__ == "__main__":
    main()
