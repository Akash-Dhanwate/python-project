import os
import json
import random
import time
import platform
import datetime
import sqlite3
import tkinter.font as tkfont
from tkinter import *
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import qrcode

system = platform.system()
if system == "Windows":
    try:
        import winsound
    except Exception:
        winsound = None
else:
    try:
        from playsound import playsound
    except Exception:
        playsound = None

def play_sound(kind):
    """Play short system sound (Windows) or try playsound if available."""
    try:
        if system == "Windows" and 'winsound' in globals() and winsound:
            if kind == 'save':
                winsound.MessageBeep(winsound.MB_OK)
            elif kind == 'delete':
                winsound.MessageBeep(winsound.MB_ICONHAND)
            elif kind == 'error':
                winsound.MessageBeep(winsound.MB_ICONSTOP)
            elif kind == 'qr':
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            else:
                winsound.MessageBeep()
        else:
            if 'playsound' in globals() and playsound:
                fn = f"{kind}.wav"
                if os.path.exists(fn):
                    # non-blocking behavior not guaranteed, but we attempt
                    playsound(fn)
    except Exception:
        pass

# ---------- DATABASE (SQLite) ----------
DB_FILE = "hospital.db"

def get_db_conn():
    conn = sqlite3.connect(DB_FILE, timeout=5, check_same_thread=False)
    return conn

def ensure_tables():
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS hospital (
      nameoftablets TEXT,
      Refrence TEXT,
      dose TEXT,
      nooftablets TEXT,
      issuedate TEXT,
      expdate TEXT,
      dailydose TEXT,
      sideeffect TEXT,
      nameofpatient TEXT,
      dob TEXT,
      patientaddress TEXT
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS audit_log (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      operator_name TEXT,
      operator_role TEXT,
      action TEXT,
      ref_val TEXT,
      ts TEXT
    );
    """)
    conn.commit()
    cur.close()
    conn.close()

def log_audit_sql(operator_name, operator_role, action, ref_val=None):
    try:
        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute("INSERT INTO audit_log (operator_name, operator_role, action, ref_val, ts) VALUES (?, ?, ?, ?, ?)",
                    (operator_name, operator_role, action, ref_val, datetime.datetime.now().isoformat()))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print("Audit write failed:", e)

def insert_hospital_row(values_tuple):
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO hospital (nameoftablets, Refrence, dose, nooftablets, issuedate, expdate, dailydose, sideeffect, nameofpatient, dob, patientaddress)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, values_tuple)
    conn.commit()
    cur.close()
    conn.close()

def fetch_all_rows():
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("""
      SELECT nameoftablets, Refrence, dose, nooftablets, issuedate, expdate, dailydose, sideeffect, nameofpatient, dob, patientaddress
      FROM hospital
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def delete_row_by_ref(ref_val):
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM hospital WHERE Refrence = ?", (ref_val,))
    conn.commit()
    cur.close()
    conn.close()

# ensure DB & tables exist immediately
ensure_tables()

# ---------- UI and feature code ----------
win = Tk()
win.title("Hospital Management System — Offline (SQLite)")
win.state('zoomed')

# Fonts & styles
base_font = tkfont.Font(family="Segoe UI", size=11)
title_font = tkfont.Font(family="Segoe UI Semibold", size=22)
section_font = tkfont.Font(family="Segoe UI", size=12, weight="bold")
label_font = tkfont.Font(family="Segoe UI", size=10)
text_font = tkfont.Font(family="Consolas", size=10)

style = ttk.Style()
try:
    style.theme_use('clam')
except Exception:
    pass
style.configure('TButton', font=base_font, padding=6)
style.configure('TLabel', background='#f2f4f7', font=label_font)
style.configure('Card.TFrame', background='white', relief='flat')
style.configure('Treeview', font=base_font, rowheight=24)
style.configure('Treeview.Heading', font=('Segoe UI Semibold', 11))

# Operator info
OPERATOR_NAME = None
OPERATOR_ROLE = None
ROLES = ['Operator', 'Pharmacist', 'Reception', 'Supervisor', 'Data Clerk']

# Particle background canvas
particle_canvas = Canvas(win, highlightthickness=0)
particle_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
PARTICLE_COUNT = 20
particles = []

def init_particles():
    particle_canvas.delete("all")
    global particles
    particles = []
    w = win.winfo_width() or win.winfo_screenwidth()
    h = win.winfo_height() or win.winfo_screenheight()
    for _ in range(PARTICLE_COUNT):
        x = random.randint(0, w)
        y = random.randint(0, h)
        r = random.randint(6, 18)
        dx = random.choice([-1, -0.5, 0.5, 1])
        dy = random.choice([-0.6, -0.3, 0.3, 0.6])
        color = random.choice(['#e6f2ff', '#fff1e6', '#eafbe7', '#f7e6ff', '#fff4f4'])
        id_ = particle_canvas.create_oval(x-r, y-r, x+r, y+r, fill=color, outline='')
        particles.append({'id': id_, 'x': x, 'y': y, 'r': r, 'dx': dx, 'dy': dy, 'color': color})

def animate_particles():
    w = win.winfo_width() or win.winfo_screenwidth()
    h = win.winfo_height() or win.winfo_screenheight()
    for p in particles:
        p['x'] += p['dx']; p['y'] += p['dy']
        if p['x'] < -50: p['x'] = w + 50
        if p['x'] > w + 50: p['x'] = -50
        if p['y'] < -50: p['y'] = h + 50
        if p['y'] > h + 50: p['y'] = -50
        id_ = p['id']; r = p['r']
        particle_canvas.coords(id_, p['x']-r, p['y']-r, p['x']+r, p['y']+r)
    win.after(60, animate_particles)

# Themes
themes = {
    'morning': {'bg_win': '#fffaf0', 'card': '#ffffff', 'accent': '#f39c12', 'text': '#1b1b1b'},
    'afternoon': {'bg_win': '#f2f8ff', 'card': '#ffffff', 'accent': '#2b6cb0', 'text': '#1b1b1b'},
    'night': {'bg_win': '#0f1724', 'card': '#111827', 'accent': '#7c3aed', 'text': '#e6eef8'}
}
current_theme = 'afternoon'

def pick_theme_by_time():
    h = time.localtime().tm_hour
    if 6 <= h < 12:
        return 'morning'
    elif 12 <= h < 19:
        return 'afternoon'
    else:
        return 'night'

def apply_theme(theme_name):
    global current_theme
    th = themes.get(theme_name, themes['afternoon'])
    current_theme = theme_name
    win.configure(bg=th['bg_win'])
    particle_canvas.configure(bg=th['bg_win'])
    try:
        title_bar.configure(bg=th['accent'])
        title_label.configure(background=th['accent'], foreground='white')
    except Exception:
        pass
    style.configure('TLabel', background=th['bg_win'], foreground=th['text'])

def ripple_theme(accent_color):
    """
    Show a short translucent overlay flash using a Canvas and fade it out.
    Fixed: use overlay.tkraise() instead of overlay.lift() to raise the widget,
    and ensure the overlay is destroyed at the end.
    """
    overlay = Canvas(win, highlightthickness=0, bg=accent_color)
    overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
    steps = 8

    def fade_out(step=0):
        # remove overlay at the end
        if step >= steps:
            try:
                overlay.destroy()
            except Exception:
                pass
            return

        # ensure widget is on top (use tkraise to raise the widget, not canvas item)
        try:
            overlay.tkraise()
        except Exception:
            # defensive: if tkraise isn't available for some reason, ignore
            pass

        # schedule next fade step (the visual fade is simulated by timing; this
        # overlay uses a solid color — we keep it simple and just remove it quickly)
        win.after(40, lambda: fade_out(step + 1))

    # start the animation
    fade_out(0)

# Assistant (operator)
# assistant_frame = None
# assistant_text = None
# assistant_avatar = None
# assistant_messages = []

# def init_assistant():
#     global assistant_frame, assistant_text, assistant_avatar
#     assistant_frame = Frame(win, bd=0, bg='#ffffff', relief=RIDGE)
#     assistant_frame.place(relx=0.78, rely=0.72, relwidth=0.2, relheight=0.18)
#     assistant_avatar = Label(assistant_frame, text="🤖", font=("Segoe UI Emoji", 28), bg='#ffffff')
#     assistant_avatar.pack(side=LEFT, padx=(8,6), pady=8)
#     assistant_text = Text(assistant_frame, height=4, wrap=WORD, bd=0, font=('Segoe UI', 9))
#     assistant_text.insert(END, "Operator assistant ready. Please login.\n")
#     assistant_text.config(state='disabled', bg='#ffffff')
#     assistant_text.pack(side=LEFT, fill=BOTH, expand=True, padx=(0,8), pady=8)

# def assistant_say(text):
#     display = f"{OPERATOR_NAME or 'Operator'} ({OPERATOR_ROLE or '—'}): {text}"
#     assistant_messages.append(display)
#     try:
#         assistant_text.config(state='normal')
#         assistant_text.insert(END, display + "\n")
#         assistant_text.config(state='disabled')
#         assistant_text.see(END)
#     except Exception:
#         pass
    # # avatar pulse
    # def pulse(count=0):
    #     if count >= 6:
    #         assistant_avatar.config(font=("Segoe UI Emoji", 28))
    #         return
    #     size = 28 + (2 if count % 2 == 0 else 0)
    #     assistant_avatar.config(font=("Segoe UI Emoji", size))
    #     win.after(90, lambda: pulse(count+1))
    # pulse()

# QR helpers
def generate_qr(reference, tablet_name, patient_name):
    if not reference:
        raise ValueError("Reference is empty.")
    payload = {"ref": str(reference), "tablet": str(tablet_name), "patient": str(patient_name)}
    data = json.dumps(payload)
    img = qrcode.make(data)
    safe_ref = "".join(c for c in str(reference) if c.isalnum() or c in ('-', '_'))
    filename = f"qr_{safe_ref}.png"
    img.save(filename)
    return filename

def show_qr_popup():
    ref_val = ref.get().strip()
    if not ref_val:
        messagebox.showerror("Error", "Reference field is empty.")
        play_sound('error')
        # assistant_say("You tried to show a QR without a reference.")
        return
    safe_ref = "".join(c for c in str(ref_val) if c.isalnum() or c in ('-', '_'))
    filename = f"qr_{safe_ref}.png"
    try:
        if not os.path.exists(filename):
            generate_qr(ref_val, nameoftablets.get(), nameofpatient.get())
    except Exception as e:
        messagebox.showerror("QR Error", f"Could not generate QR: {e}")
        play_sound('error')
        # assistant_say("QR generation failed.")
        return
    popup = Toplevel(win)
    popup.title(f"QR — {ref_val}")
    popup.geometry("360x420")
    popup.config(bg=themes[current_theme]['bg_win'])
    try:
        pil_img = Image.open(filename)
        max_side = 340
        if max(pil_img.size) > max_side:
            ratio = max_side / float(max(pil_img.size))
            new_size = (int(pil_img.size[0] * ratio), int(pil_img.size[1] * ratio))
            pil_img = pil_img.resize(new_size)
        img_tk = ImageTk.PhotoImage(pil_img)
        lbl = Label(popup, image=img_tk, bg=themes[current_theme]['bg_win'])
        lbl.image = img_tk
        lbl.pack(pady=12)
        txt = Text(popup, height=4, width=40)
        txt.insert(END, json.dumps({"ref": ref_val, "tablet": nameoftablets.get(), "patient": nameofpatient.get()}, indent=2))
        txt.config(state='disabled')
        txt.pack(padx=10, pady=(0,12))
        play_sound('qr')
        # assistant_say(f"Displayed QR for {ref_val}.")
        log_audit_sql(OPERATOR_NAME or 'N/A', OPERATOR_ROLE or 'N/A', "show_qr", ref_val)
    except Exception as e:
        messagebox.showerror("Preview Error", f"Could not open QR image: {e}")
        play_sound('error')
        # assistant_say("Could not preview QR.")

# ---------- DB-backed behaviors (SQLite) ----------
import traceback
import pathlib

def write_error_log(exc):
    """Append full traceback + timestamp to error.log for debugging."""
    try:
        p = pathlib.Path(__file__).parent if '__file__' in globals() else pathlib.Path.cwd()
        log_path = p / "error.log"
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"\n=== {datetime.datetime.now().isoformat()} ===\n")
            f.write(exc)
            f.write("\n")
    except Exception:
        # If logging fails, print to console as fallback
        print("Failed to write error.log", exc)

def pd():
    """Save record to SQLite (robust version with logging & sanity checks)."""
    # Basic required fields
    if nameoftablets.get().strip() == "" or ref.get().strip() == "":
        messagebox.showerror("Error", "Name of Tablets and Reference No. are required")
        play_sound('error')
        # assistant_say("Please fill required fields before saving.")
        return

    try:
        # Sanity: check DB file can be created/written
        db_path = os.path.abspath(DB_FILE)
        db_dir = os.path.dirname(db_path)
        if not os.path.isdir(db_dir):
            raise Exception(f"Database directory does not exist: {db_dir}")
        # try to touch the DB file (will create if missing)
        try:
            open(db_path, "a").close()
        except Exception as e:
            raise Exception(f"Cannot create or write DB file at {db_path}: {e}")

        # Sanity: ensure tables exist
        ensure_tables()

        # Build parameter tuple (11 fields)
        params = (
            nameoftablets.get().strip(),
            ref.get().strip(),
            dose.get().strip(),
            nooftablets.get().strip(),
            issuedate.get().strip(),
            expdate.get().strip(),
            dailydose.get().strip(),
            sideeffect.get().strip(),
            nameofpatient.get().strip(),
            dob.get().strip(),
            patientaddress.get().strip()
        )

        # Optional: quick check that we have 11 values
        if len(params) != 11:
            raise Exception(f"Parameter length mismatch: expected 11, got {len(params)}")

        # Insert row
        insert_hospital_row(params)

        # Generate QR (best-effort)
        try:
            generate_qr(ref.get(), nameoftablets.get(), nameofpatient.get())
        except Exception as e:
            # don't block saving if QR generation fails
            print("QR generation failed:", e)

        # Refresh UI & notify user
        fetch_data()
        play_sound('save')
        ripple_theme(themes[current_theme]['accent'])
        # assistant_say(f"Saved prescription {ref.get()}.")
        log_audit_sql(OPERATOR_NAME or 'N/A', OPERATOR_ROLE or 'N/A', "save", ref.get())

    except Exception as ex:
        # Build full traceback and write to error.log
        tb = traceback.format_exc()
        write_error_log(tb)

        # Show user-friendly message + small hint, not raw traceback
        message = (
            "Database Error — save failed.\n\n"
            "What happened: the app could not save the record to the local database.\n\n"
            "Quick checks you can try:\n"
            "• Ensure the program folder is writable (run Python as normal user).\n"
            "• Make sure hospital.db is not open/locked by another program.\n"
            "• If antivirus blocks file creation, allow the folder.\n\n"
            "Detailed error has been written to error.log (in the app folder). "
            "If you'd like, copy the last lines from that file and paste them here and I will debug further."
        )
        # show message and log a short assistant note
        messagebox.showerror("Database Error", message)
        play_sound('error')
        # assistant_say("Save failed — details written to error.log.")
        # also print traceback to console for convenience
        print(tb)


def fetch_data():
    try:
        rows = fetch_all_rows()
        table.delete(*table.get_children())
        for row in rows:
            table.insert('', END, values=row)
    except Exception as e:
        # assistant_say("Could not fetch DB rows.")
        print("Fetch error:", e)

def get_data(event=''):
    try:
        cursor_row = table.focus()
        if not cursor_row:
            return
        data = table.item(cursor_row)
        row = data.get('values')
        if not row:
            return
        nameoftablets.set(row[0]); ref.set(row[1]); dose.set(row[2]); nooftablets.set(row[3])
        issuedate.set(row[4]); expdate.set(row[5]); dailydose.set(row[6]); sideeffect.set(row[7])
        nameofpatient.set(row[8]); dob.set(row[9]); patientaddress.set(row[10])
        # assistant_say(f"Loaded record {ref.get()} into form.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load row: {e}")
        play_sound('error')
        # assistant_say("Failed to load selected row.")
# 
def delete():
    if not ref.get().strip():
        messagebox.showerror("Error", "Select or enter Reference No. to delete")
        play_sound('error')
        # assistant_say("Provide a reference to delete.")
        return
    try:
        delete_row_by_ref(ref.get().strip())
        fetch_data()
        play_sound('delete')
        # assistant_say(f"Deleted record {ref.get()}.")
        log_audit_sql(OPERATOR_NAME or 'N/A', OPERATOR_ROLE or 'N/A', "delete", ref.get())
    except Exception as e:
        messagebox.showerror("Database Error", f"{e}")
        play_sound('error')
        # assistant_say("Delete failed.")

def clear():
    nameoftablets.set(''); ref.set(''); dose.set(''); nooftablets.set('')
    issuedate.set(''); expdate.set(''); dailydose.set(''); sideeffect.set('')
    bloodpressure.set(''); storage.set(''); medication.set(''); patientid.set('')
    nameofpatient.set(''); dob.set(''); patientaddress.set('')
    txt_frme.delete(1.0, END)
    log_audit_sql(OPERATOR_NAME or 'N/A', OPERATOR_ROLE or 'N/A', "clear", None)
    play_sound('save')

def pre():
    txt_frme.delete(1.0, END)
    lines = [
        f"Name of Tablets:   {nameoftablets.get()}",
        f"Reference No.:     {ref.get()}",
        f"Dose:              {dose.get()}",
        f"No. of Tablets:    {nooftablets.get()}",
        f"Issue Date:        {issuedate.get()}",
        f"Exp Date:          {expdate.get()}",
        f"Daily Dose:        {dailydose.get()}",
        f"Side Effect:       {sideeffect.get()}",
        f"Blood Pressure:    {bloodpressure.get()}",
        f"Storage Device:    {storage.get()}",
        f"Medication:        {medication.get()}",
        f"Patient Id:        {patientid.get()}",
        f"Patient Name:      {nameofpatient.get()}",
        f"DOB:               {dob.get()}",
        f"Address:           {patientaddress.get()}",
    ]
    txt_frme.insert(END, "\n".join(lines))
    # assistant_say("Preview generated.")
    log_audit_sql(OPERATOR_NAME or 'N/A', OPERATOR_ROLE or 'N/A', "preview", ref.get())

def exit_app():
    if messagebox.askyesno('Confirmation', 'Are you sure you want to exit?'):
        win.destroy()

# ---------- UI building ----------
title_bar = Frame(win, bg='#2b6cb0', pady=10)
title_bar.place(relx=0.0, rely=0.0, relwidth=1.0, height=62)
title_label = Label(title_bar, text="Hospital Management System", font=title_font, fg='white', bg='#2b6cb0')
title_label.pack(side=LEFT, padx=18)

operator_label = Label(title_bar, text="Operator: —", font=('Segoe UI', 10, 'italic'), fg='white', bg='#2b6cb0')
operator_label.pack(side=RIGHT, padx=12)

def update_operator_display():
    operator_label.config(text=f"Operator: {OPERATOR_NAME or '—'} ({OPERATOR_ROLE or '—'})")

def toggle_theme():
    names = list(themes.keys())
    idx = names.index(current_theme)
    new = names[(idx + 1) % len(names)]
    apply_theme(new)
    # assistant_say(f"Theme switched to {new}.")

theme_btn = Button(title_bar, text="Theme", command=toggle_theme)
theme_btn.pack(side=RIGHT, padx=12)

content = ttk.Frame(win, padding=12, style='Card.TFrame')
content.place(relx=0.02, rely=0.12, relwidth=0.96, relheight=0.56)

left_card = ttk.Frame(content, style='Card.TFrame', padding=12)
left_card.grid(row=0, column=0, sticky='nsew', padx=(0,12))
right_card = ttk.Frame(content, style='Card.TFrame', padding=12)
right_card.grid(row=0, column=1, sticky='nsew')

content.columnconfigure(0, weight=1); content.columnconfigure(1, weight=1)
content.rowconfigure(0, weight=1)

# form variables
nameoftablets = StringVar(); ref = StringVar(); dose = StringVar(); nooftablets = StringVar()
issuedate = StringVar(); expdate = StringVar(); dailydose = StringVar(); sideeffect = StringVar()
bloodpressure = StringVar(); storage = StringVar(); medication = StringVar(); patientid = StringVar()
nameofpatient = StringVar(); dob = StringVar(); patientaddress = StringVar()

Label(left_card, text="Patient Information", font=section_font, background='white').grid(row=0, column=0, columnspan=4, sticky='w', pady=(0,8))
def make_label(r, c, text):
    lbl = ttk.Label(left_card, text=text, font=label_font)
    lbl.grid(row=r, column=c, sticky='w', padx=6, pady=6)

make_label(1, 0, "Name of Tablets"); e1 = ttk.Entry(left_card, textvariable=nameoftablets, font=base_font); e1.grid(row=1, column=1, sticky='ew', padx=6)
make_label(2, 0, "Reference No."); e2 = ttk.Entry(left_card, textvariable=ref, font=base_font); e2.grid(row=2, column=1, sticky='ew', padx=6)
make_label(3, 0, "Dose"); e3 = ttk.Entry(left_card, textvariable=dose, font=base_font); e3.grid(row=3, column=1, sticky='ew', padx=6)
make_label(4, 0, "No. of Tablets"); e4 = ttk.Entry(left_card, textvariable=nooftablets, font=base_font); e4.grid(row=4, column=1, sticky='ew', padx=6)
make_label(5, 0, "Issue Date"); e5 = ttk.Entry(left_card, textvariable=issuedate, font=base_font); e5.grid(row=5, column=1, sticky='ew', padx=6)
make_label(6, 0, "Exp Date"); e6 = ttk.Entry(left_card, textvariable=expdate, font=base_font); e6.grid(row=6, column=1, sticky='ew', padx=6)
make_label(7, 0, "Daily Dose"); e7 = ttk.Entry(left_card, textvariable=dailydose, font=base_font); e7.grid(row=7, column=1, sticky='ew', padx=6)
make_label(8, 0, "Side Effect"); e8 = ttk.Entry(left_card, textvariable=sideeffect, font=base_font); e8.grid(row=8, column=1, sticky='ew', padx=6)

make_label(1, 2, "Blood Pressure"); e9 = ttk.Entry(left_card, textvariable=bloodpressure, font=base_font); e9.grid(row=1, column=3, sticky='ew', padx=6)
make_label(2, 2, "Storage Device"); e10 = ttk.Entry(left_card, textvariable=storage, font=base_font); e10.grid(row=2, column=3, sticky='ew', padx=6)
make_label(3, 2, "Medication"); e11 = ttk.Entry(left_card, textvariable=medication, font=base_font); e11.grid(row=3, column=3, sticky='ew', padx=6)
make_label(4, 2, "Patient Id"); e12 = ttk.Entry(left_card, textvariable=patientid, font=base_font); e12.grid(row=4, column=3, sticky='ew', padx=6)
make_label(5, 2, "Name of Patient"); e13 = ttk.Entry(left_card, textvariable=nameofpatient, font=base_font); e13.grid(row=5, column=3, sticky='ew', padx=6)
make_label(6, 2, "DOB"); e14 = ttk.Entry(left_card, textvariable=dob, font=base_font); e14.grid(row=6, column=3, sticky='ew', padx=6)
make_label(7, 2, "Address"); e15 = ttk.Entry(left_card, textvariable=patientaddress, font=base_font); e15.grid(row=7, column=3, rowspan=2, sticky='nsew', padx=6)

left_card.columnconfigure(1, weight=1); left_card.columnconfigure(3, weight=1)

Label(right_card, text="Prescription", font=section_font, background='white').pack(anchor='w')
txt_frme = Text(right_card, font=text_font, bg='#fff9db', height=12, bd=1)
txt_frme.pack(fill=X, padx=6, pady=(6,12))

btn_frame = ttk.Frame(right_card, style='Card.TFrame')
btn_frame.pack(fill=X, padx=6, pady=(0,8))
save_btn = ttk.Button(btn_frame, text="Save", command=pd); save_btn.pack(side=LEFT, padx=6)
ttk.Button(btn_frame, text="Preview", command=pre).pack(side=LEFT, padx=6)
ttk.Button(btn_frame, text="Show QR", command=show_qr_popup).pack(side=LEFT, padx=6)
ttk.Button(btn_frame, text="Clear", command=clear).pack(side=LEFT, padx=6)
ttk.Button(btn_frame, text="Delete", command=delete).pack(side=LEFT, padx=6)
ttk.Button(btn_frame, text="Exit", command=exit_app).pack(side=RIGHT, padx=6)

table_frame = ttk.Frame(win, padding=12, style='Card.TFrame')
table_frame.place(relx=0.02, rely=0.70, relwidth=0.96, relheight=0.26)

scroll_x = ttk.Scrollbar(table_frame, orient=HORIZONTAL); scroll_x.pack(side='bottom', fill='x')
scroll_y = ttk.Scrollbar(table_frame, orient=VERTICAL); scroll_y.pack(side='right', fill='y')

table = ttk.Treeview(table_frame,
                     columns=('nameoftablets','Refrence','dose','nooftablets','issuedate','expdate','dailydose','sideeffect','nameofpatient','dob','patientaddress'),
                     xscrollcommand=scroll_x.set,
                     yscrollcommand=scroll_y.set,
                     show='headings')
scroll_x.config(command=table.xview); scroll_y.config(command=table.yview)

table.heading('nameoftablets', text='Name of Tablets'); table.column('nameoftablets', width=180)
table.heading('Refrence', text='Reference No.');    table.column('Refrence', width=120)
table.heading('dose', text='Dose');                  table.column('dose', width=90)
table.heading('nooftablets', text='No. of Tablets'); table.column('nooftablets', width=120)
table.heading('issuedate', text='Issue Date');       table.column('issuedate', width=110)
table.heading('expdate', text='Exp. date');          table.column('expdate', width=110)
table.heading('dailydose', text='Daily Dose');       table.column('dailydose', width=110)
table.heading('sideeffect', text='Side Effect');     table.column('sideeffect', width=160)
table.heading('nameofpatient', text='Patient Name'); table.column('nameofpatient', width=160)
table.heading('dob', text='DOB');                    table.column('dob', width=110)
table.heading('patientaddress', text='Patient Address'); table.column('patientaddress', width=260)

table.pack(fill=BOTH, expand=True)
table.bind('<ButtonRelease-1>', get_data)

# Operator sign-in dialog
def show_login_dialog():
    global OPERATOR_NAME, OPERATOR_ROLE
    dlg = Toplevel(win); dlg.title("Operator Login"); dlg.geometry("360x220"); dlg.transient(win); dlg.grab_set()
    Label(dlg, text="Sign in as Operator", font=('Segoe UI Semibold', 14)).pack(pady=(12,6))
    Label(dlg, text="Name:").pack(anchor='w', padx=16)
    name_entry = Entry(dlg); name_entry.pack(fill=X, padx=16)
    Label(dlg, text="Role:").pack(anchor='w', padx=16, pady=(8,0))
    role_var = StringVar(value=ROLES[0])
    role_menu = ttk.Combobox(dlg, values=ROLES, textvariable=role_var, state='readonly'); role_menu.pack(fill=X, padx=16)
    def do_login():
        nonlocal name_entry, role_var, dlg
        name = name_entry.get().strip()
        role = role_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Enter operator name.")
            return
        OPERATOR_NAME = name
        OPERATOR_ROLE = role
        update_operator_display()
        # assistant_say(f"{OPERATOR_NAME} signed in as {OPERATOR_ROLE}. Ready.")
        dlg.destroy()
    try:
        default_user = os.getlogin(); name_entry.insert(0, default_user)
    except Exception:
        pass
    Button(dlg, text="Sign in", command=do_login).pack(pady=14)
    dlg.wait_window()

# Init widgets & behaviors
init_particles(); animate_particles();
apply_theme(pick_theme_by_time())

# show login after short delay
win.after(150, lambda: show_login_dialog())

# load initial rows
try:
    fetch_data()
except Exception:
    pass

# handle resizing for particles
win.bind("<Configure>", lambda e: init_particles())

# keyboard shortcuts
def on_key(event):
    if event.state & 4 and event.keysym.lower() == 'q':  # Ctrl+Q
        show_qr_popup()
    if event.state & 4 and event.state & 1 and event.keysym.lower() == 'f':  # Ctrl+Shift+F
        if table_frame.winfo_viewable():
            table_frame.place_forget();
        else:
            table_frame.place(relx=0.02, rely=0.70, relwidth=0.96, relheight=0.26); 
win.bind_all("<Key>", on_key)

# assistant_say("Assistant ready. Please sign in.")
update_operator_display()

win.mainloop()

