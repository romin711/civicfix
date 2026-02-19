# CivicFix

A role-based civic issue management platform where citizens report local problems, government officers process department-specific complaints, and admins monitor the full system.

## Highlights

- Multi-role authentication: `citizen`, `government`, and `admin`
- OTP-based signup flow (demo mode)
- Citizen issue reporting with image upload and priority selection
- Automatic department routing for common issue types
- Government dashboard to update complaint status (`Pending`, `In Progress`, `Resolved`)
- Admin dashboard with approval workflow and issue analytics
- SQLite-backed persistence with automatic DB initialization

## Tech Stack

- Backend: Python, Flask
- Frontend: HTML (Jinja2 templates), CSS, Vanilla JavaScript
- Database: SQLite
- File Uploads: Flask/Werkzeug `secure_filename`

## Project Structure

```text
civicfix/
├── app.py
├── requirements.txt
├── dummy_data.sql
├── database/
│   └── civicfix.db (auto-created)
├── static/
│   ├── css/
│   ├── js/
│   └── uploads/ (auto-created, gitignored)
└── templates/
    ├── auth/
    ├── citizen/
    ├── government/
    ├── admin/
    └── partials/
```

## Getting Started

### 1. Prerequisites

- Python 3.9+
- `pip`

### 2. Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Run the app

```bash
python app.py
```

The server starts at:

- `http://127.0.0.1:5000`

## Default Access

On first run, the app auto-creates an admin account:

- Email: `admin@civicfix.com`
- Password: `admin123`

Government accounts require admin approval before login access is granted.

## Optional: Load Sample Data

After first run (or after tables exist), you can insert demo records:

```bash
sqlite3 database/civicfix.db < dummy_data.sql
```

## Main Routes

- Public: `/`, `/signup`, `/login`, `/logout`, `/generate-otp`
- Citizen: `/citizen/home`, `/citizen/report`, `/citizen/my-issues`, `/citizen/profile`
- Admin: `/admin/dashboard`, `/admin/officers`, `/admin/citizens`, `/admin/issues`
- Government: `/government/dashboard`

## Notes

- This project appears to be intended for academic/demo use.
- OTP generation is currently demo-oriented (OTP is returned in the API response).
- Passwords are stored as plain text in the current implementation; production deployment should use password hashing and stronger security hardening.
