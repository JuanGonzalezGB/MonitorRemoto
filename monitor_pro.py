#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk
import subprocess

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
            mode = "cpu"
            continue
        elif line == "CORES:":
            mode = "cores"
            continue
        elif line == "GPU:":
            mode = "gpu"
            continue

        if not line:
            continue

        if mode == "cpu":
            try:
                cpu = float(line)
            except:
                pass

        elif mode == "gpu":
            try:
                gpu = float(line)
            except:
                pass

        elif mode == "cores":
            if ":" in line:
                parts = line.split(":")
                if len(parts) == 2:
                    name = parts[0].strip()
                    try:
                        temp = float(parts[1])
                        cores.append((name, temp))
                    except:
                        pass

    return cpu, gpu, cores


def color(temp):
    if temp is None:
        return "white"
    if temp < 50:
        return "lime"
    elif temp < 70:
        return "yellow"
    else:
        return "red"


def update():
    cpu, gpu, cores = parse()

    # CPU
    if cpu is not None:
        cpu_label.config(text=f"CPU {cpu:.1f} C", fg=color(cpu))
        cpu_bar["value"] = cpu
    else:
        cpu_label.config(text="CPU --")
        cpu_bar["value"] = 0

    # GPU
    if gpu is not None:
        gpu_label.config(text=f"GPU {gpu:.1f} C", fg=color(gpu))
        gpu_bar["value"] = gpu
    else:
        gpu_label.config(text="GPU --")
        gpu_bar["value"] = 0

    # CORES
    for widget in cores_frame.winfo_children():
        widget.destroy()

    for name, temp in cores:
        lbl = tk.Label(
            cores_frame,
            text=f"{name}: {temp:.1f} C",
            fg=color(temp),
            bg="black",
            font=("Arial", 9)
        )
        lbl.pack(anchor="w")

    root.after(2000, update)


# UI
root = tk.Tk()
root.title("Monitor PRO")
root.geometry("480x320")
root.configure(bg="black")

# Estilo barras
style = ttk.Style()
style.theme_use('default')
style.configure("TProgressbar", troughcolor='black', background='cyan')

title = tk.Label(root, text="MONITOR PRO", fg="cyan", bg="black", font=("Arial", 12, "bold"))
title.pack()

# CPU
cpu_label = tk.Label(root, text="CPU --", fg="white", bg="black", font=("Arial", 12))
cpu_label.pack()

cpu_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate", maximum=100)
cpu_bar.pack(pady=2)

# GPU
gpu_label = tk.Label(root, text="GPU --", fg="white", bg="black", font=("Arial", 12))
gpu_label.pack()

gpu_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate", maximum=100)
gpu_bar.pack(pady=2)

# CORES
cores_frame = tk.Frame(root, bg="black")
cores_frame.pack()

update()
root.mainloop()
