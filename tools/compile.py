#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Vinver, Inc.
"""
Compile TOML board manifests to MessagePack for the Vinver edge runtime.

Reads boards/*.toml, restructures nested sections, injects runtime defaults,
serializes to MessagePack, and writes output to dist/v1/.

Usage:
    python3 tools/compile.py                # compile all
    python3 tools/compile.py --dry-run      # validate without writing
    python3 tools/compile.py FILE...        # specific files
"""

import hashlib
import json
import sys
import tomllib
from datetime import date
from pathlib import Path

try:
    import msgpack
except ImportError:
    print("ERROR: msgpack not installed. Run: pip install 'msgpack>=1.0,<2'")
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
BOARDS_DIR = ROOT / "boards"
DIST_DIR = ROOT / "dist" / "v1"

RISCV_CHIPS = {"esp32c3", "esp32c6", "esp32h2", "esp32c5"}


def parse_flash_size_mb(s: str) -> int:
    s = s.strip().upper()
    if s.endswith("MB"):
        return int(s[:-2])
    return int(s)


def compute_runtime_defaults(chip: str, psram: bool, flash_size: str) -> dict:
    flash_mb = parse_flash_size_mb(flash_size)
    chip_lower = chip.lower()

    if chip_lower in RISCV_CHIPS:
        return {"heap_kb": 64, "stack_kb": 8, "native_stack_kb": 16}

    if not psram:
        return {"heap_kb": 64, "stack_kb": 8, "native_stack_kb": 16}

    if chip_lower == "esp32s3" and flash_mb >= 8:
        return {"heap_kb": 1024, "stack_kb": 32, "native_stack_kb": 32}

    if chip_lower == "esp32s3":
        return {"heap_kb": 512, "stack_kb": 16, "native_stack_kb": 24}

    # ESP32 / ESP32-S2 with PSRAM
    return {"heap_kb": 512, "stack_kb": 16, "native_stack_kb": 24}


def inject_runtime(data: dict) -> dict:
    if "runtime" in data:
        return data

    meta = data.get("meta", {})
    chip = meta.get("chip", "esp32")
    psram = meta.get("psram", False)
    flash_size = meta.get("flash_size", "4MB")

    data["runtime"] = compute_runtime_defaults(chip, psram, flash_size)
    return data


def restructure(data: dict) -> dict:
    result = {}
    drivers = {}
    custom = {}
    for key, val in data.items():
        if key.startswith("drivers.") and isinstance(val, dict):
            name = key.split(".", 1)[1]
            drivers[name] = val
        elif key.startswith("custom.") and isinstance(val, dict):
            name = key.split(".", 1)[1]
            custom[name] = val
        else:
            result[key] = val
    if drivers:
        result["drivers"] = drivers
    if custom:
        result["custom"] = custom
    return result


def compile_one(path: Path) -> tuple[bytes, bytes, dict]:
    with open(path, "rb") as f:
        raw_toml = f.read()

    data = tomllib.loads(raw_toml.decode())
    data = inject_runtime(data)
    data = restructure(data)

    packed = msgpack.packb(data, use_bin_type=True)

    # Round-trip verification
    unpacked = msgpack.unpackb(packed, raw=False)
    meta_id = unpacked.get("meta", {}).get("id", "")
    expected_id = path.stem
    if meta_id != expected_id:
        raise ValueError(
            f"{path.name}: round-trip failed: meta.id={meta_id!r} != {expected_id!r}"
        )

    entry = {
        "id": meta_id,
        "chip": unpacked.get("meta", {}).get("chip", ""),
        "description": unpacked.get("meta", {}).get("description", ""),
        "family": unpacked.get("meta", {}).get("family", ""),
        "tier": unpacked.get("meta", {}).get("tier", ""),
        "sha256_msgpack": hashlib.sha256(packed).hexdigest(),
        "sha256_toml": hashlib.sha256(raw_toml).hexdigest(),
    }

    return packed, raw_toml, entry


def compile_all(files: list[Path], dist_dir: Path, dry_run: bool) -> bool:
    index_entries = []
    errors = 0

    for path in sorted(files):
        try:
            packed, raw_toml, entry = compile_one(path)
        except Exception as e:
            print(f"ERROR: {path.name}: {e}")
            errors += 1
            continue

        index_entries.append(entry)

        if not dry_run:
            dist_dir.mkdir(parents=True, exist_ok=True)
            (dist_dir / f"{path.stem}.msgpack").write_bytes(packed)
            (dist_dir / f"{path.stem}.toml").write_bytes(raw_toml)

    if errors:
        print(f"\n{errors} file(s) failed to compile")
        return False

    index = {
        "version": str(date.today()),
        "schema_version": "1.0",
        "total": len(index_entries),
        "boards": sorted(index_entries, key=lambda e: e["id"]),
    }

    if not dry_run:
        dist_dir.mkdir(parents=True, exist_ok=True)
        (dist_dir / "index.json").write_text(
            json.dumps(index, indent=2, ensure_ascii=False) + "\n"
        )

    print(f"Compiled {len(index_entries)} boards ({errors} errors)")
    if dry_run:
        print("(dry-run: no files written)")

    return True


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    dry_run = "--dry-run" in sys.argv

    if args:
        files = [Path(a).resolve() for a in args]
    else:
        files = sorted(BOARDS_DIR.glob("*.toml"))

    if not files:
        print(f"No TOML files found in {BOARDS_DIR}")
        sys.exit(1)

    ok = compile_all(files, DIST_DIR, dry_run)
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
