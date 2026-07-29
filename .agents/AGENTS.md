# Project Guidelines & Rules for EL-STRIX

Welcome to the **EL-STRIX** repository guidelines. This document outlines the mandatory architecture patterns, code quality standards, and automated workflows required for developing and maintaining the EL-STRIX engine.

---

## 📌 1. Repository Purpose & Architecture

**EL-STRIX** is an automated engine designed to generate dynamic GitHub banners, stat cards, and profile README updates.

### Core Modules (`scripts/`)
- `main.py`: Entry point orchestrating the entire automated pipeline execution.
- `github.py`: Robust API wrapper for GitHub REST and GraphQL requests with error handling, rate limiting, and caching.
- `data_engine.py`: Orchestrates the fetching of all raw data from GitHub (commits, PRs, issues) and saves it to structured JSON.
- `stats.py`: Core statistics engine that processes raw JSON data into a single source of truth for all numerical values.
- `avatar_engine.py`: Handles image preprocessing, ASCII matrix generation, and dynamic avatar SVG rendering.
- `renderer.py`: Graphics engine rendering theme-aware light/dark SVG graphics for statistics and profile cards.
- `readme_engine.py`: Dynamic template processor that updates the README.md with live metrics.
- `automation.py`: Handles Git tracking, detecting file changes, and automated commits/pushes.
- `utils/`: Core utilities directory including JSON helpers, filesystem enforcement, logging, and environment management.

---

## ⚙️ 2. Git & Commit Workflow Rules

> [!IMPORTANT]
> **Mandatory Commit Policy**: Every completed feature, bug fix, refactor, or workspace task MUST culminate in a clean Git commit before ending the session.

- **Conventional Commits**: Format commit messages according to Conventional Commits standards:
  - `feat:` New features or generation capabilities
  - `fix:` Bug fixes or API error handling patches
  - `docs:` Documentation improvements
  - `style:` Formatting, layout, or SVG aesthetic adjustments
  - `refactor:` Code restructuring without functional changes
  - `test:` Adding or updating unit tests
  - `chore:` Maintenance, GitHub Actions updates, or dependency updates

- **Clean Working Tree**: Ensure temporary files, cache outputs, or build artifacts (other than `.gitkeep`) are never committed. Verify using `git status` prior to committing.

---

## 🐍 3. Python Code Quality & Design Patterns

1. **Code Style & Formatting**:
   - Adhere strictly to **PEP 8** standards.
   - Use explicit type annotations (`typing.Dict`, `typing.List`, `typing.Optional`) on function arguments and return types.
   - Ensure all public functions and classes contain clear docstrings.

2. **Error Handling & Resilience**:
   - Always handle network timeouts, rate limiting, and HTTP exceptions gracefully when calling external APIs (e.g., `requests.RequestException`).
   - Log errors informative using `utils.logger` without failing silently or crashing unhandled.

3. **Dependencies**:
   - Maintain minimal external dependencies in `requirements.txt` and `pyproject.toml`.
   - Use standard library modules whenever possible.

---

## 🎨 4. Asset & SVG Graphics Standards

- **Theme Support**: All generated banners must maintain dark and light theme parity (`assets/svg/light.svg` and `assets/svg/dark.svg`).
- **Responsive Layout**: Ensure SVG graphics specify flexible `viewBox` properties for seamless rendering across screen sizes.
- **Accessibility & Contrast**: Maintain high color contrast ratios and modern visual aesthetics.

---

## 🧪 5. Testing & Verification

- **Unit Testing**: All generator and renderer utility functions must have corresponding test coverage in `tests/`.
- **Validation**: Verify scripts compile cleanly without syntax errors (`python -m py_compile scripts/*.py`) and pass `pytest` before finalizing changes.

---

## 📚 6. Documentation Maintenance

- Keep `README.md` and documentation under `docs/` in sync whenever features or workflow commands are modified.

