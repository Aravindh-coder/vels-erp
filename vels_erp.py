from tkinter import *
from tkinter import messagebox, ttk
from PIL import Image, ImageTk, ImageFilter, ImageDraw
import sqlite3

# ============================================================
#  VELS ERP — Original logic fully preserved, UI upgraded
# ============================================================

# ─── THEME PATCH (applied before any widgets) ───
BG      = "#0D1117"
PANEL   = "#161B22"
CARD    = "#1C2230"
LIGHT   = "#21262D"
WHITE   = "#F0F6FC"
DIM     = "#8B949E"
MUTED   = "#484F58"
BLUE    = "#58A6FF"
GREEN   = "#3FB950"
GOLD    = "#D29922"
RED     = "#F85149"
ORANGE  = "#FFA657"
PURPLE  = "#BC8CFF"
CYAN    = "#39C5CF"

def _patch_btn(b, color=BLUE):
    b.config(bg=color, fg=WHITE, activebackground=color,
             activeforeground=WHITE, relief=FLAT, cursor="hand2",
             font=("Segoe UI", 10), bd=0)
    b.bind("<Enter>", lambda e: b.config(bg=_lit(color)))
    b.bind("<Leave>", lambda e: b.config(bg=color))

def _lit(h):
    try:
        r,g,b2=[int(h.lstrip("#")[i:i+2],16) for i in (0,2,4)]
        return "#%02x%02x%02x"%(min(r+30,255),min(g+30,255),min(b2+30,255))
    except: return h

def _patch_tree(tv):
    s=ttk.Style()
    s.theme_use("clam")
    s.configure("Vels.Treeview", background=CARD, foreground=WHITE,
                fieldbackground=CARD, rowheight=30, font=("Segoe UI",10))
    s.configure("Vels.Treeview.Heading", background=PANEL,
                foreground=BLUE, font=("Segoe UI",10,"bold"), relief=FLAT)
    s.map("Vels.Treeview", background=[("selected","#264F78")])
    tv.config(style="Vels.Treeview")
    tv.tag_configure("odd",  background="#1A2235")
    tv.tag_configure("even", background=CARD)

def _patch_entry(e):
    e.config(bg=LIGHT, fg=WHITE, insertbackground=WHITE,
             relief=FLAT, highlightthickness=1,
             highlightbackground="#30363D", highlightcolor=BLUE,
             font=("Segoe UI",10))

# ─────────────────────────────────────────────
#  MAIN WINDOW
# ─────────────────────────────────────────────
root = Tk()
root.title("VELS ERP")
try:    root.attributes("-zoomed", True)
except: pass
root.configure(bg=BG)

# ─── DATABASE (original) ───
def get_db():
    return sqlite3.connect("erp.db")

def create_tables():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, regno TEXT UNIQUE,
            dept TEXT, course TEXT DEFAULT '',
            marks TEXT DEFAULT '', attendance TEXT DEFAULT ''
        )""")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS staffs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, dept TEXT, position TEXT
        )""")
    conn.commit(); conn.close()

create_tables()

# ─── BACKGROUND (original logic) ───
try:
    bg = Image.open("vels_logo.jpg.jpeg")
    bg = bg.resize((root.winfo_screenwidth(), root.winfo_screenheight()))
    bg = bg.filter(ImageFilter.GaussianBlur(8))
    # darken overlay so text is readable
    dark = Image.new("RGBA", bg.size, (0,0,0,160))
    bg = bg.convert("RGBA")
    bg = Image.alpha_composite(bg, dark).convert("RGB")
    bg_photo = ImageTk.PhotoImage(bg)
    Label(root, image=bg_photo).place(relwidth=1, relheight=1)
except:
    root.config(bg=BG)

# ─── ROUND LOGO (original logic) ───
try:
    size = 120
    img = Image.open("vels_logo.jpg.jpeg").resize((size, size))
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0,0,size,size), fill=255)
    img.putalpha(mask)
    logo = ImageTk.PhotoImage(img)
    frame_logo = Frame(root, bg=BLUE, bd=2)
    frame_logo.place(x=20, y=20)
    Label(frame_logo, image=logo, bg=CARD).pack()
except:
    pass

# ─── TOP ACCENT BAR ───
Frame(root, bg=BLUE, height=4).place(relx=0, rely=0, relwidth=1)

# ─── LOGIN CARD (original structure, styled) ───
card = Frame(root, bg=CARD, padx=40, pady=30)
card.place(relx=0.5, rely=0.5, anchor="center")

Label(card, text="🎓", font=("Segoe UI",36), bg=CARD, fg=BLUE).pack()
Label(card, text="VELS ERP", font=("Segoe UI",22,"bold"), bg=CARD, fg=WHITE).pack()
Label(card, text="Vels Institute of Science, Technology & Advanced Studies",
      font=("Segoe UI",8), bg=CARD, fg=DIM).pack(pady=(2,16))

Frame(card, bg=MUTED, height=1).pack(fill=X, pady=(0,14))

row1 = Frame(card, bg=CARD); row1.pack(pady=5, fill=X)
Label(row1, text="Username / ID", bg=CARD, fg=DIM, font=("Segoe UI",9), anchor=W).pack(fill=X)
user_entry = Entry(row1, width=30, bg="yellow")
user_entry.pack(fill=X, ipady=8, pady=(2,0))
_patch_entry(user_entry)

row2 = Frame(card, bg=CARD); row2.pack(pady=5, fill=X)
Label(row2, text="Password", bg=CARD, fg=DIM, font=("Segoe UI",9), anchor=W).pack(fill=X)
pass_entry = Entry(row2, width=30, show="*", bg="yellow")
pass_entry.pack(fill=X, ipady=8, pady=(2,0))
_patch_entry(pass_entry); pass_entry.config(show="●")

login_btn = Button(card, text="  Sign In  →", width=30, height=1)
login_btn.pack(pady=(14,0), fill=X, ipady=6)
_patch_btn(login_btn, BLUE)
Label(card, text="Admin: ADMIN / 1234  •  Student: NAME / RegNo",
      font=("Segoe UI",8), bg=CARD, fg=MUTED).pack(pady=(8,0))

user_entry.focus()

# ─────────────────────────────────────────────
#  ADMIN PANEL  (original logic, styled)
# ─────────────────────────────────────────────
def open_admin_panel():
    win = Toplevel(root)
    win.title("VELS ERP — Admin")
    try:    win.attributes("-zoomed", True)
    except: pass
    win.configure(bg=BG)

    # ── Sidebar ──
    sidebar = Frame(win, bg=PANEL, width=190)
    sidebar.pack(side=LEFT, fill=Y)
    sidebar.pack_propagate(False)

    sb_top = Frame(sidebar, bg=BLUE, pady=14); sb_top.pack(fill=X)
    try: Label(sb_top, image=logo, bg=BLUE).pack()
    except: pass
    Label(sb_top, text="VELS ERP", font=("Segoe UI",12,"bold"),
          bg=BLUE, fg=WHITE).pack(pady=(4,0))
    Label(sb_top, text="Admin Panel", font=("Segoe UI",8),
          bg=BLUE, fg="#cce4ff").pack()

    Frame(sidebar, bg=MUTED, height=1).pack(fill=X, pady=4)

    # ── Main area ──
    main_area = Frame(win, bg=BG)
    main_area.pack(side=LEFT, fill=BOTH, expand=True)

    topbar = Frame(main_area, bg=PANEL, height=46)
    topbar.pack(fill=X); topbar.pack_propagate(False)
    page_lbl = Label(topbar, text="Dashboard", font=("Segoe UI",14,"bold"),
                     fg=WHITE, bg=PANEL)
    page_lbl.pack(side=LEFT, padx=16, pady=10)

    # ── main_frame equivalent ──
    main_frame = Frame(main_area, bg=BG)
    main_frame.pack(fill=BOTH, expand=True, padx=12, pady=10)

    def clear_main_frame():
        for w in main_frame.winfo_children(): w.destroy()

    # ── DASHBOARD (original logic) ──
    DEPT_COLORS = {
        "CSE": BLUE, "Electronics": GOLD, "Mechanical": RED,
        "Civil": GREEN, "Biotechnology": PURPLE, "Management": CYAN,
    }

    def show_dashboard():
        clear_main_frame(); page_lbl.config(text="Dashboard")
        Label(main_frame, text="Departments in VELS University",
              font=("Segoe UI",13,"bold"), bg=BG, fg=WHITE).pack(pady=(4,12), anchor=W)

        grid = Frame(main_frame, bg=BG); grid.pack(fill=X)
        depts = ["CSE","Electronics","Mechanical","Civil","Biotechnology","Management"]
        for i, d in enumerate(depts):
            color = DEPT_COLORS.get(d, BLUE)
            outer = Frame(grid, bg=color, padx=1, pady=1)
            outer.grid(row=i//3, column=i%3, padx=8, pady=8, sticky=EW)
            grid.columnconfigure(i%3, weight=1)
            inner = Frame(outer, bg=CARD, padx=16, pady=14); inner.pack(fill=BOTH)
            Label(inner, text=d, font=("Segoe UI",13,"bold"),
                  fg=color, bg=CARD).pack(anchor=W)
            conn = get_db()
            cnt = conn.execute("SELECT COUNT(*) FROM students WHERE dept=?",(d,)).fetchone()[0]
            conn.close()
            Label(inner, text=f"{cnt} students", font=("Segoe UI",9),
                  fg=DIM, bg=CARD).pack(anchor=W, pady=(2,8))
            b = Button(inner, text="Manage →", font=("Segoe UI",9),
                       command=lambda dept=d: view_students_by_dept(dept))
            b.pack(anchor=W)
            _patch_btn(b, color)

    # ── STAFF (original logic) ──
    def show_staffs():
        clear_main_frame(); page_lbl.config(text="Staff Management")

        body = Frame(main_frame, bg=BG); body.pack(fill=BOTH, expand=True)

        form = Frame(body, bg=CARD, padx=16, pady=16, width=230)
        form.pack(side=LEFT, fill=Y, padx=(0,10)); form.pack_propagate(False)
        Label(form, text="Staff Form", font=("Segoe UI",11,"bold"),
              fg=GREEN, bg=CARD).pack(pady=(0,10))

        staff_name = Entry(form, width=22); staff_dept = Entry(form, width=22)
        staff_pos  = Entry(form, width=22)
        for lbl_txt, e in [("Name",staff_name),("Dept",staff_dept),("Position",staff_pos)]:
            Label(form, text=lbl_txt, font=("Segoe UI",9),
                  fg=DIM, bg=CARD, anchor=W).pack(fill=X, pady=(6,0))
            e.pack(fill=X, ipady=5); _patch_entry(e)

        table_f = Frame(body, bg=BG); table_f.pack(side=LEFT, fill=BOTH, expand=True)
        staff_table = ttk.Treeview(table_f, columns=("Name","Dept","Position"), show="headings")
        staff_table.pack(fill=BOTH, expand=True)
        _patch_tree(staff_table)
        for col, w in [("Name",170),("Dept",140),("Position",160)]:
            staff_table.heading(col, text=col); staff_table.column(col, width=w, anchor=CENTER)

        def load_staffs():
            staff_table.delete(*staff_table.get_children())
            conn=get_db(); cursor=conn.cursor()
            cursor.execute("SELECT name,dept,position FROM staffs")
            for i,r in enumerate(cursor.fetchall()):
                staff_table.insert("",END,values=r,tags=("odd" if i%2 else "even",))
            conn.close()
        load_staffs()

        def select_staff(event):
            values = staff_table.item(staff_table.focus(),"values")
            if not values: return
            staff_name.delete(0,END); staff_name.insert(0,values[0])
            staff_dept.delete(0,END); staff_dept.insert(0,values[1])
            staff_pos.delete(0,END);  staff_pos.insert(0,values[2])
        staff_table.bind("<ButtonRelease-1>", select_staff)

        def add_staff():
            conn=get_db(); cursor=conn.cursor()
            cursor.execute("INSERT INTO staffs VALUES(NULL,?,?,?)",
                           (staff_name.get(),staff_dept.get(),staff_pos.get()))
            conn.commit(); conn.close()
            messagebox.showinfo("✅ Added","Staff Added"); load_staffs()

        def update_staff():
            values=staff_table.item(staff_table.focus(),"values")
            if not values: return
            conn=get_db(); cursor=conn.cursor()
            cursor.execute("UPDATE staffs SET name=?,dept=?,position=? WHERE name=? AND dept=?",
                           (staff_name.get(),staff_dept.get(),staff_pos.get(),values[0],values[1]))
            conn.commit(); conn.close()
            messagebox.showinfo("✅ Updated","Staff Updated"); load_staffs()

        def delete_staff():
            values=staff_table.item(staff_table.focus(),"values")
            if not values: return
            conn=get_db(); cursor=conn.cursor()
            cursor.execute("DELETE FROM staffs WHERE name=? AND dept=?",(values[0],values[1]))
            conn.commit(); conn.close()
            messagebox.showinfo("🗑 Deleted","Staff Removed"); load_staffs()

        for txt, color, cmd in [("➕ Add",GREEN,add_staff),
                                 ("✏️ Update",GOLD,update_staff),
                                 ("🗑 Delete",RED,delete_staff)]:
            b = Button(form, text=txt, font=("Segoe UI",10), width=18)
            b.pack(fill=X, pady=3, ipady=4); _patch_btn(b, color)
            b.config(command=cmd)

    # ── STUDENTS BY DEPT (original logic) ──
    def view_students_by_dept(dept_name):
        clear_main_frame()
        page_lbl.config(text=f"Students — {dept_name}")
        color = DEPT_COLORS.get(dept_name, BLUE)

        hdr = Frame(main_frame, bg=BG); hdr.pack(fill=X, pady=(0,8))
        Label(hdr, text=f"📚 {dept_name}", font=("Segoe UI",13,"bold"),
              fg=color, bg=BG).pack(side=LEFT)
        back_b = Button(hdr, text="← Dashboard", font=("Segoe UI",9),
                        command=show_dashboard)
        back_b.pack(side=RIGHT); _patch_btn(back_b, LIGHT)

        body = Frame(main_frame, bg=BG); body.pack(fill=BOTH, expand=True)

        form = Frame(body, bg=CARD, padx=16, pady=16, width=230)
        form.pack(side=LEFT, fill=Y, padx=(0,10)); form.pack_propagate(False)
        Label(form, text="Student Form", font=("Segoe UI",11,"bold"),
              fg=color, bg=CARD).pack(pady=(0,10))

        name=Entry(form,width=22); reg=Entry(form,width=22)
        dept=Entry(form,width=22); course=Entry(form,width=22)
        marks=Entry(form,width=22); att=Entry(form,width=22)

        for lbl_txt, e, default in [
            ("Name",name,""), ("Reg No",reg,""), ("Dept",dept,dept_name),
            ("Course",course,""), ("Marks",marks,""), ("Attendance",att,"")
        ]:
            Label(form, text=lbl_txt, font=("Segoe UI",9),
                  fg=DIM, bg=CARD, anchor=W).pack(fill=X, pady=(6,0))
            e.pack(fill=X, ipady=5); _patch_entry(e)
            if default: e.insert(0, default)

        # Table side
        table_f = Frame(body, bg=BG); table_f.pack(side=LEFT, fill=BOTH, expand=True)

        # Search bar (bonus, non-breaking)
        sf = Frame(table_f, bg=BG); sf.pack(fill=X, pady=(0,6))
        Label(sf, text="🔍", fg=DIM, bg=BG, font=("Segoe UI",10)).pack(side=LEFT)
        sv = StringVar()
        se = Entry(sf, textvariable=sv, width=26); se.pack(side=LEFT, padx=4, ipady=4)
        _patch_entry(se)

        table = ttk.Treeview(table_f,
            columns=("Name","Reg","Dept","Course","Marks","Attendance"),
            show="headings")
        table.pack(fill=BOTH, expand=True)
        _patch_tree(table)
        for col, w in [("Name",150),("Reg",100),("Dept",80),
                       ("Course",140),("Marks",80),("Attendance",100)]:
            table.heading(col, text=col); table.column(col, width=w, anchor=CENTER)

        def load_data(filter_txt=""):
            table.delete(*table.get_children())
            conn=get_db(); cursor=conn.cursor()
            cursor.execute(
                "SELECT name,regno,dept,course,marks,attendance FROM students WHERE dept=?",
                (dept_name,))
            rows = cursor.fetchall(); conn.close()
            if filter_txt:
                rows = [r for r in rows if any(filter_txt.lower() in str(v).lower() for v in r)]
            for i,r in enumerate(rows):
                table.insert("",END,values=r,tags=("odd" if i%2 else "even",))

        sv.trace_add("write", lambda *a: load_data(sv.get()))
        load_data()

        def select_data(event):
            values=table.item(table.focus(),"values")
            if not values: return
            for e in [name,reg,dept,course,marks,att]: e.delete(0,END)
            name.insert(0,values[0]); reg.insert(0,values[1]); dept.insert(0,values[2])
            course.insert(0,values[3]); marks.insert(0,values[4]); att.insert(0,values[5])
        table.bind("<ButtonRelease-1>",select_data)

        def add_student():
            conn=get_db(); cursor=conn.cursor()
            try:
                cursor.execute("INSERT INTO students VALUES (NULL,?,?,?,?,?,?)",
                               (name.get().upper(),reg.get(),dept.get(),
                                course.get(),marks.get(),att.get()))
                conn.commit(); messagebox.showinfo("✅ Added","Student Added"); load_data()
            except: messagebox.showerror("Error","Student Exists / Invalid Input")
            conn.close()

        def update_student():
            conn=get_db(); cursor=conn.cursor()
            cursor.execute(
                "UPDATE students SET name=?,dept=?,course=?,marks=?,attendance=? WHERE regno=?",
                (name.get().upper(),dept.get(),course.get(),marks.get(),att.get(),reg.get()))
            conn.commit(); conn.close(); load_data()
            messagebox.showinfo("✅ Updated","Student Updated")

        def delete_student():
            values=table.item(table.focus(),"values")
            if not values: return
            conn=get_db(); cursor=conn.cursor()
            cursor.execute("DELETE FROM students WHERE regno=?",(values[1],))
            conn.commit(); conn.close(); load_data()
            messagebox.showinfo("🗑 Deleted","Student Removed")

        for txt, color2, cmd in [("➕ Add",GREEN,add_student),
                                  ("✏️ Update",GOLD,update_student),
                                  ("🗑 Delete",RED,delete_student)]:
            b = Button(form, text=txt, font=("Segoe UI",10), width=18)
            b.pack(fill=X, pady=3, ipady=4); _patch_btn(b, color2)
            b.config(command=cmd)

    # ── Sidebar nav buttons ──
    active_nb = [None]
    def _nav(b, title, fn):
        if active_nb[0]: active_nb[0].config(bg=PANEL, fg=DIM)
        b.config(bg=CARD, fg=WHITE); active_nb[0] = b
        page_lbl.config(text=title); fn()

    for txt, fn in [("📊  Dashboard", show_dashboard),
                    ("👨‍🏫  Staff",     show_staffs)]:
        nb = Button(sidebar, text=txt, font=("Segoe UI",10),
                    bg=PANEL, fg=DIM, relief=FLAT, anchor=W,
                    padx=16, pady=9, bd=0, cursor="hand2",
                    activebackground=CARD, activeforeground=WHITE)
        nb.config(command=lambda b=nb, f=fn, t=txt.strip(): _nav(b, t.split("  ")[-1], f))
        nb.pack(fill=X)

    Frame(sidebar, bg=MUTED, height=1).pack(fill=X, pady=8)
    logout_b = Button(sidebar, text="🚪  Logout", font=("Segoe UI",10), width=22)
    logout_b.pack(padx=10, pady=4, fill=X, ipady=4)
    _patch_btn(logout_b, RED); logout_b.config(command=win.destroy)

    show_dashboard()

# ─────────────────────────────────────────────
#  STUDENT LOGIN PANEL  (original logic, styled)
# ─────────────────────────────────────────────
def open_student_view(result):
    s_win = Toplevel(root)
    s_win.title("Student Dashboard")
    try:    s_win.attributes("-zoomed", True)
    except: pass
    s_win.configure(bg=BG)

    try:
        bg_student = Image.open("vels_logo.jpg.jpeg")
        bg_student = bg_student.resize((s_win.winfo_screenwidth(), s_win.winfo_screenheight()))
        bg_student = bg_student.filter(ImageFilter.GaussianBlur(8))
        dark2 = Image.new("RGBA", bg_student.size, (0,0,0,160))
        bg_student = Image.alpha_composite(bg_student.convert("RGBA"), dark2).convert("RGB")
        bg_student_photo = ImageTk.PhotoImage(bg_student)
        Label(s_win, image=bg_student_photo).place(relwidth=1, relheight=1)
        s_win.bg = bg_student_photo
    except:
        s_win.config(bg=BG)

    Frame(s_win, bg=BLUE, height=4).place(relx=0, rely=0, relwidth=1)

    # Original "VELS" label
    Label(s_win, text="VELS", font=("Arial",60,"bold"),
          fg=WHITE, bg=BG).place(relx=0.5, rely=0.1, anchor=CENTER)

    frame_info = Frame(s_win, bg=CARD, padx=36, pady=28, bd=0)
    frame_info.place(relx=0.5, rely=0.55, anchor=CENTER)

    Label(frame_info, text="🎓 STUDENT DETAILS", font=("Segoe UI",16,"bold"),
          bg=CARD, fg=BLUE).pack(pady=(0,12))
    Frame(frame_info, bg=MUTED, height=1).pack(fill=X, pady=(0,10))

    field_colors = [WHITE, CYAN, GOLD, GREEN, PURPLE, ORANGE]
    for idx, (field, color) in enumerate(
        zip(["Name","Reg No","Dept","Course","Marks","Attendance"], field_colors)
    ):
        row = Frame(frame_info, bg=CARD); row.pack(fill=X, pady=3)
        Label(row, text=f"{field}:", width=12, font=("Segoe UI",10),
              fg=DIM, bg=CARD, anchor=W).pack(side=LEFT)
        Label(row, text=str(result[idx+1]) if result[idx+1] else "—",
              font=("Segoe UI",11,"bold"), fg=color, bg=CARD).pack(side=LEFT, padx=8)

    Frame(frame_info, bg=MUTED, height=1).pack(fill=X, pady=10)
    exit_b = Button(frame_info, text="🚪 Logout", width=20)
    exit_b.pack(pady=(4,0), ipady=5)
    _patch_btn(exit_b, RED); exit_b.config(command=s_win.destroy)

# ─────────────────────────────────────────────
#  LOGIN  (original logic)
# ─────────────────────────────────────────────
def login():
    name  = user_entry.get().strip().upper()
    regno = pass_entry.get().strip()

    if name == "ADMIN" and regno == "1234":
        open_admin_panel(); return

    conn = get_db(); cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE name=? AND regno=?", (name, regno))
    result = cursor.fetchone(); conn.close()

    if result:
        open_student_view(result)
    else:
        messagebox.showerror("Error", "Invalid Login")

login_btn.config(command=login)
root.bind("<Return>", lambda e: login())

root.mainloop()
