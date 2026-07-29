# 🏛️ Architecture Overview

Curious about how EL-STRIX works under the hood? You're in the right place!

EL-STRIX is designed as a highly modular, automated engine. Instead of a single messy script, the workload is divided into specialized modules. This makes it easy to maintain, scale, and debug.

Here is the journey of how your data becomes a beautiful GitHub banner.

## 🔄 The Generation Pipeline

When the engine runs (via GitHub Actions or locally), it follows a strict, step-by-step pipeline orchestrated by `scripts/main.py`.

### 1. Data Collection (`data_engine.py` & `github.py`)
Everything starts with data.
- **`github.py`**: This acts as our secure gateway to GitHub. It handles all API requests (both REST and GraphQL), manages rate limits, and safely uses your `EL_STRIX_TOKEN`.
- **`data_engine.py`**: This module asks for your commits, PRs, issues, and repository data, pulling everything down and saving it as raw JSON.

### 2. Number Crunching (`stats.py`)
Raw data isn't very pretty.
- **`stats.py`**: The "brain" of the operation. It processes the raw JSON, calculates your total contributions, finds your most used languages, and determines your current GitHub rank. It creates the final "source of truth" dataset.

### 3. Visual Magic (`renderer.py` & `avatar_engine.py`)
Time to make things look good.
- **`renderer.py`**: This is the graphics engine. It takes the statistics and your `profile.json` config, and renders pixel-perfect SVG banners in both light and dark themes.
- **`avatar_engine.py`**: Specifically handles fetching your GitHub profile picture, processing it, and turning it into those awesome ASCII/Matrix style avatars.

### 4. Updating the Profile (`readme_engine.py`)
Now that the images are generated, they need to be displayed.
- **`readme_engine.py`**: This reads your `templates/README.template.md`, injects the fresh live metrics and dynamic SVG links, and saves it as your final `README.md`.

### 5. Deployment (`automation.py`)
The final touch.
- **`automation.py`**: It tracks all the files that were modified during the run. If things changed, it automatically creates a clean Git commit (using Conventional Commits) and pushes the updates directly to your repository so the world can see them.

---

### 🧩 Utilities & Config
Throughout this process, the engine relies on:
- **`config_loader.py`**: To read your preferences.
- **`cache_manager.py`**: To speed up execution by caching older data.
- **`logger.py`**: To print beautiful, readable logs to the terminal so you always know what the engine is doing.
