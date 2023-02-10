import ctypes
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
from urllib import request

version = "0.1.0"
copyright = f"PepPre {version}\nCopyright © 2023 Tarn Yeong Ching\nhttp://peppre.ctarn.io"
try:
    headline = request.urlopen(f"http://peppre.ctarn.io/api/{version}/headline").read().decode("utf-8")
except:
    headline = ""

is_linux = platform.system() == "Linux"
is_darwin = platform.system() == "Darwin"
is_windows = platform.system() == "Windows"

def get_arch(m=platform.machine()):
    return {"AMD64": "x86_64",}.get(m, m)

if is_windows: ctypes.windll.shcore.SetProcessDpiAwareness(1)

class Console:
    widget = None

    def __init__(self, widget):
        self.widget = widget

    def write(self, msg):
        self.widget.config(state="normal")
        if msg.endswith("\x1b[K\n"):
            self.widget.delete("end-2l", "end")
            self.widget.insert("end", "\n")
            msg = msg[0:-4] + "\n"
        self.widget.insert("end", msg)
        self.widget.config(state="disabled")
        self.widget.update()
        self.widget.see("end")

    def flush(self):
        pass

def run_cmd(cmd):
    c = Console(console)
    c.write("cmd: " + str(cmd) +"\n")
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, encoding="utf-8", creationflags=subprocess.CREATE_NO_WINDOW if is_windows else 0,
    )
    while p.poll() is None: c.write(p.stdout.readline())
    for line in p.stdout.readlines(): c.write(line)

def get_content(*path, subdir=True):
    path = os.path.join(*path)
    if getattr(sys, 'frozen', False):
        if is_darwin: return os.path.join(sys._MEIPASS, "content", path)
        else: return os.path.join("content", path)
    else:
        if subdir: return os.path.join("tmp", f"{get_arch()}.{platform.system()}", path)
        else: return os.path.join("tmp", path)

def save_task(path):
    try:
        print("task saving to", path)
        with open(path, mode="w") as io:
            json.dump({k: v.get() for k, v in vars.items()}, io)
    except:
        print("task failed to saving to", path)

def load_task(path):
    print("task loading from", path)
    try:
        with open(path) as io:
            data = json.load(io)
        for k, v in vars.items():
            if k in data: v.set(data[k])
    except:
        print("task failed to loading from", path)

def run_msconvert(data, out):
    cmd = [vars["msconvert"].get(), "--ms1", "--filter", "peakPicking true", "-o", out, data]
    run_cmd(cmd)
    cmd = [vars["msconvert"].get(), "--ms2", "--filter", "peakPicking true", "-o", out, data]
    run_cmd(cmd)
    return os.path.join(out, os.path.splitext(os.path.basename(data))[0] + ".ms2")

def run_peppre(path):
    cmd = [
        vars["peppre"].get(),
        path,
        "-m", vars["model"].get(),
        "-t", vars["exclusion"].get(),
        "-e", vars["error"].get(),
        "-w", vars["width"].get(),
        "-z", vars["charge_min"].get() + ":" + vars["charge_max"].get(),
        "-n", vars["fold"].get(),
        "-f", ",".join(filter(lambda x: vars[f"fmt_{x}"].get(), fmts)),
        "-o", vars["out"].get(),
    ]
    if vars["preserve"].get():
        cmd.append("-i")
    run_cmd(cmd)

def do_select_peppre():
    path = filedialog.askopenfilename()
    if len(path) > 0: vars["peppre"].set(path)

def do_select_msconvert():
    path = filedialog.askopenfilename()
    if len(path) > 0: vars["msconvert"].set(path)

def do_select_data():
    if is_windows: filetypes = (("All", "*.*"),)
    else: filetypes = (("MS", "*.ms2"), ("All", "*.*"))
    files = filedialog.askopenfilenames(filetypes=filetypes)
    if len(files) > 1:
        print("multiple data selected:")
        for file in files: print(">>", file)
    vars["data"].set(";".join(files))
    if len(vars["data"].get()) > 0 and len(vars["out"].get()) == 0:
        vars["out"].set(os.path.join(os.path.dirname(files[0]), "out"))

def do_select_model():
    path = filedialog.askopenfilename(filetypes=(("Model", "*.model"), ("All", "*.*")))
    if len(path) > 0: vars["model"].set(path)

def do_select_out():
    path = filedialog.askdirectory()
    if len(path) > 0: vars["out"].set(path)

def do_load():
    path = filedialog.askopenfilename(filetypes=(("Configuration", "*.task"), ("All", "*.*")))
    if len(path) > 0: load_task(path)

def do_save():
    save_task(path_autosave)
    path = vars["out"].get()
    if len(path) > 0:
        os.makedirs(path, exist_ok=True)
        save_task(os.path.join(path, "PepPre.task"))
    else:
        print("`Output Directory` is required")

def do_run():
    btn_run.config(state="disabled")
    do_save()
    for p in vars["data"].get().split(";"):
        ext = os.path.splitext(p)[1].lower()
        if ext == ".ms1":
            print("ERROR: select MS2 files instead of MS1 files.")
            break
        if ext != ".ms2":
            p = run_msconvert(p, vars["out"].get())
        run_peppre(p)
    btn_run.config(state="normal")

dir_cfg = os.path.join(Path.home(), ".PepPre", version)
os.makedirs(dir_cfg, exist_ok=True)
path_autosave = os.path.join(dir_cfg, "autosave.task")

fmts = ["csv", "tsv", "ms2", "mgf"]

vars_spec = {
    "peppre": {"type": tk.StringVar, "value": get_content("PepPre", "bin", "PepPre")},
    "msconvert": {"type": tk.StringVar, "value": get_content("ProteoWizard", "msconvert")},
    "model": {"type": tk.StringVar, "value": os.path.join(dir_cfg, "PepPre.model")},
    "data": {"type": tk.StringVar, "value": ""},
    "exclusion": {"type": tk.StringVar, "value": "1.0"},
    "error": {"type": tk.StringVar, "value": "10.0"},
    "width": {"type": tk.StringVar, "value": "2.0"},
    "charge_min": {"type": tk.StringVar, "value": "2"},
    "charge_max": {"type": tk.StringVar, "value": "6"},
    "fold": {"type": tk.StringVar, "value": "4.0"},
    "preserve": {"type": tk.IntVar, "value": 0},
    "fmt_csv": {"type": tk.IntVar, "value": 1},
    "fmt_tsv": {"type": tk.IntVar, "value": 0},
    "fmt_ms2": {"type": tk.IntVar, "value": 0},
    "fmt_mgf": {"type": tk.IntVar, "value": 0},
    "out": {"type": tk.StringVar, "value": ""},
}

win = tk.Tk()
win.title("PepPre")
win.resizable(False, False)
main = ttk.Frame(win)
main.grid(column=0, row=0, padx=16, pady=8)
vars = {k: v["type"](value=v["value"]) for k, v in vars_spec.items()}

row = 0
if len(headline) > 0:
    ttk.Label(main, text=headline, justify="center").grid(column=0, row=row, columnspan=3)
    row += 1

ttk.Label(main, text="PepPre:").grid(column=0, row=row, sticky="W")
ttk.Entry(main, textvariable=vars["peppre"]).grid(column=1, row=row, sticky="WE")
ttk.Button(main, text="Select", command=do_select_peppre).grid(column=2, row=row, sticky="W")
row += 1

if is_windows:
    ttk.Label(main, text="MsConvert:").grid(column=0, row=row, sticky="W")
    ttk.Entry(main, textvariable=vars["msconvert"]).grid(column=1, row=row, sticky="WE")
    ttk.Button(main, text="Select", command=do_select_msconvert).grid(column=2, row=row, sticky="W")
    row += 1

ttk.Label(main, text="Model:").grid(column=0, row=row, sticky="W")
ttk.Entry(main, textvariable=vars["model"]).grid(column=1, row=row, sticky="WE")
ttk.Button(main, text="Select", command=do_select_model).grid(column=2, row=row, sticky="W")
row += 1

ttk.Label(main, text="Data:").grid(column=0, row=row, sticky="W")
ttk.Entry(main, textvariable=vars["data"]).grid(column=1, row=row, sticky="WE")
ttk.Button(main, text="Select", command=do_select_data).grid(column=2, row=row, sticky="W")
row += 1

ttk.Label(main, text="Exclusion Threshold:").grid(column=0, row=row, sticky="W")
ttk.Entry(main, textvariable=vars["exclusion"]).grid(column=1, row=row, sticky="WE")
row += 1

ttk.Label(main, text="Mass Error:").grid(column=0, row=row, sticky="W")
ttk.Entry(main, textvariable=vars["error"]).grid(column=1, row=row, sticky="WE")
ttk.Label(main, text="ppm").grid(column=2, row=row, sticky="W")
row += 1

ttk.Label(main, text="Isolation Width:").grid(column=0, row=row, sticky="W")
ttk.Entry(main, textvariable=vars["width"]).grid(column=1, row=row, sticky="WE")
ttk.Label(main, text="Th").grid(column=2, row=row, sticky="W")
row += 1

ttk.Label(main, text="Charge Range:").grid(column=0, row=row, sticky="W")
frm_charge = ttk.Frame(main)
frm_charge.grid(column=1, row=row, sticky="WE")
ttk.Entry(frm_charge, textvariable=vars["charge_min"]).grid(column=0, row=0, sticky="WE")
ttk.Label(frm_charge, text=" - ").grid(column=1, row=0, sticky="WE")
ttk.Entry(frm_charge, textvariable=vars["charge_max"]).grid(column=2, row=0, sticky="WE")
row += 1

ttk.Label(main, text="Precursor Number:").grid(column=0, row=row, sticky="W")
ttk.Entry(main, textvariable=vars["fold"]).grid(column=1, row=row, sticky="WE")
ttk.Label(main, text="fold").grid(column=2, row=row, sticky="W")
row += 1

ttk.Label(main, text="Original Precursor:").grid(column=0, row=row, sticky="W")
ttk.Checkbutton(main, text="Preserve", variable=vars["preserve"]).grid(column=1, row=row)
row += 1

ttk.Label(main, text="Output Format:").grid(column=0, row=row, sticky="W")
frm_format = ttk.Frame(main)
frm_format.grid(column=1, row=row)
for i, fmt in enumerate(fmts):
    ttk.Checkbutton(frm_format, text=fmt.upper(), variable=vars[f"fmt_{fmt}"]).grid(column=i, row=0)
row += 1

ttk.Label(main, text="Output Directory:").grid(column=0, row=row, sticky="W")
ttk.Entry(main, textvariable=vars["out"]).grid(column=1, row=row, sticky="WE")
ttk.Button(main, text="Select", command=do_select_out).grid(column=2, row=row, sticky="W")
row += 1

frm_btn = ttk.Frame(main)
frm_btn.grid(column=0, row=row, columnspan=3)
ttk.Button(frm_btn, text="Load Task", command=do_load).grid(column=0, row=0, padx=16, pady=8)
ttk.Button(frm_btn, text="Save Task", command=do_save).grid(column=1, row=0, padx=16, pady=8)
btn_run = ttk.Button(frm_btn, text="Save & Run", command=lambda: threading.Thread(target=do_run).start())
btn_run.grid(column=2, row=0, padx=16, pady=8)
row += 1

console = scrolledtext.ScrolledText(main, height=16)
console.config(state="disabled")
console.grid(column=0, row=row, columnspan=3)
row += 1

ttk.Label(main, text=copyright, justify="center").grid(column=0, row=row, columnspan=3)

sys.stdout = Console(console)
sys.stderr = Console(console)

load_task(path_autosave)

tk.mainloop()
