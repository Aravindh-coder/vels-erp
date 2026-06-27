from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3, os

app = Flask(__name__)
app.secret_key = "vels_erp_secret_2024"

DB = "erp.db"

def get_db():
    return sqlite3.connect(DB)

def create_tables():
    conn = get_db()
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, regno TEXT UNIQUE,
        dept TEXT, course TEXT DEFAULT '',
        marks TEXT DEFAULT '', attendance TEXT DEFAULT ''
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS staffs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, dept TEXT, position TEXT
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
            c.execute("INSERT INTO students VALUES (NULL,?,?,?,?,?,?)", s)
        except: pass
    conn.commit(); conn.close()

create_tables()

@app.route("/", methods=["GET","POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form["username"].strip().upper()
        password = request.form["password"].strip()
        if username == "ADMIN" and password == "1234":
            session["role"] = "admin"
            return redirect(url_for("admin_dashboard"))
        conn = get_db()
        result = conn.execute(
            "SELECT * FROM students WHERE name=? AND regno=?", (username, password)
        ).fetchone()
        conn.close()
        if result:
            session["role"] = "student"
            session["student_id"] = result[0]
            return redirect(url_for("student_dashboard"))
        else:
            error = "Invalid credentials. Username = Full Name in CAPITALS, Password = Reg No"
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/student")
def student_dashboard():
    if session.get("role") != "student":
        return redirect(url_for("login"))
    conn = get_db()
    student = conn.execute("SELECT * FROM students WHERE id=?", (session["student_id"],)).fetchone()
    conn.close()
    return render_template("student_dashboard.html", student=student)

@app.route("/admin")
def admin_dashboard():
    if session.get("role") != "admin":
        return redirect(url_for("login"))
    conn = get_db()
    depts = ["CSE","Electronics","Mechanical","Civil","Biotechnology","Management"]
    dept_counts = {}
    for d in depts:
        cnt = conn.execute("SELECT COUNT(*) FROM students WHERE dept=?", (d,)).fetchone()[0]
        dept_counts[d] = cnt
    conn.close()
    return render_template("admin_dashboard.html", dept_counts=dept_counts, depts=depts)

@app.route("/admin/students/<dept>")
def admin_students(dept):
    if session.get("role") != "admin":
        return redirect(url_for("login"))
    conn = get_db()
    students = conn.execute("SELECT * FROM students WHERE dept=?", (dept,)).fetchall()
    conn.close()
    return render_template("admin_students.html", students=students, dept=dept)

@app.route("/admin/students/<dept>/add", methods=["POST"])
def add_student(dept):
    if session.get("role") != "admin":
        return redirect(url_for("login"))
    d = request.form
    conn = get_db()
    try:
        conn.execute("INSERT INTO students VALUES (NULL,?,?,?,?,?,?)",
            (d["name"].upper(), d["regno"], d["dept"], d["course"], d["marks"], d["attendance"]))
        conn.commit()
    except: pass
    conn.close()
    return redirect(url_for("admin_students", dept=dept))

@app.route("/admin/students/<dept>/update", methods=["POST"])
def update_student(dept):
    if session.get("role") != "admin":
        return redirect(url_for("login"))
    d = request.form
    conn = get_db()
    conn.execute("UPDATE students SET name=?,dept=?,course=?,marks=?,attendance=? WHERE regno=?",
        (d["name"].upper(), d["dept"], d["course"], d["marks"], d["attendance"], d["regno"]))
    conn.commit(); conn.close()
    return redirect(url_for("admin_students", dept=dept))

@app.route("/admin/students/<dept>/delete/<regno>")
def delete_student(dept, regno):
    if session.get("role") != "admin":
        return redirect(url_for("login"))
    conn = get_db()
    conn.execute("DELETE FROM students WHERE regno=?", (regno,))
    conn.commit(); conn.close()
    return redirect(url_for("admin_students", dept=dept))

@app.route("/admin/staff")
def admin_staff():
    if session.get("role") != "admin":
        return redirect(url_for("login"))
    conn = get_db()
    staffs = conn.execute("SELECT * FROM staffs").fetchall()
    conn.close()
    return render_template("admin_staff.html", staffs=staffs)

@app.route("/admin/staff/add", methods=["POST"])
def add_staff():
    if session.get("role") != "admin":
        return redirect(url_for("login"))
    d = request.form
    conn = get_db()
    conn.execute("INSERT INTO staffs VALUES (NULL,?,?,?)", (d["name"], d["dept"], d["position"]))
    conn.commit(); conn.close()
    return redirect(url_for("admin_staff"))

@app.route("/admin/staff/update", methods=["POST"])
def update_staff():
    if session.get("role") != "admin":
        return redirect(url_for("login"))
    d = request.form
    conn = get_db()
    conn.execute("UPDATE staffs SET name=?,dept=?,position=? WHERE id=?",
        (d["name"], d["dept"], d["position"], d["id"]))
    conn.commit(); conn.close()
    return redirect(url_for("admin_staff"))

@app.route("/admin/staff/delete/<int:sid>")
def delete_staff(sid):
    if session.get("role") != "admin":
        return redirect(url_for("login"))
    conn = get_db()
    conn.execute("DELETE FROM staffs WHERE id=?", (sid,))
    conn.commit(); conn.close()
    return redirect(url_for("admin_staff"))

if __name__ == "__main__":
    app.run(debug=True)
