<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Vinver, Inc. -->

## Summary

<!-- Brief description of changes -->

## Checklist

- [ ] `meta.id` matches the filename (without `.toml`)
- [ ] `meta.chip` is correct for this board
- [ ] `meta.tier` is set (`volume` or `gold`)
- [ ] Every `[drivers.*]` section has a matching `[capabilities]` entry
- [ ] Every `[custom.*]` section has a matching `[capabilities]` entry with `type = "custom"`
- [ ] `python3 tools/validate.py` passes with 0 issues
- [ ] Source link provided (schematic, header file, or product page)
