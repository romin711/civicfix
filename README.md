# 🏛️ CivicFix

A **role-based civic issue management platform** where citizens can report local problems, government officers handle department-specific complaints, and admins monitor and control the entire system.

---

## ✨ Highlights

- 👥 **Multi-role authentication**: Supports `citizen`, `government`, and `admin` roles  
- 🔐 **OTP-based signup flow**: Email verification enabled (demo mode)  
- 📝 **Citizen issue reporting**: Submit complaints with image upload and priority selection  
- 🏢 **Automatic department routing**: Issues are assigned to the appropriate department automatically  
- 📊 **Government dashboard**: Officers can update complaint status (`Pending`, `In Progress`, `Resolved`)  
- 🛠️ **Admin dashboard**: Approval workflow, user management, and issue monitoring  
- 💾 **SQLite-backed persistence**: Automatic database creation and initialization  

---

## 🧰 Tech Stack

- ⚙️ **Backend**: Python, Flask  
- 🎨 **Frontend**: HTML (Jinja2 templates), CSS, Vanilla JavaScript  
- 🗄️ **Database**: SQLite  
- 📁 **File Uploads**: Flask/Werkzeug `secure_filename`  

---

## 📁 Project Structure

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

---

## 🚀 Getting Started

### 1. Prerequisites

- Python 3.9+
- `pip`

---

### 2. Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

### 3. Run the app

```bash
python app.py
```

The server starts at:

- 🌐 `http://127.0.0.1:5000`

---

## 🔐 Default Access

On first run, the system automatically creates an admin account:

- 📧 **Email**: `admin@civicfix.com`  
- 🔑 **Password**: `admin123`  

⚠️ Government accounts require admin approval before login access is granted.

---

## 🧪 Optional: Load Sample Data

After first run (or after tables exist), you can insert demo records:

```bash
sqlite3 database/civicfix.db < dummy_data.sql
```

---

## 🌐 Main Routes

**Public**
- `/`
- `/signup`
- `/login`
- `/logout`
- `/generate-otp`

**Citizen**
- `/citizen/home`
- `/citizen/report`
- `/citizen/my-issues`
- `/citizen/profile`

**Admin**
- `/admin/dashboard`
- `/admin/officers`
- `/admin/citizens`
- `/admin/issues`

**Government**
- `/government/dashboard`

---

## ⚠️ Notes

- This project is designed for **academic and demonstration purposes**
- OTP generation is currently **demo-based** (OTP is returned in API response)
- Passwords are stored in **plain text**

For production use, implement:

- 🔒 Password hashing (bcrypt)
- 🛡️ Strong authentication and security
- 🗄️ Production database (PostgreSQL / MySQL)
- 🚀 Deployment configuration
