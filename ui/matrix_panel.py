"""
ui/matrix_panel.py
W-Matrix visualisation: bracket-style matrix (like the textbook screenshot)
with a 3D heatmap colouring based on |W^(nk)|  and  ∠W^(nk).

Layout:
  ┌──────────────────────────────────────────────┐
  │  X(0)  ┐   ┌ W^0  W^0  W^0  W^0 ┐  ┌ x(0) ┐
  │  X(1)  │ = │ W^0  W^1  W^2  W^3 │  │ x(1) │
  │  X(2)  │   │ W^0  W^2  W^4  W^6 │  │ x(2) │
  │  X(3)  ┘   └ W^0  W^3  W^6  W^9 ┘  └ x(3) ┘
  └──────────────────────────────────────────────┘
  Below: magnitude heatmap strip + phase heatmap strip
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import math
import cmath

from assets.themes.theme import *
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np


def _phase_color(phase_deg: float, alpha: float = 1.0) -> str:
    """Map phase in [-180,180] → hue → hex colour (teal-blue-purple palette)."""
    hue = (phase_deg + 180) / 360          # 0..1
    r, g, b = plt.cm.cool(hue)[:3]
    return "#{:02x}{:02x}{:02x}".format(int(r*255), int(g*255), int(b*255))


def _mag_color(mag_norm: float) -> str:
    """Map normalised magnitude 0..1 → dark→bright teal."""
    r, g, b = plt.cm.YlGnBu(mag_norm)[:3]
    return "#{:02x}{:02x}{:02x}".format(int(r*255), int(g*255), int(b*255))


class MatrixPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG_DARK)
        self._placeholder()

    def _placeholder(self):
        tk.Label(self, text="Run a simulation to see the W matrix →",
                 font=("Segoe UI", 14), bg=BG_DARK, fg=TEXT_MUTED).pack(expand=True)

    def render(self, W_mat: list, N: int):
        for w in self.winfo_children():
            w.destroy()

        # ── Scrollable container ──────────────────────────────────────────
        outer = tk.Canvas(self, bg=BG_DARK, highlightthickness=0)
        vsb   = ttk.Scrollbar(self, orient="vertical",   command=outer.yview)
        hsb   = ttk.Scrollbar(self, orient="horizontal", command=outer.xview)
        inner = tk.Frame(outer, bg=BG_DARK)
        inner.bind("<Configure>",
            lambda e: outer.configure(scrollregion=outer.bbox("all")))
        outer.create_window((0, 0), window=inner, anchor="nw")
        outer.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side="right",  fill="y")
        hsb.pack(side="bottom", fill="x")
        outer.pack(fill="both", expand=True)
        outer.bind_all("<MouseWheel>",
            lambda e: outer.yview_scroll(-1*(e.delta//120), "units"))

        # ── Header ───────────────────────────────────────────────────────
        hdr = tk.Frame(inner, bg=BG_DARK, pady=14, padx=20)
        hdr.pack(fill="x")
        tk.Label(hdr, text="Twiddle Factor Matrix   W_N^(n·k)",
                 font=("Segoe UI", 15, "bold"),
                 bg=BG_DARK, fg=ACCENT_TEAL).pack(side="left")
        tk.Label(hdr, text=f"  N = {N}    W_N = e^(−j·2π/{N})",
                 font=("Consolas", 11), bg=BG_DARK, fg=TEXT_MUTED).pack(side="left")

        tk.Frame(inner, bg=BORDER, height=1).pack(fill="x", padx=20, pady=(0, 10))

        # ── Bracket Matrix canvas ─────────────────────────────────────────
        self._draw_bracket_matrix(inner, W_mat, N)

        # ── Magnitude heatmap ─────────────────────────────────────────────
        tk.Label(inner, text="Magnitude Heatmap  |W^(nk)|",
                 font=("Segoe UI", 11, "bold"),
                 bg=BG_DARK, fg=ACCENT_BLUE).pack(anchor="w", padx=20, pady=(16, 4))
        self._draw_heatmap(inner, W_mat, N, mode="magnitude")

        # ── Phase heatmap ─────────────────────────────────────────────────
        tk.Label(inner, text="Phase Heatmap  ∠W^(nk)  (degrees)",
                 font=("Segoe UI", 11, "bold"),
                 bg=BG_DARK, fg=ACCENT_PURP).pack(anchor="w", padx=20, pady=(12, 4))
        self._draw_heatmap(inner, W_mat, N, mode="phase")

    # ── BRACKET MATRIX ────────────────────────────────────────────────────
    def _draw_bracket_matrix(self, parent, W_mat, N):
        """
        Draw the matrix equation in the textbook bracket style:

          ⎡ X(0) ⎤   ⎡ W⁰  W⁰  W⁰  W⁰ ⎤   ⎡ x(0) ⎤
          ⎢ X(1) ⎥ = ⎢ W⁰  W¹  W²  W³ ⎥ × ⎢ x(1) ⎥
          ⎢ X(2) ⎥   ⎢ W⁰  W²  W⁴  W⁶ ⎥   ⎢ x(2) ⎥
          ⎣ X(3) ⎦   ⎣ W⁰  W³  W⁶  W⁹ ⎦   ⎣ x(3) ⎦
        """
        CELL_W = max(80, 560 // max(N, 1))
        CELL_H = 36
        PAD_X  = 28   # bracket arm width
        PAD_Y  = 14   # top/bottom padding inside brackets

        mat_px_w = N * CELL_W
        mat_px_h = N * CELL_H
        total_h  = mat_px_h + PAD_Y * 2

        # Total canvas width: X-vec + "=" + W-mat + "×" + x-vec
        vec_w  = CELL_W + PAD_X * 2
        eq_w   = 30
        total_w = vec_w + eq_w + (mat_px_w + PAD_X*2) + eq_w + vec_w + 40

        c = tk.Canvas(parent, width=min(total_w, 1100),
                      height=total_h, bg=BG_DARK, highlightthickness=0)
        c.pack(padx=20, pady=4)

        # Helper: draw big bracket around a rectangle
        def bracket(x1, y1, x2, y2, open_left=True, color=TEXT_WHITE):
            lw = 2
            arm = 12
            if open_left:
                # Left bracket ⎡⎢⎣
                c.create_line(x1+arm, y1, x1, y1,     fill=color, width=lw)  # top
                c.create_line(x1, y1, x1, y2,          fill=color, width=lw)  # vertical
                c.create_line(x1, y2, x1+arm, y2,      fill=color, width=lw)  # bottom
            else:
                # Right bracket ⎤⎥⎦
                c.create_line(x2-arm, y1, x2, y1,     fill=color, width=lw)
                c.create_line(x2, y1, x2, y2,          fill=color, width=lw)
                c.create_line(x2, y2, x2-arm, y2,      fill=color, width=lw)

        # ── Column 1: X(k) vector ────────────────────────────
        ox = 10
        oy = PAD_Y
        bracket(ox, oy, ox + vec_w, oy + total_h - PAD_Y, open_left=True,  color=ACCENT_TEAL)
        bracket(ox, oy, ox + vec_w, oy + total_h - PAD_Y, open_left=False, color=ACCENT_TEAL)
        for k in range(N):
            cy = oy + k * CELL_H + CELL_H // 2
            c.create_text(ox + PAD_X + CELL_W//2, cy,
                          text=f"X({k})", fill=ACCENT_TEAL,
                          font=("Consolas", 11, "bold"))

        # ── "=" sign ─────────────────────────────────────────
        ox += vec_w
        c.create_text(ox + eq_w//2, oy + total_h//2 - PAD_Y//2,
                      text="=", fill=TEXT_WHITE, font=("Segoe UI", 18, "bold"))
        ox += eq_w

        # ── Column 2: W matrix ───────────────────────────────
        w_ox = ox
        bracket(w_ox, oy, w_ox + mat_px_w + PAD_X*2, oy + total_h - PAD_Y,
                open_left=True,  color=ACCENT_BLUE)
        bracket(w_ox, oy, w_ox + mat_px_w + PAD_X*2, oy + total_h - PAD_Y,
                open_left=False, color=ACCENT_BLUE)

        # Cell backgrounds and text with heatmap colouring
        mags_all = [abs(W_mat[k][n]) for k in range(N) for n in range(N)]
        mx_mag   = max(mags_all) if mags_all else 1

        for k in range(N):
            for n in range(N):
                val   = W_mat[k][n]
                mag   = abs(val)
                phase = math.degrees(cmath.phase(val))
                mag_n = mag / mx_mag
                exp   = (n * k) % N

                cx = w_ox + PAD_X + n * CELL_W + CELL_W // 2
                cy = oy + k * CELL_H + CELL_H // 2

                # Coloured cell background
                cell_col = _mag_color(mag_n)
                c.create_rectangle(
                    w_ox + PAD_X + n * CELL_W + 3,
                    oy + k * CELL_H + 3,
                    w_ox + PAD_X + (n+1) * CELL_W - 3,
                    oy + (k+1) * CELL_H - 3,
                    fill=cell_col, outline="")

                # Text label  W^exp
                text_col = TEXT_WHITE if mag_n > 0.4 else TEXT_MUTED
                superscript = str(exp)
                c.create_text(cx - 4, cy, text="W", fill=text_col,
                              font=("Consolas", 10, "bold"))
                c.create_text(cx + 8, cy - 5, text=superscript,
                              fill=ACCENT_GOLD, font=("Consolas", 7, "bold"))

        ox += mat_px_w + PAD_X * 2

        # ── "×" sign ─────────────────────────────────────────
        c.create_text(ox + eq_w//2, oy + total_h//2 - PAD_Y//2,
                      text="×", fill=TEXT_WHITE, font=("Segoe UI", 14))
        ox += eq_w

        # ── Column 3: x(n) vector ────────────────────────────
        bracket(ox, oy, ox + vec_w, oy + total_h - PAD_Y, open_left=True,  color=ACCENT_PURP)
        bracket(ox, oy, ox + vec_w, oy + total_h - PAD_Y, open_left=False, color=ACCENT_PURP)
        for n in range(N):
            cy = oy + n * CELL_H + CELL_H // 2
            c.create_text(ox + PAD_X + CELL_W//2, cy,
                          text=f"x({n})", fill=ACCENT_PURP,
                          font=("Consolas", 11, "bold"))

    # ── HEATMAP ──────────────────────────────────────────────────────────
    def _draw_heatmap(self, parent, W_mat, N, mode="magnitude"):
        data = np.zeros((N, N))
        for k in range(N):
            for n in range(N):
                v = W_mat[k][n]
                data[k][n] = abs(v) if mode == "magnitude" else math.degrees(cmath.phase(v))

        fig_h = max(2.2, N * 0.45)
        fig, ax = plt.subplots(figsize=(min(N * 0.85, 10), fig_h),
                                facecolor=BG_DARK)
        ax.set_facecolor(BG_CARD)

        cmap = "YlGnBu" if mode == "magnitude" else "cool"
        im = ax.imshow(data, cmap=cmap, aspect="auto")

        # Annotate cells
        for k in range(N):
            for n in range(N):
                exp = (n * k) % N
                val = data[k][n]
                lbl = f"W^{exp}\n{val:.2f}" if mode == "magnitude" else f"W^{exp}\n{val:.0f}°"
                ax.text(n, k, lbl, ha="center", va="center",
                        color="white" if val < (data.max()*0.6 if mode=="magnitude" else 0)
                              else "black",
                        fontsize=max(6, 9 - N//4), fontweight="bold")

        ax.set_xticks(range(N))
        ax.set_yticks(range(N))
        ax.set_xticklabels([f"n={i}" for i in range(N)], color=TEXT_MUTED, fontsize=8)
        ax.set_yticklabels([f"k={i}" for i in range(N)], color=TEXT_MUTED, fontsize=8)
        ax.set_xlabel("n  (signal index)", color=TEXT_MUTED, fontsize=8)
        ax.set_ylabel("k  (frequency index)", color=TEXT_MUTED, fontsize=8)
        for sp in ax.spines.values():
            sp.set_edgecolor(BORDER)

        cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        lbl_txt = "|W^(nk)|" if mode == "magnitude" else "∠W^(nk) (°)"
        cb.set_label(lbl_txt, color=TEXT_MUTED, fontsize=8)
        cb.ax.yaxis.set_tick_params(color=TEXT_MUTED, labelcolor=TEXT_MUTED)
        fig.patch.set_facecolor(BG_DARK)
        fig.tight_layout()

        cv = FigureCanvasTkAgg(fig, master=parent)
        cv.draw()
        cv.get_tk_widget().pack(padx=20, pady=(0, 4))
        plt.close(fig)
