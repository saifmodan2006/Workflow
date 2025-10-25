# Link Building Workflow Manager (Streamlit + SQLite)

This repo contains a Streamlit app and a small SQLite data layer to manage link-building workflows (Free, Outreach, Exchange, Pay).

What is included
- `app.py` — Streamlit UI. Upload CSVs, add websites manually, edit/update records, view activity logs, export CSV.
- `db.py` — SQLAlchemy models and helper functions (Website, ActivityLog). Creates `websites.db` on first run.
- `requirements.txt` — minimal dependencies.

Quick start (Windows PowerShell)

1. From the project folder:

```powershell
cd 'c:\Users\Sahil\Downloads\VS Code File\Workflow Task'
# (optional) create and activate venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

2. First run will create `websites.db` in the same folder.

CSV upload notes
- Provide a CSV with at least a `website` column (case-insensitive). Other useful headers: `contact_email`, `contact_name`, `module`, `traffic`, `da`, `status`, `assignee`, `notes`.

Next steps / improvements
- Add authentication (basic or SSO) for multiple users.
- Add scheduled reminders and follow-up automation.
- Replace SQLite with Postgres for team-level concurrency.
- Add outreach email templates and SMTP/Gmail integration.

If you want, I can now: run a quick syntax check or add a sample CSV and seed data. Tell me which.
