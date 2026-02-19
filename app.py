from flask import Flask, render_template, request, redirect, session, flash, jsonify
import re
import sqlite3
import random
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "civicfix_secret_key"

#  CONFIG 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "civicfix.db")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(os.path.join(BASE_DIR, "database"), exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

GOV_DEPARTMENTS = ["Water Supply", "Sanitation", "Electricity", "Public Works"]
DEFAULT_ADMIN_EMAIL = "admin@civicfix.com"
DEFAULT_ADMIN_MOBILE = "9999999999"
DEPARTMENT_BY_ISSUE_TYPE = {
    "Garbage": "Sanitation",
    "Water": "Water Supply",
    "Street Light": "Electricity",
    "Road": "Public Works"
}
DEPARTMENT_BY_CODE = {
    "W": "Water Supply",
    "S": "Sanitation",
    "E": "Electricity",
    "P": "Public Works"
}

# ================= DATABASE =================
def get_db():
    return sqlite3.connect(DB_PATH)

def init_db():
    db = get_db()
    cur = db.cursor()

    # USERS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        mobile TEXT,
        password TEXT,
        role TEXT,
        gov_id TEXT,
        status TEXT,
        aadhaar TEXT,
        dob TEXT,
        gender TEXT,
        address TEXT,
        department TEXT
    )
    """)

    # Backward-compatible migration for older databases
    cur.execute("PRAGMA table_info(users)")
    user_columns = [column[1] for column in cur.fetchall()]
    if "department" not in user_columns:
        cur.execute("ALTER TABLE users ADD COLUMN department TEXT")
    if "mobile" not in user_columns:
        cur.execute("ALTER TABLE users ADD COLUMN mobile TEXT")

    # COMPLAINTS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS complaints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT,
        location TEXT,
        department TEXT,
        citizen_id INTEGER,
        priority TEXT,
        status TEXT,
        image TEXT,
        assigned_to INTEGER,
        date TEXT
    )
    """)

    # DEFAULT ADMIN
    cur.execute("SELECT id, email, mobile FROM users WHERE role='admin' LIMIT 1")
    admin_user = cur.fetchone()
    if not admin_user:
        cur.execute("""
        INSERT INTO users (name,email,mobile,password,role,status)
        VALUES (?,?,?,?,?,?)
        """, ("Admin", DEFAULT_ADMIN_EMAIL, DEFAULT_ADMIN_MOBILE, "admin123", "admin", "active"))
    else:
        admin_id, _, admin_mobile = admin_user
        if not admin_mobile:
            cur.execute("UPDATE users SET mobile=? WHERE id=?", (DEFAULT_ADMIN_MOBILE, admin_id))

    db.commit()
    db.close()


# ================= HELPER FUNCTIONS =================
def is_profile_complete(user_id):
    """Check if citizen profile is complete"""
    db = get_db()
    cur = db.cursor()
    cur.execute("""
    SELECT aadhaar, dob, gender, address
    FROM users WHERE id=?
    """, (user_id,))
    user = cur.fetchone()
    
    if not user:
        return False
    
    # Check if all required fields are filled
    return all([user[0], user[1], user[2], user[3]])

def is_basic_email(email):
    normalized_email = (email or "").strip()
    return "@" in normalized_email and "." in normalized_email

def is_valid_mobile(mobile):
    normalized_mobile = (mobile or "").strip()
    return bool(re.fullmatch(r"[789]\d{9}", normalized_mobile))

def require_role(role):
    if session.get("role") != role:
        return redirect("/login")
    return None

def fetch_officers(cur, status):
    cur.execute("""
    SELECT id, name, email, gov_id, department
    FROM users
    WHERE role='government' AND status=?
    ORDER BY id DESC
    """, (status,))
    return cur.fetchall()

def fetch_citizens(cur):
    cur.execute("""
    SELECT id, name, email
    FROM users
    WHERE role='citizen'
    ORDER BY id DESC
    """)
    return cur.fetchall()

# ================= PUBLIC =================
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate-otp", methods=["POST"])
def generate_otp():
    payload = request.get_json(silent=True) or request.form

    email = (payload.get("email") or "").strip().lower()
    mobile = (payload.get("mobile") or "").strip()

    if not is_basic_email(email):
        return jsonify({
            "ok": False,
            "message": "Enter a valid email before generating OTP"
        }), 400

    if not is_valid_mobile(mobile):
        return jsonify({
            "ok": False,
            "message": "Enter valid 10-digit mobile number starting with 7, 8, or 9"
        }), 400


    otp = str(random.randint(100000, 999999))

    
    session["otp"] = otp
    session["email"] = email
    session["mobile"] = mobile

    return jsonify({
        "ok": True,
        "otp": otp
    })





# ================= AUTH =================
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        mobile = request.form["mobile"].strip()
        password = request.form["password"]
        role = request.form["role"]
        gov_id = request.form.get("gov_id", "").strip()
        department = request.form.get("department")
        otp = request.form["otp"].strip()

        if not is_basic_email(email):
            flash("Enter a valid email with @ and .")
            return redirect("/signup")

        if not is_valid_mobile(mobile):
            flash("Enter a valid 10-digit mobile number starting with 7, 8, or 9")
            return redirect("/signup")

        if otp != session.get("otp"):
            flash("Invalid OTP")
            return redirect("/signup")

        if role == "government":
            if not gov_id:
                flash("Government Official ID is required")
                return redirect("/signup")
            if department not in GOV_DEPARTMENTS:
                flash("Please select a valid department")
                return redirect("/signup")
        else:
            gov_id = None
            department = None

        status = "pending" if role == "government" else "active"

        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT id FROM users WHERE email=?", (email,))
        if cur.fetchone():
            flash("Email already registered")
            return redirect("/signup")

        cur.execute("SELECT id FROM users WHERE mobile=?", (mobile,))
        if cur.fetchone():
            flash("Mobile number already registered")
            return redirect("/signup")

        cur.execute("""
        INSERT INTO users (name,email,mobile,password,role,gov_id,status,department)
        VALUES (?,?,?,?,?,?,?,?)
        """, (name, email, mobile, password, role, gov_id, status, department))
        db.commit()

        session.pop("otp", None)
        flash("Signup successful. Please login.", "success")
        return redirect("/login")

    return render_template("auth/signup.html", departments=GOV_DEPARTMENTS)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        if not is_basic_email(email):
            flash("Enter a valid email with @ and .")
            return redirect("/login")

        db = get_db()
        cur = db.cursor()
        cur.execute("""
        SELECT id, role, status FROM users
        WHERE email=? AND password=?
        """, (email, password))
        user = cur.fetchone()

        if not user:
            flash("Invalid credentials")
            return redirect("/login")

        if user[1] == "government" and user[2] != "active":
            flash("Government account not approved yet")
            return redirect("/login")

        user_id, role = user[0], user[1]
        session["user_id"] = user_id
        session["role"] = role

        if role == "citizen":
            if not is_profile_complete(user_id):
                flash("Please complete your profile to report issues", "info")
            return redirect("/citizen/home")

        return redirect({
            "admin": "/admin/dashboard",
            "government": "/government/dashboard",
        }.get(role, "/login"))

    return render_template("auth/login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ================= CITIZEN =================
@app.route("/citizen/home")
def citizen_home():
    if role_check := require_role("citizen"):
        return role_check

    db = get_db()
    cur = db.cursor()
    cur.execute("""
    SELECT complaints.title, complaints.description, complaints.location,
           complaints.priority, complaints.status, complaints.image, users.name
    FROM complaints
    JOIN users ON complaints.citizen_id = users.id
    ORDER BY complaints.id DESC
    """)
    issues = cur.fetchall()

    return render_template("citizen/home.html", issues=issues)

@app.route("/citizen/report", methods=["GET", "POST"])
def citizen_report():
    if role_check := require_role("citizen"):
        return role_check
    
    # Check if profile is complete before allowing issue submission
    if not is_profile_complete(session["user_id"]):
        flash("Please complete your profile before reporting issues", "info")
        return redirect("/citizen/profile/edit")

    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        location = request.form["location"]
        issue_type = request.form["type"]
        priority = request.form["priority"]

        image_file = request.files.get("image")
        filename = None

        if image_file and image_file.filename:
            filename = secure_filename(image_file.filename)
            image_file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        from datetime import datetime
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        db = get_db()
        cur = db.cursor()
        cur.execute("""
        INSERT INTO complaints
        (title,description,location,department,citizen_id,priority,status,image,date)
        VALUES (?,?,?,?,?,?,?,?,?)
        """, (
            title, description, location,
            DEPARTMENT_BY_ISSUE_TYPE.get(issue_type),
            session["user_id"], priority,
            "Pending", filename, current_date
        ))
        db.commit()

        return redirect("/citizen/my-issues")

    return render_template("citizen/report.html")

@app.route("/citizen/my-issues")
def citizen_my_issues():
    if role_check := require_role("citizen"):
        return role_check

    db = get_db()
    cur = db.cursor()
    cur.execute("""
    SELECT title, location, priority, status, image
    FROM complaints
    WHERE citizen_id=?
    ORDER BY id DESC
    """, (session["user_id"],))
    issues = cur.fetchall()

    return render_template("citizen/my_issues.html", issues=issues)

@app.route("/citizen/profile")
def citizen_profile():
    if role_check := require_role("citizen"):
        return role_check

    db = get_db()
    cur = db.cursor()
    cur.execute("""
    SELECT name,email,aadhaar,dob,gender,address
    FROM users WHERE id=?
    """, (session["user_id"],))
    user = cur.fetchone()

    return render_template("citizen/profile.html", user=user)

@app.route("/citizen/profile/edit", methods=["GET", "POST"])
def citizen_profile_edit():
    if role_check := require_role("citizen"):
        return role_check
    
    if request.method == "POST":
        aadhaar = request.form["aadhaar"]
        dob = request.form["dob"]
        gender = request.form["gender"]
        address = request.form["address"]
        
        db = get_db()
        cur = db.cursor()
        cur.execute("""
        UPDATE users
        SET aadhaar=?, dob=?, gender=?, address=?
        WHERE id=?
        """, (aadhaar, dob, gender, address, session["user_id"]))
        db.commit()
        
        flash("Profile updated successfully!", "success")
        return redirect("/citizen/profile")
    
    # GET request - show form with current data
    db = get_db()
    cur = db.cursor()
    cur.execute("""
    SELECT name, email, aadhaar, dob, gender, address
    FROM users WHERE id=?
    """, (session["user_id"],))
    user = cur.fetchone()
    
    return render_template("citizen/profile_edit.html", user=user)

#  ADMIN 
@app.route("/admin/dashboard")
def admin_dashboard():
    if role_check := require_role("admin"):
        return role_check

    db = get_db()
    cur = db.cursor()

    # Get statistics
    cur.execute("SELECT COUNT(*) FROM users WHERE role='government' AND status='active'")
    total_officers = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM users WHERE role='citizen'")
    total_citizens = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM complaints")
    total_issues = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM users WHERE role='government' AND status='pending'")
    pending_count = cur.fetchone()[0]

    # Get all complaints
    cur.execute("SELECT * FROM complaints ORDER BY id DESC")
    complaints = cur.fetchall()

    pending_gov = fetch_officers(cur, "pending")
    approved_officers = fetch_officers(cur, "active")
    citizens = fetch_citizens(cur)

    return render_template(
        "admin/dashboard.html",
        total_officers=total_officers,
        total_citizens=total_citizens,
        total_issues=total_issues,
        pending_count=pending_count,
        complaints=complaints,
        pending=pending_gov,
        approved_officers=approved_officers,
        citizens=citizens
    )

@app.route("/admin/approve/<int:user_id>")
def approve_government(user_id):
    db = get_db()
    cur = db.cursor()
    cur.execute("""
    UPDATE users SET status='active'
    WHERE id=? AND role='government'
    """, (user_id,))
    db.commit()
    return redirect("/admin/officers")

@app.route("/admin/reject/<int:user_id>")
def reject_government(user_id):
    db = get_db()
    cur = db.cursor()
    cur.execute("DELETE FROM users WHERE id=?", (user_id,))
    db.commit()
    return redirect("/admin/officers")

@app.route("/admin/officers")
def admin_officers():
    if role_check := require_role("admin"):
        return role_check

    db = get_db()
    cur = db.cursor()

    pending_gov = fetch_officers(cur, "pending")
    approved_officers = fetch_officers(cur, "active")

    return render_template(
        "admin/officers.html",
        pending=pending_gov,
        approved_officers=approved_officers
    )

@app.route("/admin/citizens")
def admin_citizens():
    if role_check := require_role("admin"):
        return role_check

    db = get_db()
    cur = db.cursor()
    
    citizens = fetch_citizens(cur)

    return render_template(
        "admin/citizens.html",
        citizens=citizens
    )

@app.route("/admin/issues")
def admin_issues():
    if role_check := require_role("admin"):
        return role_check

    db = get_db()
    cur = db.cursor()
    
    # Get filters from query parameters
    area_filter = request.args.get("area", "")
    status_filter = request.args.get("status", "")
    priority_filter = request.args.get("priority", "")
    department_filter = request.args.get("department", "")
    
    # Build dynamic query based on filters
    query = """
    SELECT id, title, location, department, priority, status, date
    FROM complaints
    WHERE 1=1
    """
    params = []
    
    for column, value in (
        ("location", area_filter),
        ("status", status_filter),
        ("priority", priority_filter),
        ("department", department_filter),
    ):
        if value:
            query += f" AND {column}=?"
            params.append(value)
    
    query += " ORDER BY id DESC"
    
    cur.execute(query, params)
    complaints = cur.fetchall()
    
    # Get comprehensive statistics
    
    # Area-wise stats
    cur.execute("""
    SELECT location, COUNT(*) as count
    FROM complaints
    GROUP BY location
    ORDER BY count DESC
    """)
    area_stats = cur.fetchall()
    
    # Status-wise stats
    cur.execute("""
    SELECT status, COUNT(*) as count
    FROM complaints
    GROUP BY status
    """)
    status_stats = cur.fetchall()
    
    # Priority-wise stats
    cur.execute("""
    SELECT priority, COUNT(*) as count
    FROM complaints
    GROUP BY priority
    ORDER BY 
        CASE priority
            WHEN 'High' THEN 1
            WHEN 'Medium' THEN 2
            WHEN 'Low' THEN 3
        END
    """)
    priority_stats = cur.fetchall()
    
    # Department-wise stats
    cur.execute("""
    SELECT department, COUNT(*) as count
    FROM complaints
    GROUP BY department
    ORDER BY count DESC
    """)
    department_stats = cur.fetchall()

    return render_template(
        "admin/issues.html",
        complaints=complaints,
        area_stats=area_stats,
        status_stats=status_stats,
        priority_stats=priority_stats,
        department_stats=department_stats,
        selected_area=area_filter,
        selected_status=status_filter,
        selected_priority=priority_filter,
        selected_department=department_filter
    )

# ================= GOVERNMENT =================
@app.route("/government/dashboard")
def government_dashboard():
    if role_check := require_role("government"):
        return role_check

    db = get_db()
    cur = db.cursor()

    # Get government officer info
    cur.execute("""
    SELECT name, department, gov_id FROM users
    WHERE id=?
    """, (session["user_id"],))
    officer = cur.fetchone()

    # Use explicit department if set; fallback for legacy gov_id-based users.
    department = officer[1] if officer and officer[1] else None
    if not department:
        dept_code = officer[2][0] if officer and officer[2] else "W"
        department = DEPARTMENT_BY_CODE.get(dept_code, "Water Supply")

    # Get all complaints for this department
    cur.execute("""
    SELECT id, title, location, status, priority, date
    FROM complaints
    WHERE department=?
    ORDER BY id DESC
    """, (department,))
    complaints = cur.fetchall()

    # Calculate statistics
    total = len(complaints)
    pending = sum(1 for c in complaints if c[3] == "Pending")
    in_progress = sum(1 for c in complaints if c[3] == "In Progress")
    resolved = sum(1 for c in complaints if c[3] == "Resolved")

    return render_template(
        "government/dashboard.html",
        officer_name=officer[0] if officer else "Officer",
        department=department,
        total=total,
        pending=pending,
        in_progress=in_progress,
        resolved=resolved,
        complaints=complaints
    )

@app.route("/government/update-status/<int:complaint_id>", methods=["POST"])
def update_complaint_status(complaint_id):
    if role_check := require_role("government"):
        return role_check

    new_status = (request.form.get("status") or "").strip()
    allowed_statuses = {"Pending", "In Progress", "Resolved"}
    if new_status not in allowed_statuses:
        flash("Please select a valid complaint status.", "error")
        return redirect("/government/dashboard")

    db = get_db()
    cur = db.cursor()

    cur.execute("SELECT department FROM users WHERE id=?", (session["user_id"],))
    officer_row = cur.fetchone()
    officer_department = officer_row[0] if officer_row else None

    cur.execute("SELECT status, department FROM complaints WHERE id=?", (complaint_id,))
    complaint_row = cur.fetchone()
    if not complaint_row:
        flash("Complaint not found.", "error")
        return redirect("/government/dashboard")

    current_status, complaint_department = complaint_row
    if officer_department and complaint_department != officer_department:
        flash("You can only update complaints assigned to your department.", "error")
        return redirect("/government/dashboard")

    if current_status == new_status:
        flash("No status change detected.", "info")
        return redirect("/government/dashboard")

    cur.execute("""
    UPDATE complaints
    SET status=?, assigned_to=?
    WHERE id=?
    """, (new_status, session["user_id"], complaint_id))
    db.commit()
    flash(f"Complaint status updated to {new_status}.", "success")

    return redirect("/government/dashboard")

# ================= MAIN =================
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
