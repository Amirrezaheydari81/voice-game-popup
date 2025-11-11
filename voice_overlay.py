import os, subprocess, threading, tkinter as tk, keyboard, ctypes
from ctypes import wintypes

# مسیر پوشه‌ها
VOICE_DIR = os.path.join(os.path.dirname(__file__), "voices")
FONT_PATH = os.path.join(os.path.dirname(__file__), "Vazirmatn-Regular.ttf")
os.makedirs(VOICE_DIR, exist_ok=True)

# --- پخش صدا با ffplay ---
current_process, lock = None, threading.Lock()
def stop_audio():
    global current_process
    with lock:
        if current_process and current_process.poll() is None:
            current_process.terminate()
            current_process = None

def play_audio(filename):
    global current_process
    path = os.path.join(VOICE_DIR, filename)
    with lock:
        if current_process and current_process.poll() is None:
            current_process.terminate()
        current_process = subprocess.Popen(
            ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", path],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

# --- GUI ---
root = tk.Tk()
root.geometry("360x700+60+60")
root.overrideredirect(True)
root.attributes("-topmost", True)
root.attributes("-alpha", 0.7)
root.configure(bg="#000000")

# فونت سفارشی
try:
    FR_PRIVATE = 0x10
    ctypes.windll.gdi32.AddFontResourceExW(FONT_PATH, FR_PRIVATE, 0)
    fname = "Vazirmatn Regular"
except Exception:
    fname = "Tahoma"
font_item = (fname, 10, "bold")
font_title = (fname, 13, "bold")

# قاب گرد مینیمال
container = tk.Canvas(root, bg="#000000", highlightthickness=0)
container.place(relwidth=1, relheight=1)
round_box = container.create_rectangle(8, 8, 352, 692, outline="#1f1f1f", fill="#111111", width=2)

# عنوان و شمارنده
title = tk.Label(root, text=" ویس های میم | TG: iPsar ", fg="white", bg="#111111", font=font_title)
title.place(x=0, y=10, relwidth=1)
counter = tk.Label(root, fg="#aaaaaa", bg="#111111", font=font_item)
counter.place(x=0, y=40, relwidth=1)

# فیلد جستجو
search_var = tk.StringVar()
search_entry = tk.Entry(root, textvariable=search_var, fg="#ffffff", bg="#222222",
                        insertbackground="#ffffff", font=font_item, justify="right", relief="flat")
search_entry.place(x=30, y=65, width=300, height=26)

# ناحیه لیست
canvas = tk.Canvas(root, bg="#111111", highlightthickness=0, bd=0)
scroll = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=scroll.set)
scroll.place(relx=0.97, rely=0.15, relheight=0.8)
canvas.place(x=16, y=100, width=325, height=580)
inner = tk.Frame(canvas, bg="#111111")
canvas.create_window((0, 0), window=inner, anchor="ne")

# فایل‌ها
files = [f for f in os.listdir(VOICE_DIR) if f.lower().endswith((".mp3", ".wav", ".ogg", ".opus"))]
files.sort()
current_files = files[:]  # همیشه لیست فعلیِ فیلتر شده
selected_index = 0
labels = []

# ساخت و نمایش لیست فیلتر شده
def populate(filter_text=""):
    global current_files, selected_index
    for lbl in labels:
        lbl.destroy()
    labels.clear()

    t = filter_text.strip().lower()
    if not t:
        filtered = files[:]
    else:
        head = [f for f in files if f.lower().startswith(t)]
        tail = [f for f in files if (t in f.lower()) and not f.lower().startswith(t)]
        filtered = head + tail

    current_files = filtered
    selected_index = 0

    for f in current_files:
        name, _ = os.path.splitext(f)
        lbl = tk.Label(inner, text=name, bg="#111111", fg="#dddddd",
                       anchor="e", justify="right", font=font_item, padx=12, pady=6)
        lbl.pack(fill="x", pady=2, anchor="e")
        labels.append(lbl)

    inner.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))
    canvas.yview_moveto(0)
    counter.config(text=f"{len(current_files)} صدا یافت شد")
    refresh_selection()

# تغییر ظاهر انتخاب
def refresh_selection():
    for i, lbl in enumerate(labels):
        if i == selected_index:
            lbl.config(bg="#000000", fg="#FFB22C")
        else:
            lbl.config(bg="#111111", fg="#bbbbbb")
    if labels:
        canvas.yview_moveto(selected_index / max(1, len(labels)))

# حرکت در لیست
def move_selection(offset):
    global selected_index
    if not current_files: return
    selected_index = max(0, min(len(current_files) - 1, selected_index + offset))
    refresh_selection()

# پخش صدای انتخاب شده
def play_selected():
    if 0 <= selected_index < len(current_files):
        threading.Thread(target=play_audio, args=(current_files[selected_index],), daemon=True).start()

# سرچ زنده
def on_search(*_):
    populate(search_var.get())

search_var.trace_add("write", on_search)

# شروع اولیه
populate()

# Hotkeys
keyboard.add_hotkey("ctrl+alt+up", lambda: move_selection(-1))
keyboard.add_hotkey("ctrl+alt+down", lambda: move_selection(1))
keyboard.add_hotkey("ctrl+alt+p", play_selected)
keyboard.add_hotkey("ctrl+alt+o", stop_audio)
keyboard.add_hotkey("ctrl+alt+q", lambda: root.destroy())

# شفاف و بدون فوکوس (Overlay واقعی)
GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x80000
WS_EX_TRANSPARENT = 0x20
WS_EX_NOACTIVATE = 0x08000000
hwnd = wintypes.HWND(ctypes.windll.user32.FindWindowW(None, "Voice Overlay"))
style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE,
    style | WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_NOACTIVATE)

counter.config(text=f"{len(current_files)} صدا یافت شد")
refresh_selection()

root.mainloop()
