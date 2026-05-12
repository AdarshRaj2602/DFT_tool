# ui/initial_matrix_panel.py "Question" tab — shows the DFT problem as a textbook matrix equation with x(n) values filled in but W entries shown as W^(nk) symbols only. The user sees the PROBLEM here; the W Matrix tab shows the ANSWER.

import tkinter as tk
from tkinter import ttk
import math
import cmath

from assets.themes.theme import *


class InitialMatrixPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG_DARK)
        self._placeholder()

    def _placeholder(self):
        tk.Label(self,
                 text="Run a simulation to see the DFT problem setup →",
                 font=("Segoe UI", 14), bg=BG_DARK, fg=TEXT_MUTED).pack(expand=True)
    def render(self, signal: list, N: int):
        for w in self.winfo_children():
            w.destroy()

        # Scrollable canvas
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
        hdr = tk.Frame(inner, bg=BG_DARK, pady=16, padx=24)
        hdr.pack(fill="x")

        tk.Label(hdr, text="❓  DFT Problem Setup",
                 font=("Segoe UI", 16, "bold"),
                 bg=BG_DARK, fg=ACCENT_GOLD).pack(anchor="w")
        tk.Label(hdr,
                 text="Given the signal x(n) below, find the DFT coefficients X(k) = ?",
                 font=("Segoe UI", 11), bg=BG_DARK, fg=TEXT_MUTED).pack(anchor="w", pady=(2, 0))

        tk.Frame(inner, bg=ACCENT_GOLD, height=2).pack(fill="x", padx=24, pady=(0, 10))
        formula_box = tk.Frame(inner, bg=BG_CARD2, padx=20, pady=14)
        formula_box.pack(fill="x", padx=24, pady=(0, 16))

        tk.Label(formula_box,
                 text="X[k]  =  Σ  x[n] · W_N^(n·k)       n = 0, 1, …, N−1",
                 font=("Consolas", 13, "bold"),
                 bg=BG_CARD2, fg=ACCENT_TEAL).pack(anchor="w")
        tk.Label(formula_box,
                 text=f"W_N  =  e^(−j·2π/N)  =  e^(−j·2π/{N})         N = {N}",
                 font=("Consolas", 10),
                 bg=BG_CARD2, fg=TEXT_MUTED).pack(anchor="w", pady=(4, 0))
        q_lbl = tk.Frame(inner, bg=BG_CARD, padx=20, pady=10)
        q_lbl.pack(fill="x", padx=24, pady=(0, 8))
        tk.Label(q_lbl,
                 text="📋  Write the matrix equation  [X(k)] = [W^(nk)] × [x(n)]  and solve for X(k):",
                 font=("Segoe UI", 11, "bold"),
                 bg=BG_CARD, fg=ACCENT_PURP).pack(anchor="w")
        self._draw_question_matrix(inner, signal, N)
        tk.Label(inner, text="Given Signal Values",
                 font=("Segoe UI", 12, "bold"),
                 bg=BG_DARK, fg=ACCENT_BLUE).pack(anchor="w", padx=24, pady=(20, 6))

        self._draw_signal_table(inner, signal, N)
        hint = tk.Frame(inner, bg="#1a2a1a", padx=18, pady=14)
        hint.pack(fill="x", padx=24, pady=(16, 24))
        tk.Label(hint,
                 text="💡  Hint",
                 font=("Segoe UI", 10, "bold"),
                 bg="#1a2a1a", fg=ACCENT_TEAL).pack(anchor="w")
        hints = [
            f"  1.  W_N = e^(−j·2π/{N})  is the twiddle factor base",
            f"  2.  Each cell W^(n·k) is computed as W_N raised to the power (n × k)",
            f"  3.  W^0 = 1  always  (zero-power rule)",
            f"  4.  Exponents repeat with period N  →  W^(nk) = W^(nk mod N)",
            f"  5.  e.g. W^6 = W^(6 mod {N}) = W^{6 % N}  (shown in the W Matrix tab)",
            f"  6.  Go to the  🔢 W Matrix  tab to see the fully solved answer →",
        ]
        for h in hints:
            tk.Label(hint, text=h, font=("Consolas", 9),
                     bg="#1a2a1a", fg=TEXT_MUTED).pack(anchor="w", pady=1)
    def _draw_question_matrix(self, parent, signal, N):
        """
        Draw the matrix like the textbook screenshot but with:
          - X(k) column on left  (unknowns — shown as X(0)=?, X(1)=? …)
          - W matrix in middle   (symbolic W^(nk) — no numeric values)
          - x(n) column on right (filled with actual signal values)
        """
        CELL_W = max(90, min(120, 700 // max(N, 1)))
        CELL_H = 44
        PAD_X  = 32
        PAD_Y  = 16

        mat_px_w = N * CELL_W
        mat_px_h = N * CELL_H
        total_h  = mat_px_h + PAD_Y * 2

        vec_w   = CELL_W + PAD_X * 2
        eq_w    = 36
        total_w = vec_w + eq_w + (mat_px_w + PAD_X*2) + eq_w + vec_w + 60

        c = tk.Canvas(parent, width=min(total_w, 1160),
                      height=total_h + 20, bg=BG_DARK, highlightthickness=0)
        c.pack(padx=24, pady=8)

        def bracket(x1, y1, x2, y2, left=True, color=TEXT_WHITE, lw=2):
            arm = 14
            if left:
                c.create_line(x1+arm, y1, x1, y1, fill=color, width=lw)
                c.create_line(x1, y1, x1, y2,     fill=color, width=lw)
                c.create_line(x1, y2, x1+arm, y2, fill=color, width=lw)
            else:
                c.create_line(x2-arm, y1, x2, y1, fill=color, width=lw)
                c.create_line(x2, y1, x2, y2,     fill=color, width=lw)
                c.create_line(x2, y2, x2-arm, y2, fill=color, width=lw)

        ox = 10
        oy = PAD_Y
        bracket(ox, oy, ox+vec_w, oy+total_h-PAD_Y, left=True,  color=ACCENT_GOLD, lw=3)
        bracket(ox, oy, ox+vec_w, oy+total_h-PAD_Y, left=False, color=ACCENT_GOLD, lw=3)
        for k in range(N):
            cy = oy + k*CELL_H + CELL_H//2
            c.create_text(ox+PAD_X+CELL_W//2 - 14, cy,
                          text=f"X({k})", fill=ACCENT_GOLD,
                          font=("Consolas", 12, "bold"))
            c.create_text(ox+PAD_X+CELL_W//2 + 18, cy,
                          text="= ?", fill=ACCENT_PINK,
                          font=("Consolas", 11, "bold"))
        ox += vec_w
        c.create_text(ox+eq_w//2, oy+total_h//2-PAD_Y//2,
                      text="=", fill=TEXT_WHITE, font=("Segoe UI", 20, "bold"))
        ox += eq_w
        w_ox = ox
        bracket(w_ox, oy, w_ox+mat_px_w+PAD_X*2, oy+total_h-PAD_Y,
                left=True,  color=ACCENT_TEAL, lw=3)
        bracket(w_ox, oy, w_ox+mat_px_w+PAD_X*2, oy+total_h-PAD_Y,
                left=False, color=ACCENT_TEAL, lw=3)

        for k in range(N):
            for n in range(N):
                exp_raw = n * k          # unreduced: W^0..W^(N-1)^2
                cx  = w_ox + PAD_X + n*CELL_W + CELL_W//2
                cy  = oy + k*CELL_H + CELL_H//2

                # Dim cell background — question style (no heatmap colour)
                c.create_rectangle(
                    w_ox+PAD_X + n*CELL_W + 3,
                    oy + k*CELL_H + 3,
                    w_ox+PAD_X + (n+1)*CELL_W - 3,
                    oy + (k+1)*CELL_H - 3,
                    fill=BG_CARD2, outline=BORDER)

                # W^exp_raw label — unreduced (e.g. W^6 stays W^6, not W^2)
                c.create_text(cx-6, cy, text="W",
                              fill=TEXT_WHITE, font=("Consolas", 11, "bold"))
                c.create_text(cx+8, cy-6, text=str(exp_raw),
                              fill=ACCENT_TEAL, font=("Consolas", 8, "bold"))

        ox += mat_px_w + PAD_X*2
        c.create_text(ox+eq_w//2, oy+total_h//2-PAD_Y//2,
                      text="×", fill=TEXT_WHITE, font=("Segoe UI", 16))
        ox += eq_w
        bracket(ox, oy, ox+vec_w, oy+total_h-PAD_Y, left=True,  color=ACCENT_PURP, lw=3)
        bracket(ox, oy, ox+vec_w, oy+total_h-PAD_Y, left=False, color=ACCENT_PURP, lw=3)
        for n in range(N):
            cy   = oy + n*CELL_H + CELL_H//2
            val  = signal[n] if n < len(signal) else 0+0j
            vstr = f"{val.real:.2f}" if val.imag == 0 else f"{val.real:.1f}{val.imag:+.1f}j"
            c.create_text(ox+PAD_X+CELL_W//2, cy-6,
                          text=f"x({n})", fill=ACCENT_PURP,
                          font=("Consolas", 9))
            c.create_text(ox+PAD_X+CELL_W//2, cy+8,
                          text=vstr, fill=TEXT_WHITE,
                          font=("Consolas", 11, "bold"))
    def _draw_signal_table(self, parent, signal, N):
        style = ttk.Style()
        style.configure("Q.Treeview",
                        background=BG_CARD, foreground=TEXT_WHITE,
                        fieldbackground=BG_CARD, rowheight=26,
                        font=("Consolas", 10))
        style.configure("Q.Treeview.Heading",
                        background=BG_CARD2, foreground=ACCENT_GOLD,
                        font=("Segoe UI", 10, "bold"), relief="flat")
        style.map("Q.Treeview",
                  background=[("selected", ACCENT_BLUE)])

        cols = ("n", "x(n)", "Re{x(n)}", "Im{x(n)}")
        tree = ttk.Treeview(parent, columns=cols, show="headings",
                             style="Q.Treeview", height=min(N, 8))
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=140, anchor="center")

        for n in range(N):
            val = signal[n] if n < len(signal) else 0+0j
            tree.insert("", "end", values=(
                n,
                f"{val.real:.4f}" + (f" + {val.imag:.4f}j" if val.imag else ""),
                f"{val.real:.4f}",
                f"{val.imag:.4f}",
            ))

        tree.pack(padx=24, pady=(0, 4))
