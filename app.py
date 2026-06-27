from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "vels_erp_secret_2024"
DB = "erp.db"

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_db(); c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, regno TEXT UNIQUE, dept TEXT, course TEXT DEFAULT '',
        marks TEXT DEFAULT '', attendance TEXT DEFAULT '',
        admission_no TEXT DEFAULT '', semester TEXT DEFAULT 'I', section TEXT DEFAULT 'A',
        dob TEXT DEFAULT '', gender TEXT DEFAULT '', father_name TEXT DEFAULT '',
        mother_name TEXT DEFAULT '', address TEXT DEFAULT '', contact TEXT DEFAULT '',
        email TEXT DEFAULT '', community TEXT DEFAULT '', nationality TEXT DEFAULT '',
        religion TEXT DEFAULT '', hosteller TEXT DEFAULT 'No',
        occupation_income TEXT DEFAULT '', district_state TEXT DEFAULT ''
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS staffs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, staff_id TEXT UNIQUE, dept TEXT, position TEXT,
        dob TEXT DEFAULT '', gender TEXT DEFAULT '', father_name TEXT DEFAULT '',
        mother_name TEXT DEFAULT '', address TEXT DEFAULT '', contact TEXT DEFAULT '',
        email TEXT DEFAULT '', community TEXT DEFAULT '', nationality TEXT DEFAULT '',
        religion TEXT DEFAULT '', hosteller TEXT DEFAULT 'No',
        occupation_income TEXT DEFAULT '', district_state TEXT DEFAULT ''
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS subject_marks (
        id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INTEGER,
        subject TEXT, internal_marks TEXT DEFAULT '', exam_marks TEXT DEFAULT ''
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS subject_attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INTEGER,
        subject TEXT, classes_held INTEGER DEFAULT 0, classes_attended INTEGER DEFAULT 0
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS fee_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INTEGER,
        fee_type TEXT, amount TEXT DEFAULT '0', paid_amount TEXT DEFAULT '0',
        due_date TEXT DEFAULT '', status TEXT DEFAULT 'Due'
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS course_registration (
        id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INTEGER,
        subject TEXT, registered TEXT DEFAULT 'Yes'
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS student_activity (
        id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INTEGER,
        activity TEXT, activity_date TEXT DEFAULT ''
    )""")
    sample = [
        ("ARAVINDH A",  "24623134", "CSE",           "B.Tech CSE",       "85", "92%"),
        ("BHARATH R",   "24623135", "CSE",           "B.Tech CSE",       "78", "88%"),
        ("PRIYA S",     "24623136", "Electronics",   "B.Tech ECE",       "90", "95%"),
        ("KUMAR M",     "24623137", "Mechanical",    "B.Tech Mech",      "72", "80%"),
        ("DIVYA K",     "24623138", "Civil",         "B.Tech Civil",     "88", "91%"),
        ("RAHUL P",     "24623139", "Biotechnology", "B.Tech Biotech",   "76", "85%"),
        ("SNEHA L",     "24623140", "Management",    "BBA",              "82", "89%"),
    ]
    for s in sample:
        try:
            c.execute("INSERT INTO students (name,regno,dept,course,marks,attendance) VALUES (?,?,?,?,?,?)", s)
        except: pass
    staff_sample = [("Dr. SURESH KUMAR", "STF001", "CSE", "Assistant Professor")]
    for st in staff_sample:
        try:
            c.execute("INSERT INTO staffs (name,staff_id,dept,position) VALUES (?,?,?,?)", st)
        except: pass
    conn.commit(); conn.close()

create_tables()

# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form["username"].strip().upper()
        password = request.form["password"].strip()
        if username == "ADMIN" and password == "1234":
            session.clear(); session["role"] = "admin"
            return redirect(url_for("admin_dashboard"))
        conn = get_db()
        student = conn.execute("SELECT * FROM students WHERE UPPER(name)=? AND regno=?", (username, password)).fetchone()
        if student:
            conn.close()
            session.clear(); session["role"] = "student"; session["student_id"] = student["id"]
            return redirect(url_for("student_dashboard"))
        staff = conn.execute("SELECT * FROM staffs WHERE UPPER(name)=? AND staff_id=?", (username, password)).fetchone()
        conn.close()
        if staff:
            session.clear(); session["role"] = "staff"; session["staff_id"] = staff["id"]
            return redirect(url_for("staff_dashboard"))
        error = "Invalid credentials. Student: Name (CAPS) + RegNo. Staff: Name + Staff ID. Admin: ADMIN + 1234."
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

def require_student():
    return session.get("role") == "student"

def current_student(conn):
    return conn.execute("SELECT * FROM students WHERE id=?", (session["student_id"],)).fetchone()

# ---------------- STUDENT ----------------
@app.route("/student")
def student_dashboard():
    if not require_student(): return redirect(url_for("login"))
    conn = get_db(); student = current_student(conn); conn.close()
    return render_template("student_dashboard.html", student=student)

@app.route("/student/edit", methods=["GET", "POST"])
def student_edit():
    if not require_student(): return redirect(url_for("login"))
    conn = get_db()
    if request.method == "POST":
        d = request.form
        conn.execute("""UPDATE students SET dob=?,gender=?,father_name=?,mother_name=?,address=?,
            contact=?,email=?,community=?,nationality=?,religion=?,hosteller=?,occupation_income=?,district_state=?
            WHERE id=?""", (d.get("dob",""), d.get("gender",""), d.get("father_name",""), d.get("mother_name",""),
            d.get("address",""), d.get("contact",""), d.get("email",""), d.get("community",""),
            d.get("nationality",""), d.get("religion",""), d.get("hosteller","No"),
            d.get("occupation_income",""), d.get("district_state",""), session["student_id"]))
        conn.commit(); conn.close()
        return redirect(url_for("student_dashboard"))
    s = current_student(conn); conn.close()
    return render_template("student_edit.html", s=s)

@app.route("/student/activity")
def student_activity():
    if not require_student(): return redirect(url_for("login"))
    conn = get_db(); s = current_student(conn)
    rows = conn.execute("SELECT * FROM student_activity WHERE student_id=?", (s["id"],)).fetchall()
    conn.close()
    return render_template("student_activity.html", s=s, rows=rows)

@app.route("/student/courses")
def student_courses():
    if not require_student(): return redirect(url_for("login"))
    conn = get_db(); s = current_student(conn)
    rows = conn.execute("SELECT * FROM course_registration WHERE student_id=?", (s["id"],)).fetchall()
    conn.close()
    return render_template("student_courses.html", s=s, rows=rows)

@app.route("/student/attendance")
def student_attendance():
    if not require_student(): return redirect(url_for("login"))
    conn = get_db(); s = current_student(conn)
    rows = conn.execute("SELECT * FROM subject_attendance WHERE student_id=?", (s["id"],)).fetchall()
    conn.close()
    return render_template("student_attendance.html", s=s, rows=rows)

@app.route("/student/marks")
def student_marks():
    if not require_student(): return redirect(url_for("login"))
    conn = get_db(); s = current_student(conn)
    rows = conn.execute("SELECT * FROM subject_marks WHERE student_id=?", (s["id"],)).fetchall()
    conn.close()
    return render_template("student_marks.html", s=s, rows=rows)

@app.route("/student/result")
def student_result():
    if not require_student(): return redirect(url_for("login"))
    conn = get_db(); s = current_student(conn)
    rows = conn.execute("SELECT * FROM subject_marks WHERE student_id=?", (s["id"],)).fetchall()
    conn.close()
    return render_template("student_result.html", s=s, rows=rows)

@app.route("/student/fees")
def student_fees():
    if not require_student(): return redirect(url_for("login"))
    conn = get_db(); s = current_student(conn)
    rows = conn.execute("SELECT * FROM fee_records WHERE student_id=?", (s["id"],)).fetchall()
    conn.close()
    return render_template("student_fees.html", s=s, rows=rows)

@app.route("/student/hallticket")
def student_hallticket():
    if not require_student(): return redirect(url_for("login"))
    conn = get_db(); s = current_student(conn)
    rows = conn.execute("SELECT * FROM subject_marks WHERE student_id=?", (s["id"],)).fetchall()
    conn.close()
    return render_template("student_hallticket.html", s=s, rows=rows)

# ---------------- STAFF ----------------
def require_staff():
    return session.get("role") == "staff"

def current_staff(conn):
    return conn.execute("SELECT * FROM staffs WHERE id=?", (session["staff_id"],)).fetchone()

@app.route("/staff")
def staff_dashboard():
    if not require_staff(): return redirect(url_for("login"))
    conn = get_db(); s = current_staff(conn); conn.close()
    return render_template("staff_dashboard.html", s=s)

@app.route("/staff/edit", methods=["GET", "POST"])
def staff_edit():
    if not require_staff(): return redirect(url_for("login"))
    conn = get_db()
    if request.method == "POST":
        d = request.form
        conn.execute("""UPDATE staffs SET dob=?,gender=?,father_name=?,mother_name=?,address=?,
            contact=?,email=?,community=?,nationality=?,religion=?,hosteller=?,occupation_income=?,district_state=?
            WHERE id=?""", (d.get("dob",""), d.get("gender",""), d.get("father_name",""), d.get("mother_name",""),
            d.get("address",""), d.get("contact",""), d.get("email",""), d.get("community",""),
            d.get("nationality",""), d.get("religion",""), d.get("hosteller","No"),
            d.get("occupation_income",""), d.get("district_state",""), session["staff_id"]))
        conn.commit(); conn.close()
        return redirect(url_for("staff_dashboard"))
    s = current_staff(conn); conn.close()
    return render_template("staff_edit.html", s=s)

# ---------------- ADMIN ----------------
def require_admin():
    return session.get("role") == "admin"

@app.route("/admin")
def admin_dashboard():
    if not require_admin(): return redirect(url_for("login"))
    conn = get_db()
    depts = ["CSE","Electronics","Mechanical","Civil","Biotechnology","Management"]
    dept_counts = {d: conn.execute("SELECT COUNT(*) FROM students WHERE dept=?", (d,)).fetchone()[0] for d in depts}
    conn.close()
    return render_template("admin_dashboard.html", dept_counts=dept_counts, depts=depts)

@app.route("/admin/students/<dept>")
def admin_students(dept):
    if not require_admin(): return redirect(url_for("login"))
    conn = get_db()
    students = conn.execute("SELECT * FROM students WHERE dept=?", (dept,)).fetchall()
    conn.close()
    return render_template("admin_students.html", students=students, dept=dept)

@app.route("/admin/students/<dept>/add", methods=["POST"])
def add_student(dept):
    if not require_admin(): return redirect(url_for("login"))
    d = request.form; conn = get_db()
    try:
        conn.execute("INSERT INTO students (name,regno,dept,course,marks,attendance) VALUES (?,?,?,?,?,?)",
            (d["name"].upper(), d["regno"], d["dept"], d.get("course",""), d.get("marks",""), d.get("attendance","")))
        conn.commit()
    except: pass
    conn.close()
    return redirect(url_for("admin_students", dept=dept))

@app.route("/admin/students/<dept>/update", methods=["POST"])
def update_student(dept):
    if not require_admin(): return redirect(url_for("login"))
    d = request.form; conn = get_db()
    conn.execute("UPDATE students SET name=?,dept=?,course=?,marks=?,attendance=? WHERE regno=?",
        (d["name"].upper(), d["dept"], d.get("course",""), d.get("marks",""), d.get("attendance",""), d["regno"]))
    conn.commit(); conn.close()
    return redirect(url_for("admin_students", dept=dept))

@app.route("/admin/student/<int:sid>")
def admin_student_detail(sid):
    if not require_admin(): return redirect(url_for("login"))
    conn = get_db()
    student = conn.execute("SELECT * FROM students WHERE id=?", (sid,)).fetchone()
    marks_rows = conn.execute("SELECT * FROM subject_marks WHERE student_id=?", (sid,)).fetchall()
    att_rows = conn.execute("SELECT * FROM subject_attendance WHERE student_id=?", (sid,)).fetchall()
    fee_rows = conn.execute("SELECT * FROM fee_records WHERE student_id=?", (sid,)).fetchall()
    conn.close()
    return render_template("admin_student_detail.html", student=student,
        marks_rows=marks_rows, att_rows=att_rows, fee_rows=fee_rows)

@app.route("/admin/student/<int:sid>/marks/add", methods=["POST"])
def admin_add_marks(sid):
    if not require_admin(): return redirect(url_for("login"))
    d = request.form; conn = get_db()
    conn.execute("INSERT INTO subject_marks (student_id,subject,internal_marks,exam_marks) VALUES (?,?,?,?)",
        (sid, d["subject"], d.get("internal_marks",""), d.get("exam_marks","")))
    conn.commit(); conn.close()
    return redirect(url_for("admin_student_detail", sid=sid))

@app.route("/admin/student/<int:sid>/marks/update/<int:mid>", methods=["POST"])
def admin_update_marks(sid, mid):
    if not require_admin(): return redirect(url_for("login"))
    d = request.form; conn = get_db()
    conn.execute("UPDATE subject_marks SET internal_marks=?,exam_marks=? WHERE id=?",
        (d.get("internal_marks",""), d.get("exam_marks",""), mid))
    conn.commit(); conn.close()
    return redirect(url_for("admin_student_detail", sid=sid))

@app.route("/admin/student/<int:sid>/marks/delete/<int:mid>")
def admin_delete_marks(sid, mid):
    if not require_admin(): return redirect(url_for("login"))
    conn = get_db(); conn.execute("DELETE FROM subject_marks WHERE id=?", (mid,)); conn.commit(); conn.close()
    return redirect(url_for("admin_student_detail", sid=sid))

@app.route("/admin/student/<int:sid>/attendance/add", methods=["POST"])
def admin_add_attendance(sid):
    if not require_admin(): return redirect(url_for("login"))
    d = request.form; conn = get_db()
    conn.execute("INSERT INTO subject_attendance (student_id,subject,classes_held,classes_attended) VALUES (?,?,?,?)",
        (sid, d["subject"], d.get("classes_held",0) or 0, d.get("classes_attended",0) or 0))
    conn.commit(); conn.close()
    return redirect(url_for("admin_student_detail", sid=sid))

@app.route("/admin/student/<int:sid>/attendance/update/<int:aid>", methods=["POST"])
def admin_update_attendance(sid, aid):
    if not require_admin(): return redirect(url_for("login"))
    d = request.form; conn = get_db()
    conn.execute("UPDATE subject_attendance SET classes_held=?,classes_attended=? WHERE id=?",
        (d.get("classes_held",0) or 0, d.get("classes_attended",0) or 0, aid))
    conn.commit(); conn.close()
    return redirect(url_for("admin_student_detail", sid=sid))

@app.route("/admin/student/<int:sid>/attendance/delete/<int:aid>")
def admin_delete_attendance(sid, aid):
    if not require_admin(): return redirect(url_for("login"))
    conn = get_db(); conn.execute("DELETE FROM subject_attendance WHERE id=?", (aid,)); conn.commit(); conn.close()
    return redirect(url_for("admin_student_detail", sid=sid))

@app.route("/admin/student/<int:sid>/fees/add", methods=["POST"])
def admin_add_fee(sid):
    if not require_admin(): return redirect(url_for("login"))
    d = request.form; conn = get_db()
    conn.execute("INSERT INTO fee_records (student_id,fee_type,amount,paid_amount,due_date,status) VALUES (?,?,?,?,?,?)",
        (sid, d["fee_type"], d.get("amount","0"), d.get("paid_amount","0"), d.get("due_date",""), d.get("status","Due")))
    conn.commit(); conn.close()
    return redirect(url_for("admin_student_detail", sid=sid))

@app.route("/admin/student/<int:sid>/fees/delete/<int:fid>")
def admin_delete_fee(sid, fid):
    if not require_admin(): return redirect(url_for("login"))
    conn = get_db(); conn.execute("DELETE FROM fee_records WHERE id=?", (fid,)); conn.commit(); conn.close()
    return redirect(url_for("admin_student_detail", sid=sid))

@app.route("/admin/student/<int:sid>/overall/update", methods=["POST"])
def admin_update_overall(sid):
    if not require_admin(): return redirect(url_for("login"))
    d = request.form; conn = get_db()
    conn.execute("UPDATE students SET course=?,marks=?,attendance=?,admission_no=?,semester=?,section=? WHERE id=?",
        (d.get("course",""), d.get("marks",""), d.get("attendance",""), d.get("admission_no",""),
         d.get("semester","I"), d.get("section","A"), sid))
    conn.commit(); conn.close()
    return redirect(url_for("admin_student_detail", sid=sid))

@app.route("/admin/students/<dept>/delete/<regno>")
def delete_student(dept, regno):
    if not require_admin(): return redirect(url_for("login"))
    conn = get_db(); conn.execute("DELETE FROM students WHERE regno=?", (regno,)); conn.commit(); conn.close()
    return redirect(url_for("admin_students", dept=dept))

@app.route("/admin/staff")
def admin_staff():
    if not require_admin(): return redirect(url_for("login"))
    conn = get_db(); staffs = conn.execute("SELECT * FROM staffs").fetchall(); conn.close()
    return render_template("admin_staff.html", staffs=staffs)

@app.route("/admin/staff/add", methods=["POST"])
def add_staff():
    if not require_admin(): return redirect(url_for("login"))
    d = request.form; conn = get_db()
    try:
        conn.execute("INSERT INTO staffs (name,staff_id,dept,position) VALUES (?,?,?,?)",
            (d["name"], d["staff_id"], d["dept"], d.get("position","")))
        conn.commit()
    except: pass
    conn.close()
    return redirect(url_for("admin_staff"))

@app.route("/admin/staff/update", methods=["POST"])
def update_staff():
    if not require_admin(): return redirect(url_for("login"))
    d = request.form; conn = get_db()
    conn.execute("UPDATE staffs SET name=?,dept=?,position=? WHERE id=?",
        (d["name"], d["dept"], d.get("position",""), d["id"]))
    conn.commit(); conn.close()
    return redirect(url_for("admin_staff"))

@app.route("/admin/staff/delete/<int:sid>")
def delete_staff(sid):
    if not require_admin(): return redirect(url_for("login"))
    conn = get_db(); conn.execute("DELETE FROM staffs WHERE id=?", (sid,)); conn.commit(); conn.close()
    return redirect(url_for("admin_staff"))

if __name__ == "__main__":
    app.run(debug=True)
