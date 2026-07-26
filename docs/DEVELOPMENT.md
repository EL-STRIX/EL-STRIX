# Development Guide

Welcome to the development documentation for **EL-STRIX**.

## Prerequisites

- Python 3.10+
- `pip` package manager
- Git

## Setup & Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/EL-STRIX/EL-STRIX.git
   cd EL-STRIX
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running Locally

Run the main generator script locally:
```bash
python scripts/main.py
```

## Running Tests

Execute the unit test suite:
```bash
pytest
```
