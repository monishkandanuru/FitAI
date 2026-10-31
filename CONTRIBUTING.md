# Contributing to FitAI

Thank you for contributing to **FitAI — AI Powered Fitness & Nutrition Coach**!

## Development Workflow

1. **Fork & Clone** the repository:
   ```bash
   git clone https://github.com/monishkandanuru/FitAI.git
   cd FitAI
   ```
2. **Branching Strategy**:
   - Create feature branches from `develop` (`git checkout -b feature/your-feature develop`).
   - Keep modules self-contained (`routes/`, `models/`, `utils/`, `templates/`).
   - Never commit `.env` secrets, virtual environments (`venv/`), or local SQLite database files (`*.db`).
3. **Run Automated Checks Before Submitting a PR**:
   ```bash
   ./venv/bin/python -m unittest discover -s tests -v
   ./venv/bin/python build.py
   ```
4. **Pull Requests**:
   - Open pull requests against `develop`, then merge verified releases to `main` for Vercel production deployment.
