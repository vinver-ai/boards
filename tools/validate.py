#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Vinver, Inc.
"""
TOML board manifest validator.

Checks all .toml files in boards/ against the schema rules:
- Capability/driver consistency
- Pin-based capability presence
- Custom section promotion hints
- Legacy field detection
- meta.id <-> filename match

Usage:
    python3 tools/validate.py              # validate all boards
    python3 tools/validate.py FILE...      # validate specific files
"""

import sys
import tomllib
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parent.parent
BOARDS_DIR = ROOT / "boards"

# ─── Standard driver -> capability type mapping ───────────────────────
DRIVER_CAP_TYPE = {
    "drivers.neopixel":   "rgb_led",
    "drivers.display":    "display",
    "drivers.camera":     "camera",
    "drivers.audio":      "audio",
    "drivers.touch":      "touch",
    "drivers.lora":       "lora",
    "drivers.gps":        "gps",
    "drivers.pmu":        "pmu",
    "drivers.sdcard":     "sdcard",
    "drivers.ethernet":   "ethernet",
    "drivers.can":        "can",
    "drivers.rs485":      "rs485",
    "drivers.nfc":        "nfc",
    "drivers.imu":        "imu",
    "drivers.rtc":        "rtc",
    "drivers.env_sensor": "env_sensor",
    "drivers.ir":         "ir",
    "drivers.wifi_halow": "wifi_halow",
}

# ─── Pin-based capability rules ──────────────────────────────────────
PIN_CAP_RULES = {
    "led_pin":    ("led",    "led"),
    "button_pin": ("button", "button"),
    "buzzer_pin": ("buzzer", "buzzer"),
    "dac1_pin":   ("dac1",   "dac"),
    "dac2_pin":   ("dac2",   "dac"),
}

# ─── CUSTOM_SHOULD_BE_DRIVER detection ───────────────────────────────
IC_TO_DRIVER = {}
for ic in ("bma423", "mpu6050", "lsm6ds3", "bmi270", "qmi8658", "lis3dh"):
    IC_TO_DRIVER[ic] = "drivers.imu"
for ic in ("pcf8563", "ds3231", "rv3028"):
    IC_TO_DRIVER[ic] = "drivers.rtc"
for ic in ("bme280", "sht30", "bmp280", "aht20", "dht22", "sht40"):
    IC_TO_DRIVER[ic] = "drivers.env_sensor"
for ic in ("ir_tx", "ir_rx", "ir"):
    IC_TO_DRIVER[ic] = "drivers.ir"

NAME_TO_DRIVER = {
    "accelerometer":   "drivers.imu",
    "gyroscope":       "drivers.imu",
    "imu":             "drivers.imu",
    "rtc":             "drivers.rtc",
    "real_time_clock": "drivers.rtc",
    "temperature":     "drivers.env_sensor",
    "humidity":        "drivers.env_sensor",
    "barometer":       "drivers.env_sensor",
    "env_sensor":      "drivers.env_sensor",
    "ir_transmitter":  "drivers.ir",
    "ir_receiver":     "drivers.ir",
    "ir":              "drivers.ir",
}


def collect_toml_files(args: list[str]) -> list[Path]:
    """Collect TOML files from CLI args or default to boards/ directory."""
    if args:
        return [Path(a).resolve() for a in args]
    return sorted(BOARDS_DIR.rglob("*.toml"))


def validate_file(path: Path) -> list[tuple[str, str]]:
    """Validate one TOML file. Returns list of (ISSUE_TYPE, description)."""
    issues: list[tuple[str, str]] = []

    try:
        with open(path, "rb") as f:
            data = tomllib.load(f)
    except Exception as e:
        issues.append(("PARSE_ERROR", str(e)))
        return issues

    # ── CHECK 0: meta.id <-> filename match ───────────────────────────
    meta = data.get("meta", {})
    expected_id = path.stem
    actual_id = meta.get("id", "")
    if actual_id and actual_id != expected_id:
        issues.append((
            "ID_FILENAME_MISMATCH",
            f'meta.id="{actual_id}" does not match filename "{path.name}"'
        ))

    caps = data.get("capabilities", {})
    system = data.get("system", {})

    cap_by_driver: dict[str, list[tuple[str, str]]] = {}
    cap_by_pin: dict[str, list[tuple[str, str]]] = {}

    for cap_name, cap_val in caps.items():
        if not isinstance(cap_val, dict):
            continue
        cap_type = cap_val.get("type", "")
        if "driver" in cap_val:
            drv = cap_val["driver"]
            cap_by_driver.setdefault(drv, []).append((cap_name, cap_type))
        if "pin" in cap_val:
            pin = cap_val["pin"]
            cap_by_pin.setdefault(pin, []).append((cap_name, cap_type))

    driver_sections: set[str] = set()
    custom_sections: dict[str, dict] = {}

    for key, val in data.items():
        if key.startswith("drivers.") and isinstance(val, dict):
            driver_sections.add(key)
        elif key.startswith("custom.") and isinstance(val, dict):
            custom_sections[key] = val

    # ── CHECK 1: MISSING_CAP_FOR_DRIVER ───────────────────────────────
    for drv in sorted(driver_sections):
        if drv not in cap_by_driver:
            issues.append((
                "MISSING_CAP_FOR_DRIVER",
                f'["{drv}"] section exists but no capability references it'
            ))

    # ── CHECK 2: MISSING_CAP_FOR_CUSTOM ───────────────────────────────
    for cust in sorted(custom_sections):
        if cust not in cap_by_driver:
            issues.append((
                "MISSING_CAP_FOR_CUSTOM",
                f'["{cust}"] section exists but no capability references it'
            ))

    # ── CHECK 3: CUSTOM_SHOULD_BE_DRIVER ──────────────────────────────
    for cust, cust_data in sorted(custom_sections.items()):
        cust_type = cust_data.get("type", "")
        short_name = cust.split(".", 1)[1] if "." in cust else cust

        if cust_type.lower() in IC_TO_DRIVER:
            target = IC_TO_DRIVER[cust_type.lower()]
            issues.append((
                "CUSTOM_SHOULD_BE_DRIVER",
                f'["{cust}"] type="{cust_type}" should be [{target}]'
            ))
        elif short_name.lower() in NAME_TO_DRIVER:
            target = NAME_TO_DRIVER[short_name.lower()]
            issues.append((
                "CUSTOM_SHOULD_BE_DRIVER",
                f'["{cust}"] name "{short_name}" suggests it should be [{target}]'
            ))

    # ── CHECK 4: WRONG_CAP_TYPE ───────────────────────────────────────
    for cap_name, cap_val in caps.items():
        if not isinstance(cap_val, dict):
            continue
        cap_type = cap_val.get("type", "")
        drv = cap_val.get("driver", "")

        if drv in DRIVER_CAP_TYPE:
            expected = DRIVER_CAP_TYPE[drv]
            if cap_type != expected:
                issues.append((
                    "WRONG_CAP_TYPE",
                    f'capabilities.{cap_name} references {drv} with type="{cap_type}", '
                    f'expected type="{expected}"'
                ))
        elif drv.startswith("custom."):
            if cap_type != "custom":
                issues.append((
                    "WRONG_CAP_TYPE",
                    f'capabilities.{cap_name} references {drv} with type="{cap_type}", '
                    f'expected type="custom"'
                ))

    # ── CHECK 5: ORPHAN_CAP ───────────────────────────────────────────
    for cap_name, cap_val in caps.items():
        if not isinstance(cap_val, dict):
            continue
        drv = cap_val.get("driver", "")
        if drv.startswith("drivers.") and drv not in driver_sections:
            issues.append((
                "ORPHAN_CAP",
                f'capabilities.{cap_name} references "{drv}" but no [{drv}] section exists'
            ))
        elif drv.startswith("custom.") and drv not in custom_sections:
            issues.append((
                "ORPHAN_CAP",
                f'capabilities.{cap_name} references "{drv}" but no [{drv}] section exists'
            ))

    # ── CHECK 6: MISSING_PIN_CAP ──────────────────────────────────────
    for sys_field, (expected_cap_name, expected_cap_type) in PIN_CAP_RULES.items():
        if sys_field in system:
            pin_val = system[sys_field]
            if pin_val == -1:
                continue
            pin_path = f"system.{sys_field}"
            if pin_path not in cap_by_pin:
                issues.append((
                    "MISSING_PIN_CAP",
                    f'system.{sys_field}={pin_val} exists but no capability '
                    f'references pin="system.{sys_field}"'
                ))

    # ── CHECK 7: LEGACY_FIELD ─────────────────────────────────────────
    for drv_name in sorted(driver_sections):
        drv_data = data.get(drv_name, {})
        short = drv_name.split(".", 1)[1] if "." in drv_name else drv_name

        if short in ("touch", "imu", "rtc", "nfc", "ethernet"):
            if "int" in drv_data and "irq" not in drv_data:
                issues.append((
                    "LEGACY_FIELD",
                    f'["{drv_name}"] has "int" -- should be "irq"'
                ))

        if short == "neopixel":
            if "count" in drv_data and "num_leds" not in drv_data:
                issues.append((
                    "LEGACY_FIELD",
                    f'["{drv_name}"] has "count" -- should be "num_leds"'
                ))

        if short in ("display", "sdcard", "ethernet"):
            if "power" in drv_data and "power_pin" not in drv_data:
                issues.append((
                    "LEGACY_FIELD",
                    f'["{drv_name}"] has "power" -- should be "power_pin"'
                ))

        if short == "display":
            if "address" in drv_data and "addr" not in drv_data:
                issues.append((
                    "LEGACY_FIELD",
                    f'["{drv_name}"] has "address" -- should be "addr"'
                ))

    return issues


def main():
    files = collect_toml_files(sys.argv[1:])
    if not files:
        print("No TOML files found in", BOARDS_DIR)
        sys.exit(1)

    issue_counter: Counter[str] = Counter()
    files_with_issues = 0

    results: list[tuple[Path, list[tuple[str, str]]]] = []
    for path in files:
        issues = validate_file(path)
        results.append((path, issues))
        if issues:
            files_with_issues += 1
            for issue_type, _ in issues:
                issue_counter[issue_type] += 1

    for path, issues in results:
        if not issues:
            continue
        relpath = path.relative_to(ROOT)
        print(f"=== {relpath} ===")
        for issue_type, desc in issues:
            print(f"  [{issue_type}] {desc}")
        print()

    all_types = [
        "ID_FILENAME_MISMATCH",
        "MISSING_CAP_FOR_DRIVER",
        "MISSING_CAP_FOR_CUSTOM",
        "CUSTOM_SHOULD_BE_DRIVER",
        "WRONG_CAP_TYPE",
        "ORPHAN_CAP",
        "MISSING_PIN_CAP",
        "LEGACY_FIELD",
    ]

    print("SUMMARY:")
    print(f"  Total files checked: {len(files)}")
    print(f"  Files with issues: {files_with_issues}")
    for t in all_types:
        print(f"  {t}: {issue_counter.get(t, 0)}")

    if files_with_issues > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
