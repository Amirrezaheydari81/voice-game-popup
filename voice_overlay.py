import os, subprocess, threading, tkinter as tk, keyboard, ctypes
from ctypes import wintypes

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

def play_selected():
    i = sel.get()
    if 0 <= i < len(files):
        threading.Thread(target=play_audio, args=(files[i],), daemon=True).start()

def move_selection(offset):
    if not files: return
    ni = max(0, min(len(files) - 1, sel.get() + offset))
    sel.set(ni)
    refresh_selection()

# --- GUI ---
root = tk.Tk()
root.geometry("360x700+60+60")
root.overrideredirect(True)
root.attributes("-topmost", True)
root.attributes("-alpha", 0.7)
root.configure(bg="#000000")

# فونت
try:
    import ctypes
    FR_PRIVATE = 0x10
    ctypes.windll.gdi32.AddFontResourceExW(FONT_PATH, FR_PRIVATE, 0)
    fname = "Vazirmatn Regular"
except:
    fname = "Tahoma"
font_item = (fname, 10, "bold")
font_title = (fname, 13, "bold")

# قاب اصلی با گوشه گرد
container = tk.Canvas(root, bg="#000000", highlightthickness=0)
container.place(relwidth=1, relheight=1)
round_box = container.create_rectangle(
    8, 8, 352, 692, outline="#222222", fill="#111111", width=0
)
container.itemconfig(round_box, width=2)
container.tk.call(container._w, "itemconfig", round_box, "-outline", "#1f1f1f")

# عنوان و شمارنده
title = tk.Label(root, text=" ویس های میم | TG: iPsar ", fg="white", bg="#111111", font=font_title)
title.place(x=0, y=10, relwidth=1)
counter = tk.Label(root, fg="#aaaaaa", bg="#111111", font=font_item)
counter.place(x=0, y=40, relwidth=1)

# Canvas محتوا
canvas = tk.Canvas(root, bg="#111111", highlightthickness=0, bd=0)
scroll = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=scroll.set)
scroll.place(relx=0.97, rely=0.15, relheight=0.8)
canvas.place(x=16, y=70, width=325, height=600)

inner = tk.Frame(canvas, bg="#111111")
canvas.create_window((0, 0), window=inner, anchor="ne")

# فایل‌ها
files = [f for f in os.listdir(VOICE_DIR)
         if f.lower().endswith((".mp3", ".wav", ".ogg", ".opus"))]
files.sort()
sel = tk.IntVar(value=0)
labels = []

def populate():
    for f in files:
        name, _ = os.path.splitext(f)
        lbl = tk.Label(inner, text=name, bg="#111111", fg="#dddddd",
                       anchor="e", justify="right", font=font_item,
                       padx=12, pady=6)
        lbl.pack(fill="x", pady=2, anchor="e")
        labels.append(lbl)
    inner.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))
    canvas.yview_moveto(0)

def refresh_selection():
    for i, lbl in enumerate(labels):
        if i == sel.get():
            lbl.config(bg="#000000", fg="#FFB22C")
        else:
            lbl.config(bg="#111111", fg="#bbbbbb")
    if labels:
        canvas.yview_moveto(sel.get() / max(1, len(labels)))

populate()
counter.config(text=f"{len(files)} صدا یافت شد")
refresh_selection()

# Hotkeys
keyboard.add_hotkey("ctrl+alt+up", lambda: move_selection(-1))
keyboard.add_hotkey("ctrl+alt+down", lambda: move_selection(1))
keyboard.add_hotkey("ctrl+alt+p", play_selected)
keyboard.add_hotkey("ctrl+alt+o", stop_audio)
keyboard.add_hotkey("ctrl+alt+q", lambda: root.destroy())

# شفاف و بدون فوکوس
GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x80000
WS_EX_TRANSPARENT = 0x20
WS_EX_NOACTIVATE = 0x08000000
hwnd = wintypes.HWND(ctypes.windll.user32.FindWindowW(None, "Voice Overlay"))
style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE,
    style | WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_NOACTIVATE)

root.mainloop()
