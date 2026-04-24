"""
ui/input_panel.py
Left panel of the solver: signal input, N, options, Run/Clear buttons.
"""

import tkinter as tk
from tkinter import filedialog, messagebox

from assets.themes.theme import *
from utils.validators    import parse_signal, load_signal_file
from core.dft            import compute_dft


class InputPanel(tk.Frame):
    def __init__(self, parent, on_result_callback):
        super().__init__(parent, bg=BG_CARD)
        self._callback = on_result_callback
        self._build()

    def _build(self):
        f = self

        tk.Label(f, text="Simulation Parameters",
                 font=("Segoe UI", 13, "bold"),
                 bg=BG_CARD, fg=ACCENT_TEAL).pack(anchor="w", padx=20, pady=(18, 4))
        tk.Frame(f, bg=BORDER, height=1).pack(fill="x", padx=20, pady=(0, 14))

        # Signal input
        self._sec("Signal  x[n]  —  Enter Values")
        sig_box = tk.Frame(f, bg=BG_CARD)
        sig_box.pack(fill="x", padx=20, pady=(0, 4))
        self.signal_text = tk.Text(sig_box, height=5, font=FONT_MONO,
                                    bg=BG_CARD2, fg=TEXT_WHITE,
                                    insertbackground=ACCENT_TEAL,
                                    relief="flat", bd=0,
                                    selectbackground=ACCENT_BLUE)
        self.signal_text.pack(fill="x", ipady=6, ipadx=6)
        self.signal_text.insert("1.0", "1, 2, 3, 4")
        tk.Label(sig_box, text="Separate with commas  e.g.  1, 2, 3, 4",
                 font=FONT_SMALL, bg=BG_CARD, fg=TEXT_MUTED).pack(anchor="w")

        # Import button
        tk.Button(f, text="📂  Import  CSV / TXT / Excel",
                  font=("Segoe UI", 10), bg=BG_CARD2, fg=ACCENT_BLUE,
                  bd=0, relief="flat", padx=12, pady=8, cursor="hand2",
                  activebackground=BORDER, activeforeground=ACCENT_BLUE,
                  command=self._import).pack(fill="x", padx=20, pady=(4, 16))

        # N value
        self._sec("DFT Size  N")
        n_row = tk.Frame(f, bg=BG_CARD)
        n_row.pack(fill="x", padx=20, pady=(0, 16))
        self.n_var = tk.StringVar(value="4")
        tk.Entry(n_row, textvariable=self.n_var,
                 font=("Segoe UI", 14, "bold"),
                 bg=BG_CARD2, fg=ACCENT_GOLD,
                 insertbackground=ACCENT_TEAL,
                 relief="flat", bd=0, width=7, justify="center").pack(
                 side="left", ipady=8, ipadx=10)
        tk.Button(n_row, text="Auto", font=FONT_SMALL,
                  bg=BG_CARD2, fg=TEXT_MUTED,
                  bd=0, relief="flat", padx=8, pady=5, cursor="hand2",
                  command=self._auto_n).pack(side="left", padx=10)

        # Options
        self._sec("Display Options")
        opts = tk.Frame(f, bg=BG_CARD)
        opts.pack(fill="x", padx=20, pady=(0, 16))
        self.show_steps = tk.BooleanVar(value=True)
        self.show_wmat  = tk.BooleanVar(value=True)
        for var, lbl in [(self.show_steps, "Show step-by-step equations"),
                         (self.show_wmat,  "Show W matrix heatmap")]:
            tk.Checkbutton(opts, text=lbl, variable=var,
                           font=FONT_BODY, bg=BG_CARD, fg=TEXT_WHITE,
                           selectcolor=BG_CARD2,
                           activebackground=BG_CARD,
                           activeforeground=TEXT_WHITE,
                           cursor="hand2").pack(anchor="w")

        # Buttons
        tk.Button(f, text="  ▶  Run DFT Simulation  ",
                  font=("Segoe UI", 13, "bold"),
                  bg=BTN_GREEN, fg=TEXT_WHITE,
                  activebackground=BTN_GREEN_H,
                  bd=0, relief="flat", pady=12, cursor="hand2",
                  command=self._run).pack(fill="x", padx=20, pady=(0, 8))

        tk.Button(f, text="🗑  Clear All",
                  font=("Segoe UI", 10),
                  bg=BTN_RED, fg=TEXT_WHITE,
                  activebackground="#B91C1C",
                  bd=0, relief="flat", pady=8, cursor="hand2",
                  command=self._clear).pack(fill="x", padx=20, pady=(0, 20))

    def _sec(self, label):
        tk.Label(self, text=label, font=("Segoe UI", 10, "bold"),
                 bg=BG_CARD, fg=TEXT_MUTED).pack(anchor="w", padx=20, pady=(0, 4))

    def _import(self):
        path = filedialog.askopenfilename(
            title="Import Signal File",
            filetypes=[("All supported", "*.csv *.txt *.xlsx *.xls"),
                       ("CSV", "*.csv"), ("Text", "*.txt"),
                       ("Excel", "*.xlsx *.xls")])
        if not path: return
        try:
            vals = load_signal_file(path)
            self.signal_text.delete("1.0", "end")
            self.signal_text.insert("1.0", ", ".join(str(v) for v in vals))
            self.n_var.set(str(len(vals)))
            messagebox.showinfo("Import OK", f"Loaded {len(vals)} samples.")
        except Exception as e:
            messagebox.showerror("Import Error", str(e))

    def _auto_n(self):
        raw = self.signal_text.get("1.0", "end").strip()
        n = len([v for v in raw.split(",") if v.strip()])
        self.n_var.set(str(n))

    def _clear(self):
        self.signal_text.delete("1.0", "end")
        self.signal_text.insert("1.0", "1, 2, 3, 4")
        self.n_var.set("4")

    def _run(self):
        raw = self.signal_text.get("1.0", "end").strip()
        try:
            signal = parse_signal(raw)
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
            return
        try:
            N = int(self.n_var.get())
            if N <= 0: raise ValueError
        except Exception:
            messagebox.showerror("Input Error", "N must be a positive integer.")
            return

        X, W_mat = compute_dft(signal, N)
        # Pad signal to N for display
        if len(signal) < N:
            signal = list(signal) + [0+0j] * (N - len(signal))
        else:
            signal = list(signal[:N])
        self._callback(signal, X, W_mat, N)
