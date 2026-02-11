<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Vinver, Inc. -->

# Governance

This document describes the governance model for the Vinver Boards project.

## Overview

Vinver Boards is maintained by Vinver, Inc. ("Vinver"). Vinver retains final
decision-making authority over the project's direction, roadmap, and releases.
Community contributions are welcome and encouraged under the terms of the
[Apache License 2.0](LICENSE) and [Contributor License Agreement](CLA-INDIVIDUAL.md).

## Roles

### Maintainers

Maintainers are Vinver employees or contractors with commit access to the
repository. They are responsible for:

- Reviewing and merging pull requests
- Triaging issues
- Maintaining the schema and validation tooling
- Publishing releases

Current maintainers are listed in [CODEOWNERS](CODEOWNERS).

### Core Team

The core team (`@vinver-ai/core`) has authority over:

- Schema changes (`schema/`)
- CI/CD workflows (`.github/`)
- Governance and licensing decisions

Changes to these areas require approval from at least one core team member.

### Contributors

Anyone who submits a pull request, opens an issue, or participates in
discussions is a contributor. Contributors must:

- Sign the [Individual CLA](CLA-INDIVIDUAL.md) (or have their employer sign
  the [Corporate CLA](CLA-CORPORATE.md))
- Follow the [Code of Conduct](CODE_OF_CONDUCT.md)
- Adhere to the [Contributing Guidelines](CONTRIBUTING.md)

## Decision Making

### Board Manifests

- **Volume-tier additions/corrections**: One maintainer approval required.
- **Gold-tier additions**: One core team member approval required, plus a link
  to the official schematic used for verification.
- **Gold-tier corrections**: Two maintainer approvals required to prevent
  regressions.

### Schema Changes

Schema changes affect all 370+ boards and the downstream SDK. These require:

1. An RFC-style issue describing the proposed change and its impact
2. A minimum 7-day comment period for community feedback
3. Approval from at least two core team members
4. A migration path for existing manifests

### Breaking Changes

Changes that would require modifications to existing board manifests or break
the SDK contract require:

1. A deprecation notice in the [CHANGELOG](CHANGELOG.md)
2. A major version bump to `manifest_version`
3. Core team approval

## Releases

Releases follow [Semantic Versioning](https://semver.org/):

- **Patch** (1.0.x): Board corrections, new volume-tier boards
- **Minor** (1.x.0): New driver types, new gold-tier boards, non-breaking
  schema additions
- **Major** (x.0.0): Breaking schema changes

## Reporting Issues

- **General issues**: [GitHub Issues](https://github.com/vinver-ai/boards/issues)
- **Incorrect pin mappings that may cause hardware issues**: security@vinver.ai
  (see [SECURITY.md](SECURITY.md))
- **Code of Conduct concerns**: conduct@vinver.ai

## Amendments

This governance document may be amended by the core team. Significant changes
will be announced via a GitHub Discussion or issue.
