# Contributing

Thanks for your interest in contributing to this project.

## Development setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
pip install -e .
```

3. Run tests:

```bash
python -m pytest src/horoscoop/tests -v
```

4. Run the app locally:

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

## Branching and pull requests

- Create a feature branch from `main`.
- Keep PRs focused and small when possible.
- Include tests for behavior changes.
- Update documentation when behavior or setup changes.

## Code style

- Follow existing project conventions.
- Keep functions deterministic and explicit where possible.
- Prefer clear naming and small, testable units.
- Astrological symbols/icons must use the central icon set (`/static/icons/astro`) via shared symbol helpers. Do not add new hardcoded unicode glyphs in rendering paths.

## Reporting issues

When opening an issue, include:

- What you expected to happen
- What happened instead
- Reproduction steps
- Relevant logs or tracebacks
