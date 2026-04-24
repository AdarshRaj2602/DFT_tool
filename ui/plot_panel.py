"""
ui/plot_panel.py
Spectrum plots: Magnitude, Phase, Real, Imaginary.
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import math
import cmath
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from assets.themes.theme import *


class PlotPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG_DARK)
        self._fig = None
        self._placeholder()

    def _placeholder(self):
        tk.Label(self, text="Run a simulation to see spectrum plots →",
                 font=("Segoe UI", 14), bg=BG_DARK, fg=TEXT_MUTED).pack(expand=True)

    def render(self, signal, X, N):
        for w in self.winfo_children():
            w.destroy()

        freq   = list(range(N))
        mags   = [abs(v)                          for v in X]
        phases = [math.degrees(cmath.phase(v))    for v in X]
        reals  = [v.real                           for v in X]
        imags  = [v.imag                           for v in X]

        fig, axes = plt.subplots(2, 2, figsize=(10, 5.5), facecolor=BG_DARK)
        fig.subplots_adjust(hspace=0.48, wspace=0.38)

        cfg = [
            (axes[0][0], mags,   ACCENT_TEAL, "Magnitude Spectrum  |X[k]|",   "|X[k]|"),
            (axes[0][1], phases, ACCENT_PURP, "Phase Spectrum  ∠X[k]  (°)",   "Phase (°)"),
            (axes[1][0], reals,  ACCENT_BLUE, "Real Part  Re{X[k]}",           "Re{X[k]}"),
            (axes[1][1], imags,  ACCENT_GOLD, "Imaginary Part  Im{X[k]}",      "Im{X[k]}"),
        ]

        for ax, yd, color, title, yl in cfg:
            ax.set_facecolor(BG_CARD)
            for sp in ax.spines.values():
                sp.set_edgecolor(BORDER)
            ax.tick_params(colors=TEXT_MUTED, labelsize=8)
            ax.set_title(title, color=TEXT_WHITE, fontsize=9, fontweight="bold", pad=8)
            ax.set_xlabel("k", color=TEXT_MUTED, fontsize=8)
            ax.set_ylabel(yl,  color=TEXT_MUTED, fontsize=8)
            ax.grid(True, color=BORDER, linestyle="--", linewidth=0.5, alpha=0.7)

            markerline, stemlines, baseline = ax.stem(freq, yd)
            plt.setp(stemlines,  color=color,   linewidth=1.8)
            plt.setp(markerline, color=color,   markersize=6)
            plt.setp(baseline,   color=BORDER,  linewidth=1)

        self._fig = fig

        cv = FigureCanvasTkAgg(fig, master=self)
        cv.draw()
        cv.get_tk_widget().pack(fill="both", expand=True)

        btn_row = tk.Frame(self, bg=BG_DARK)
        btn_row.pack(fill="x")
        tk.Button(btn_row, text="💾  Save Plots as PNG",
                  font=FONT_SMALL, bg=BG_CARD2, fg=ACCENT_BLUE,
                  bd=0, relief="flat", padx=12, pady=6, cursor="hand2",
                  command=self._save).pack(side="right", padx=12, pady=8)

    def _save(self):
        if not self._fig: return
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("PDF", "*.pdf")])
        if path:
            self._fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=BG_DARK)
            messagebox.showinfo("Saved", f"Saved to:\n{path}")
