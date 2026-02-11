<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Vinver, Inc. -->

# Contributing to Vinver Boards

Thank you for helping improve the ESP32 board database!

## Contributor License Agreement

All contributors must sign a Contributor License Agreement (CLA) before their
first pull request can be merged. The CLA bot will automatically prompt you
when you open a PR.

- **Individuals**: Sign the [Individual CLA](CLA-INDIVIDUAL.md) by commenting
  on your PR as instructed by the bot.
- **Corporations**: Have your company execute the
  [Corporate CLA](CLA-CORPORATE.md) by emailing a signed copy to
  legal@vinver.ai.

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md).
By participating, you agree to uphold its terms.

## How to Contribute

### Correcting an Existing Board

1. Open an issue using the **Bug Report** template describing the incorrect pin mapping
2. Fork the repo and edit the TOML file in `boards/`
3. Run the validator: `python3 tools/validate.py`
4. Submit a PR using the pull request template

### Adding a New Board

1. Open an issue using the **New Board** template
2. Copy an existing TOML from `boards/` for a similar board as your starting point
3. Fill in all sections: `[meta]`, `[system]`, `[capabilities]`, and relevant `[drivers.*]`
4. Ensure `meta.id` matches the filename (without `.toml`)
5. Run the validator: `python3 tools/validate.py`
6. Submit a PR

### Requesting a New Driver Type

If your board has a peripheral not covered by the 18 standard drivers, open a
**Feature Request** issue. In the meantime, use `[custom.*]` sections as an
escape hatch.

## Schema Reference

See [`schema/`](schema/) for the full TOML template and field documentation.

## Quality Tiers

| Tier     | Source                        | Promotion Path                  |
|----------|-------------------------------|---------------------------------|
| `volume` | Auto-extracted from headers   | Verified against schematic      |
| `gold`   | Verified against schematics   | —                               |

To promote a `volume` board to `gold`, open a PR with:
- The corrected TOML with `tier = "gold"`
- A link to the official schematic used for verification

## Guidelines

- One TOML file per board variant
- Filenames use the Arduino variant directory name (e.g., `esp32s3_devkitc_1.toml`)
- All pin values must be valid GPIO numbers for the board's chip
- Every `[drivers.*]` section must have a corresponding `[capabilities]` entry
- Custom sections must have a `type` field
- Run `python3 tools/validate.py` before submitting — CI will reject PRs that fail

## License

By contributing, you agree that your contributions will be licensed under the
Apache License 2.0. This is formalized through the
[Contributor License Agreement](CLA-INDIVIDUAL.md) that all contributors must
sign.
