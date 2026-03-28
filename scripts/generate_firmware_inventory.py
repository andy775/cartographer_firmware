#!/usr/bin/env python3
"""Walk firmware/ and write a CSV of every file path (for inventory / tooling)."""

from __future__ import annotations

import csv
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
FIRMWARE_DIR = REPO_ROOT / "firmware"
OUT_DEFAULT = REPO_ROOT / "firmware" / "firmware_inventory.csv"

FIRMWARE_EXT = frozenset({".bin", ".hex", ".elf", ".uf2", ".dfu"})


def family_from_rel(rel_to_repo: Path) -> str:
    parts = rel_to_repo.parts
    if len(parts) >= 2 and parts[0] == "firmware":
        parts = parts[1:]
    if not parts:
        return ""
    top = parts[0]
    if top == "v4":
        return "v4"
    if top == "v2-v3":
        return "v2-v3"
    return top


def main() -> None:
    if not FIRMWARE_DIR.is_dir():
        raise SystemExit(f"Missing directory: {FIRMWARE_DIR}")

    rows: list[dict[str, str | int]] = []
    for p in sorted(FIRMWARE_DIR.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(REPO_ROOT)
        st = p.stat()
        ext = p.suffix.lower()
        kind = "firmware_binary" if ext in FIRMWARE_EXT else "other"
        rows.append(
            {
                "relative_path": str(rel).replace("\\", "/"),
                "filename": p.name,
                "extension": ext or "",
                "size_bytes": st.st_size,
                "kind": kind,
                "family": family_from_rel(rel),
            }
        )

    OUT_DEFAULT.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "relative_path",
        "filename",
        "extension",
        "size_bytes",
        "kind",
        "family",
    ]
    with OUT_DEFAULT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    print(f"Wrote {len(rows)} rows to {OUT_DEFAULT}")


if __name__ == "__main__":
    main()
