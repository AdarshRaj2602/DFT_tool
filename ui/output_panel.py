"""
ui/output_panel.py
Step-by-step equation display + results table (two sub-tabs).
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import math
import cmath

from assets.themes.theme import *


class OutputPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG_DARK)
        self._placeholder()

    def _placeholder(self):
        tk.Label(self, text="Run a simulation to see equations →",
                 font=("Segoe UI", 14), bg=BG_DARK, fg=TEXT_MUTED).pack(expand=True)

    def render(self, signal, X, W_mat, N):
        for w in self.winfo_children():
            w.destroy()

        # Sub-notebook: equations | table
        style = ttk.Style()
        style.configure("Sub.TNotebook", background=BG_DARK, borderwidth=0)
        style.configure("Sub.TNotebook.Tab",
                        background=BG_CARD, foreground=TEXT_MUTED,
                        padding=[14, 6], font=("Segoe UI", 9))
        style.map("Sub.TNotebook.Tab",
                  background=[("selected", BG_CARD2)],
                  foreground=[("selected", ACCENT_GOLD)])

        nb = ttk.Notebook(self, style="Sub.TNotebook")
        nb.pack(fill="both", expand=True, padx=4, pady=4)

        tab_eq  = tk.Frame(nb, bg=BG_DARK)
        tab_tbl = tk.Frame(nb, bg=BG_DARK)
        nb.add(tab_eq,  text="📐  Step-by-Step Equations")
        nb.add(tab_tbl, text="📋  Results Table")

        self._build_equations(tab_eq, signal, X, W_mat, N)
        self._build_table(tab_tbl, X)

    # ── EQUATIONS ─────────────────────────────────────────────────────────
    def _build_equations(self, parent, signal, X, W_mat, N):
        t = scrolledtext.ScrolledText(
            parent, font=FONT_MONO, bg=BG_CARD, fg=TEXT_WHITE,
            insertbackground=ACCENT_TEAL, relief="flat", bd=0,
            selectbackground=ACCENT_BLUE, wrap="none")
        t.pack(fill="both", expand=True, padx=4, pady=4)

        # Tags
        t.tag_configure("title",  font=("Consolas", 13, "bold"), foreground=ACCENT_TEAL)
        t.tag_configure("head",   font=("Consolas", 11, "bold"), foreground=ACCENT_BLUE)
        t.tag_configure("eq",     font=("Consolas", 10),          foreground=TEXT_WHITE)
        t.tag_configure("result", font=("Consolas", 10, "bold"),  foreground=ACCENT_GOLD)
        t.tag_configure("muted",  font=("Consolas", 9),           foreground=TEXT_MUTED)
        t.tag_configure("purp",   font=("Consolas", 10),          foreground=ACCENT_PURP)

        def w(text, tag="eq"):
            t.insert("end", text, tag)

        W_N = cmath.exp(-2j * math.pi / N)

        w("╔══════════════════════════════════════════════════════════╗\n", "title")
        w("   DISCRETE FOURIER TRANSFORM — STEP-BY-STEP DERIVATION\n",      "title")
        w("╚══════════════════════════════════════════════════════════╝\n\n", "title")

        w("  Governing Equation:\n", "head")
        w("  X[k] = Σ  x[n] · W_N^(n·k)      n = 0 .. N-1\n", "eq")
        w(f"  W_N = e^(−j·2π/{N}) = {W_N:.6f}\n\n", "muted")
        w(f"  N = {N}     Signal length = {len(signal)}\n\n", "muted")

        w("━" * 62 + "\n", "muted")
        w("  INPUT SIGNAL  x[n]\n", "head")
        w("━" * 62 + "\n", "muted")
        for n, val in enumerate(signal):
            s = f"  x[{n:2d}] = {val.real:.4f}"
            if val.imag: s += f" + {val.imag:.4f}j"
            w(s + "\n", "eq")

        w("\n" + "━" * 62 + "\n", "muted")
        w("  COMPUTATION  X[k]\n", "head")
        w("━" * 62 + "\n", "muted")
        for k in range(N):
            w(f"\n  ── X[{k}]  (k = {k}) ──\n", "head")
            w(f"  X[{k}] = ", "eq")
            terms = [f"x[{n}]·W^{(n*k)%N}" for n in range(N)]
            w(" + ".join(terms) + "\n", "eq")
            w(f"       = ", "eq")
            num_terms = []
            for n in range(N):
                xn = signal[n]
                ww = W_mat[k][n]
                num_terms.append(f"({xn.real:.2f})·({ww.real:+.3f}{ww.imag:+.3f}j)")
            w(" +\n         ".join(num_terms) + "\n", "eq")
            res = X[k]
            w(f"  X[{k}] = {res.real:+.4f} {res.imag:+.4f}j\n", "result")
            mag = abs(res)
            ph  = math.degrees(cmath.phase(res))
            w(f"       |X[{k}]| = {mag:.4f}    ∠ = {ph:.2f}°\n", "muted")

        w("\n" + "━" * 62 + "\n", "muted")
        w("  FINAL DFT RESULTS\n", "head")
        w("━" * 62 + "\n", "muted")
        for k, val in enumerate(X):
            mag = abs(val)
            ph  = math.degrees(cmath.phase(val))
            w(f"  X[{k:2d}] = {val.real:+10.4f} {val.imag:+10.4f}j"
              f"   |X|={mag:8.4f}   ∠={ph:+8.2f}°\n", "result")

        t.configure(state="disabled")

    # ── RESULTS TABLE ─────────────────────────────────────────────────────
    def _build_table(self, parent, X):
        style = ttk.Style()
        style.configure("Dark.Treeview",
                        background=BG_CARD, foreground=TEXT_WHITE,
                        fieldbackground=BG_CARD, rowheight=28,
                        font=FONT_MONO)
        style.configure("Dark.Treeview.Heading",
                        background=BG_CARD2, foreground=ACCENT_TEAL,
                        font=("Segoe UI", 10, "bold"), relief="flat")
        style.map("Dark.Treeview",
                  background=[("selected", ACCENT_BLUE)],
                  foreground=[("selected", TEXT_WHITE)])

        cols = ("k", "Real", "Imaginary", "Magnitude", "Phase (°)")
        tree = ttk.Treeview(parent, columns=cols, show="headings",
                             style="Dark.Treeview")
        vsb = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)

        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=130, anchor="center")

        for k, val in enumerate(X):
            mag = abs(val)
            ph  = math.degrees(cmath.phase(val))
            tree.insert("", "end", values=(
                k, f"{val.real:+.4f}", f"{val.imag:+.4f}",
                f"{mag:.4f}", f"{ph:+.2f}°"))
