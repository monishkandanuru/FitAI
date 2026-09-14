# FitAI

A Python/Flask fitness journal with account authentication, an adult BMI calculator,
measurement history, workout and meal logging, and a dashboard backed by saved data.

All server logic, calculations, database access, and deployment build steps run in
Python. The browser uses HTML/CSS and a small amount of JavaScript for interactions.
No Node.js build is required. AI coaching and automatic meal recognition are not
implemented; journal entries are user supplied.

## Run locally

Python 3.12 or 3.13:

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
python app.py
```

Visit http://localhost:5000. SQLite tables are created automatically for development.
Set a stable `SECRET_KEY` in `.env` to retain sessions across server restarts. Without
one, development generates a random key at startup. Debug mode is disabled by default.

## Test

```sh
python -m pytest -q
python -m pip check
python build.py
```

GitHub Actions runs tests on Python 3.12 and 3.13, plus a PostgreSQL integration test.
Tests use isolated databases and do not change real accounts.

## Deploy to Vercel

1. Import the existing GitHub repository `monishkandanuru/FitAI` into Vercel, or use
   its existing project if already connected. Select Flask and repository root.
2. Connect a persistent PostgreSQL database. Set `DATABASE_URL` to the provider's
   connection URL (with its required TLS settings). `postgres://` and `postgresql://`
   are normalized to the psycopg driver automatically.
3. Set `FLASK_ENV=production` and a cryptographically random `SECRET_KEY` of at least
   32 characters. Generate it locally with `python -c 'import secrets; print(secrets.token_hex(32))'`.
   Store secrets in Vercel environment settings, never in GitHub source.
4. Initialize the database once from a trusted terminal with the same production
   environment variables: `python -m flask --app app init-db`. This creates missing
   tables without deleting existing rows. Back up existing data before future schema
   changes; this command is not a migration system.
5. Deploy. `pyproject.toml` selects Python and `app:app`; `build.py` copies assets to
   `public/static` for Vercel's CDN. Check `/health` for HTTP 200 and
   `{"status":"healthy", "database":"connected", ...}`.
6. On the deployed HTTPS URL, check registration, login, BMI calculation and save,
   journals, history, settings, and sign-out.

Do not use SQLite or `/tmp` as a production database on Vercel: data would not be
reliably shared or persisted across function instances. Production startup fails
with a clear configuration error if required secrets/storage are missing. Production
does not create tables at import time.

Vercel reference: https://vercel.com/docs/frameworks/backend/flask

## Behavior and limits

- Every state-changing request requires CSRF protection; sign-out uses POST.
- Session cookies are HttpOnly, SameSite=Lax, and Secure in production.
- BMI is recomputed on the server from validated measurements, never trusted from
  browser-supplied BMI/category values. This calculator is restricted to adults 20+.
- BMI is a screening measure, not a diagnosis. It does not assess body composition,
  pregnancy, or individual health needs.
- Dashboard daily totals use UTC. Journals/history show up to 100 recent records.
- `/health` actually queries the database and required tables and returns 503 on failure.
- Email verification, password reset email, AI-generated plans, and automated food
  analysis are not available. Configure platform-level rate limiting before opening
  registration to a large audience.
- No production deployment is claimed by the source alone. Vercel access, database
  credentials, deployment success, and live workflows must be verified separately.
