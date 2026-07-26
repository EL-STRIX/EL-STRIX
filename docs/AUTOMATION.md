# Automation Guide

**EL-STRIX** utilizes GitHub Actions for continuous automation, dynamic banner updates, linting, and security audits.

## Workflows Overview

- **Profile Update (`.github/workflows/profile.yml`)**:
  - Automatically fetches updated GitHub profile statistics and re-generates dynamic banner assets (`light.svg`, `dark.svg`).
  - Runs on a scheduled cron job (every 12 hours) and on manual dispatch.

- **Linter (`.github/workflows/lint.yml`)**:
  - Automatically checks Python, Markdown, and YAML file formatting on push and PR.

- **Security Scanning (`.github/workflows/security.yml`)**:
  - Runs GitHub CodeQL analysis for Python vulnerability scanning.

- **Release Automation (`.github/workflows/release.yml`)**:
  - Automatically creates GitHub releases when new `v*` tags are pushed.

## Environment Secrets

- `GH_TOKEN` or `GITHUB_TOKEN`: Read/Write access token for fetching statistics and committing generated assets back to the repo.
