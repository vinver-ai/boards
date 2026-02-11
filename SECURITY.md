<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Vinver, Inc. -->

# Security Policy

## Reporting Incorrect Pin Mappings

Incorrect pin mappings can cause hardware damage (e.g., driving a strapping pin, shorting a power rail). We treat confirmed incorrect mappings as **security-level issues**.

### How to Report

1. **Public reports** (non-dangerous errors): Open a [bug report](https://github.com/vinver-ai/boards/issues/new?template=bug_report.yml).
2. **Dangerous mappings** (could damage hardware): Email **security@vinver.ai** with:
   - Board ID and filename
   - The incorrect field(s) and expected correct value(s)
   - How you verified the correct mapping (schematic, datasheet, physical board)

We will acknowledge reports within 48 hours and aim to publish a corrected manifest within 7 days.

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.x     | Yes       |

## Scope

This policy covers:

- Board manifest data in `boards/`
- Schema definitions in `schema/`
- Validation tooling in `tools/`

For issues with the Vinver SDK or runtime, please refer to the respective repository's security policy.
