<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Vinver, Inc. -->

# Vinver Boards

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Boards](https://img.shields.io/badge/boards-370-green.svg)](boards/)
[![Gold](https://img.shields.io/badge/gold-32-gold.svg)](boards/)
[![CI](https://github.com/vinver-ai/boards/actions/workflows/validate.yml/badge.svg)](https://github.com/vinver-ai/boards/actions/workflows/validate.yml)
[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/vinver-ai/boards/badge)](https://securityscorecards.dev/viewer/?uri=github.com/vinver-ai/boards)

Machine-readable TOML manifests for 370 ESP32 board variants. Each file
describes pin mappings, bus configurations, peripheral drivers, and
capabilities for one board.

## Quick Start

```toml
[meta]
id = "esp32s3"
family = "esp32"
description = "Espressif ESP32-S3-DevKitC-1"
chip = "esp32s3"
flash_size = "8MB"
psram = true
tier = "gold"
manifest_version = "1.0"
min_runtime_version = "1.0"

[capabilities]
led     = {pin = "system.led_pin", type = "led"}
display = {driver = "drivers.display", type = "display"}

[system]
led_pin = 48
button_pin = 0

[system.i2c]
sda = 8
scl = 9

["drivers.display"]
type = "ssd1306"
bus  = "i2c"
addr = 0x3C
width = 128
height = 64
```

## Board Count

| Chip     | Boards |
|----------|--------|
| ESP32    | 136    |
| ESP32-S3 | 142    |
| ESP32-S2 | 42     |
| ESP32-C3 | 27     |
| ESP32-C6 | 20     |
| ESP32-H2 | 3      |
| **Total**| **370**|

## Quality Tiers

| Tier     | Count | Source                                                 |
|----------|-------|--------------------------------------------------------|
| `volume` | 338   | Auto-extracted from Arduino `pins_arduino.h` headers   |
| `gold`   | 32    | Verified against official board schematics              |

Gold manifests are cross-validated against PDF schematics and supersede their
volume counterparts when both exist.

## Schema

Each manifest has four layers:

1. **`[meta]`** — Board identity, chip type, flash/PSRAM, quality tier
2. **`[capabilities]`** — SDK index mapping names to pins or drivers
3. **`[system]`** — Core GPIOs, buses (I2C/SPI/UART), power sensing, buttons
4. **`[drivers.*]`** — 18 standard peripheral drivers (display, LoRa, GPS, camera, etc.)
5. **`[custom.*]`** — Escape hatch for unlisted peripherals

See [`schema/`](schema/) for the full reference template and field documentation.

## Validation

```bash
python3 tools/validate.py
```

Requires Python 3.11+ (uses `tomllib` from stdlib, zero dependencies).

Validate a single file:

```bash
python3 tools/validate.py boards/esp32s3.toml
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on adding or correcting
board manifests.

## Disclaimer

Pin mappings are provided for reference only. Always verify against official
schematics and datasheets before connecting hardware. Vinver, Inc. is not
liable for hardware damage resulting from incorrect or outdated pin data.
See [LICENSE](LICENSE) Sections 7 and 8 for the full warranty disclaimer and
limitation of liability.

## Trademarks

Board names and product names referenced in this repository (including but not
limited to Espressif, ESP32, Adafruit, M5Stack, LilyGo, TTGO, Heltec,
SparkFun, Seeed Studio, and Olimex) are trademarks of their respective owners.
Vinver, Inc. is not affiliated with or endorsed by these companies. Use of
these names is solely for identification and interoperability purposes.

## License

Apache License 2.0 — see [LICENSE](LICENSE) and [NOTICE](NOTICE).
