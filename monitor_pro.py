#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk
import subprocess
from datetime import datetime

# ===== THEME =====
BG      = "#0f0f12"
BG2     = "#161620"
BORDER  = "#1e1e2a"
GREEN   = "#3ddc84"
ORANGE  = "#f0a030"
RED     = "#e05252"
CYAN    = "#7fd4c1"
MUTED   = "#4a4a5a"
WHITE   = "#e0e0e8"

F_TITLE  = ("monospace", 10, "bold")
F_NORMAL = ("monospace", 10)
F_SMALL  = ("monospace", 8)

# ===== DATA =====
def get_data():
    try:
        return subprocess.check_output(["./monitor_pc.sh"]).decode()
    except:
        return ""

def parse():
    data = get_data().splitlines()

    cpu = None
    gpu = None
    cores = []
    mode = None

    for line in data:
        line = line.strip()

        if line == "CPU:":
            mode = "cpu"; continue
        elif line == "GPU:":
            mode = "gpu"; continue
        elif line == "CORES:":
            mode = "cores"; continue

        if not line:
            continue

        if mode == "cpu":
            try: cpu = float(line)
            except: pass

        elif mode == "gpu":
            try: gpu = float(line)
            except: pass

        elif mode == "cores":
            if ":" in line:
                name, val = line.split(":")
                try:
                    cores.append((name.strip(), float(val)))
                except:
                    pass

    return cpu, gpu, cores


def color(temp):
    if temp is None: return MUTED
    if temp < 50: return GREEN
    elif temp < 70: return ORANGE
    else: return RED


def bar_style(temp):
    if temp is None or temp < 50:
        return "Green.Horizontal.TProgressbar"
    elif temp < 70:
        return "Orange.Horizontal.TProgressbar"
    else:
        return "Red.Horizontal.TProgressbar"


# ===== UI =====
root = tk.Tk()
root.title("Monitor PRO")
root.geometry("480x280")
root.configure(bg=BG)
root.resizable(False, True)

core_widgets = {}

# ===== ESTILOS =====
style = ttk.Style()
style.theme_use("default")

style.configure("Green.Horizontal.TProgressbar",
                troughcolor=BG2, background=GREEN)

style.configure("Orange.Horizontal.TProgressbar",
                troughcolor=BG2, background=ORANGE)

style.configure("Red.Horizontal.TProgressbar",
                troughcolor=BG2, background=RED)

# ===== HEADER =====
header = tk.Frame(root, bg=BG)
header.pack(fill="x", padx=6, pady=(4, 0))

tk.Label(header, text="TEMP MONITOR",
         bg=BG, fg=CYAN, font=F_TITLE).pack(side="left")

clock_lbl = tk.Label(header, text="",
                     bg=BG, fg=MUTED, font=F_SMALL)
clock_lbl.pack(side="right")

tk.Frame(root, bg=BORDER, height=1).pack(fill="x", padx=6, pady=3)

# ===== SCROLL AREA =====
container = tk.Frame(root, bg=BG)
container.pack(fill="both", expand=True)

canvas = tk.Canvas(container, bg=BG, highlightthickness=0)
scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)

scroll_frame = tk.Frame(canvas, bg=BG)

canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

def on_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

scroll_frame.bind("<Configure>", on_configure)

# ===== SCROLL TÁCTIL =====
def start_scroll(event):
    canvas.scan_mark(event.x, event.y)

def drag_scroll(event):
    canvas.scan_dragto(event.x, event.y, gain=1)

canvas.bind("<Button-1>", start_scroll)
canvas.bind("<B1-Motion>", drag_scroll)

# ===== SCROLL MOUSE =====
def on_mousewheel(event):
    canvas.yview_scroll(int(-1*(event.delta/120)), "units")

def on_linux_scroll(event):
    if event.num == 4:
        canvas.yview_scroll(-1, "units")
    elif event.num == 5:
        canvas.yview_scroll(1, "units")

canvas.bind_all("<MouseWheel>", on_mousewheel)
canvas.bind_all("<Button-4>", on_linux_scroll)
canvas.bind_all("<Button-5>", on_linux_scroll)

# ===== PANELS =====
def make_panel(title):
    frame = tk.Frame(scroll_frame, bg=BG2)
    frame.pack(fill="x", pady=3, padx=6)

    tk.Label(frame, text=title,
             bg=BG2, fg=MUTED, font=F_SMALL).pack(anchor="w", padx=6, pady=(4, 0))
    return frame

cpu_panel = make_panel("CPU")
gpu_panel = make_panel("GPU")
cores_panel = make_panel("CORES")

# ===== CPU =====
cpu_label = tk.Label(cpu_panel, text="--",
                     bg=BG2, fg=WHITE, font=F_NORMAL)
cpu_label.pack(anchor="w", padx=6)

cpu_bar = ttk.Progressbar(cpu_panel, length=440, maximum=100)
cpu_bar.pack(padx=6, pady=(2, 6))

# ===== GPU =====
gpu_label = tk.Label(gpu_panel, text="--",
                     bg=BG2, fg=WHITE, font=F_NORMAL)
gpu_label.pack(anchor="w", padx=6)

gpu_bar = ttk.Progressbar(gpu_panel, length=440, maximum=100)
gpu_bar.pack(padx=6, pady=(2, 6))

# ===== CORES =====
cores_frame = tk.Frame(cores_panel, bg=BG2)
cores_frame.pack(fill="x", padx=6, pady=(2, 6))

# ===== UPDATE =====
def update():
    cpu, gpu, cores = parse()

    # CPU
    if cpu is not None:
        cpu_label.config(text=f"{cpu:.1f}°C", fg=color(cpu))
        cpu_bar["value"] = cpu
        cpu_bar.config(style=bar_style(cpu))
    else:
        cpu_label.config(text="--")
        cpu_bar["value"] = 0

    # GPU
    if gpu is not None:
        gpu_label.config(text=f"{gpu:.1f}°C", fg=color(gpu))
        gpu_bar["value"] = gpu
        gpu_bar.config(style=bar_style(gpu))
    else:
        gpu_label.config(text="--")
        gpu_bar["value"] = 0

    # ===== CORES OPTIMIZADO =====
    current_names = set()

    for name, temp in cores:
        current_names.add(name)

        if name not in core_widgets:
            row = tk.Frame(cores_frame, bg=BG2)
            row.pack(fill="x")

            lbl_name = tk.Label(row, text=name,
                                bg=BG2, fg=MUTED, font=F_SMALL)
            lbl_name.pack(side="left")

            lbl_temp = tk.Label(row, text="--",
                                bg=BG2, fg=WHITE, font=F_SMALL)
            lbl_temp.pack(side="right")

            core_widgets[name] = (lbl_name, lbl_temp)

        lbl_name, lbl_temp = core_widgets[name]
        lbl_temp.config(text=f"{temp:.1f}°C", fg=color(temp))

    # eliminar cores que ya no existan
    to_delete = [name for name in core_widgets if name not in current_names]

    for name in to_delete:
        lbl_name, lbl_temp = core_widgets[name]
        lbl_name.master.destroy()
        del core_widgets[name]

    root.after(2000, update)


def tick_clock():
    clock_lbl.config(text=datetime.now().strftime("%H:%M:%S"))
    root.after(1000, tick_clock)


update()
tick_clock()
root.mainloop()
