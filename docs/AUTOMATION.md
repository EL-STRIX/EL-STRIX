# ⚙️ Automation Guide

**EL-STRIX** runs completely hands-off once configured. It utilizes GitHub Actions to continuously update your profile statistics, render new banners, and commit those changes directly back to the repository.

## 🔄 Active Workflows

Currently, the engine relies on a single, powerful workflow to handle everything.

### Profile Update (`.github/workflows/profile.yml`)
This is the core automation script. 
- **What it does**: It spins up an Ubuntu runner, installs the necessary Python dependencies, and executes the entire EL-STRIX generation pipeline (`scripts/main.py`). After generating the new assets (`light.svg`, `dark.svg`), it automatically commits and pushes the updated graphics and `README.md` to your repository.
- **When it runs**: 
  - Automatically runs every 24 hours (at midnight UTC) via a cron job.
  - Automatically runs whenever you push changes to the `main` branch (excluding documentation changes).
  - Can be triggered manually at any time via the GitHub Actions tab (`workflow_dispatch`).

## 🔐 Required Environment Secrets

To allow the automation to fetch statistics and push changes back to your repository, you need to provide a token.

- **`EL_STRIX_TOKEN`**: You must create a classic Personal Access Token (PAT) with `repo` and `workflow` permissions and save it in your repository secrets as `EL_STRIX_TOKEN`. This token allows the engine to securely fetch your latest commit data across all your repositories and push the generated SVGs back to this repo.

If `EL_STRIX_TOKEN` is not found, the workflow will gracefully fall back to the default `GITHUB_TOKEN`, though this may limit its ability to fetch data from your private repositories depending on your settings.
