# SAFEHER API (PythonAnywhere)

## PythonAnywhere setup
1. Create a PythonAnywhere account and upload this backend folder or clone its GitHub repo.
2. Create a virtualenv (example Python 3.11):
   `mkvirtualenv --python=/usr/bin/python3.11 safeher-venv`
3. Install dependencies:
   `pip install -r requirements.txt`
4. In the **Web** tab, create a Flask app using manual configuration and point the WSGI file to this `app.py` via the project path; see the main README for an example WSGI configuration.
5. Set the source path to the backend folder and virtualenv to `safeher-venv`.
6. Reload the web app and test `https://YOUR-USERNAME.pythonanywhere.com/health`.

The SQLite file is created next to app.py by default. For production, set DATABASE_PATH to a persistent writable path in your own PythonAnywhere account.

## CORS
Set `ALLOWED_ORIGINS` to the exact Vercel domain, e.g. `https://safeher-inscriptions.vercel.app`. During initial testing it defaults to `*`; restrict it after the frontend URL is known.

## Important
This API only records registrations and exposes the aggregate total. It does not collect violence reports and is not an emergency service. Protect personal data, limit retention and never publish exported personal records.
