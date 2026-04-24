"""
ui/about_page.py  —  About / Technical Overview page.
"""

import tkinter as tk
from assets.themes.theme import *


class AboutPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG_DARK)
        self._build()

    def _build(self):
        f = tk.Frame(self, bg=BG_DARK)
        f.pack(fill="both", expand=True, padx=60, pady=40)

        tk.Label(f, text="DFT Visualizer — Technical Overview",
                 font=("Segoe UI", 22, "bold"), bg=BG_DARK, fg=TEXT_WHITE).pack(anchor="w")
        tk.Label(f, text="Signal Processing Lab  ·  v1.0 Research Build",
                 font=FONT_SUB, bg=BG_DARK, fg=TEXT_MUTED).pack(anchor="w", pady=(2, 24))

        for label, val in [
            ("Tool Name",   "DFT Visualizer & Solver"),
            ("Version",     "1.0 Research Build"),
            ("Developer",   "Adarsh Raj Verma"),
            ("Institution", "NIT Jalandhar"),
            ("Framework",   "Python 3  ·  Tkinter  ·  NumPy  ·  Matplotlib  ·  Pandas"),
            ("Purpose",     "Interactive step-by-step DFT for signal analysis"),
        ]:
            row = tk.Frame(f, bg=BG_CARD, pady=10, padx=16)
            row.pack(fill="x", pady=4)
            tk.Label(row, text=f"{label:<18}", font=("Consolas", 11, "bold"),
                     bg=BG_CARD, fg=ACCENT_TEAL, width=18).pack(side="left")
            tk.Label(row, text=val, font=("Consolas", 11),
                     bg=BG_CARD, fg=TEXT_WHITE).pack(side="left")

        tk.Frame(f, bg=BORDER, height=1).pack(fill="x", pady=24)

        tk.Label(f, text="Core Capabilities", font=FONT_HEAD,
                 bg=BG_DARK, fg=TEXT_WHITE).pack(anchor="w")
        for cap in [
            "• Bracket-style W matrix display — just like your textbook",
            "• Magnitude + Phase heatmaps with cell-level colour coding",
            "• Step-by-step DFT expansion for each X[k]",
            "• 4-panel spectrum visualisation (Magnitude, Phase, Re, Im)",
            "• CSV / TXT / Excel signal import  +  PNG/PDF export",
            "• Live DFT preview on the Home page",
            "• Zero-padding for arbitrary N > signal length",
        ]:
            tk.Label(f, text=cap, font=FONT_BODY,
                     bg=BG_DARK, fg=TEXT_MUTED).pack(anchor="w", pady=2)

        tk.Frame(f, bg=BORDER, height=1).pack(fill="x", pady=24)

        tk.Label(f, text="DFT Equations Reference", font=FONT_HEAD,
                 bg=BG_DARK, fg=TEXT_WHITE).pack(anchor="w")
        box = tk.Frame(f, bg=BG_CARD2, padx=20, pady=16)
        box.pack(fill="x", pady=8)
        for name, formula in [
            ("DFT Formula",   "X[k] = Σ x[n] · W_N^(nk),   k = 0..N-1"),
            ("Twiddle Factor", "W_N  = e^(−j·2π/N)"),
            ("Magnitude",      "|X[k]| = √( Re²{X[k]} + Im²{X[k]} )"),
            ("Phase",          "∠X[k] = arctan( Im{X[k]} / Re{X[k]} )  [°]"),
        ]:
            r = tk.Frame(box, bg=BG_CARD2)
            r.pack(fill="x", pady=3)
            tk.Label(r, text=f"{name:<22}", font=("Consolas", 10),
                     bg=BG_CARD2, fg=TEXT_MUTED).pack(side="left")
            tk.Label(r, text=formula, font=("Consolas", 10, "bold"),
                     bg=BG_CARD2, fg=ACCENT_TEAL).pack(side="left")
