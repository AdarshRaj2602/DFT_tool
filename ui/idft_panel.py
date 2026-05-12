# ui/idft_panel.py Inverse DFT Solver — takes X[k] frequency coefficients as input, reconstructs x[n] step-by-step and plots the result. x(n) = (1/N) Σ X(k) · W_N^(-nk) for n = 0,1,...,N-1

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import math
import cmath
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from assets.themes.theme import *
from utils.validators    import parse_signal
from core.dft            import compute_idft, build_idft_w_matrix


class IDFTSolverPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG_DARK)
        self._fig = None
        self._build()
    def _build(self):
        pane = tk.PanedWindow(self, orient="horizontal",
                              bg=BG_DARK, sashrelief="flat",
                              sashwidth=6)
        pane.pack(fill="both", expand=True)
        left = tk.Frame(pane, bg=BG_CARD, width=370)
        left.pack_propagate(False)
        pane.add(left, minsize=320)
        right = tk.Frame(pane, bg=BG_DARK)
        pane.add(right, minsize=620)

        self._build_left(left)
        self._build_right(right)
    def _build_left(self, f):
        tk.Label(f, text="IDFT Parameters",
                 font=("Segoe UI", 13, "bold"),
                 bg=BG_CARD, fg=ACCENT_PURP).pack(anchor="w", padx=20, pady=(18, 4))
        tk.Frame(f, bg=BORDER, height=1).pack(fill="x", padx=20, pady=(0, 14))

        # Formula reminder
        box = tk.Frame(f, bg=BG_CARD2, padx=14, pady=10)
        box.pack(fill="x", padx=20, pady=(0, 14))
        tk.Label(box, text="x[n] = (1/N) Σ X[k] · W_N^(−nk)",
                 font=("Consolas", 9, "bold"), bg=BG_CARD2, fg=ACCENT_PURP).pack(anchor="w")
        tk.Label(box, text="W_N = e^(−j·2π/N)    n = 0..N-1",
                 font=("Consolas", 8), bg=BG_CARD2, fg=TEXT_MUTED).pack(anchor="w")

        # X[k] input
        self._sec(f, "Frequency Coefficients  X[k]")
        self.xk_text = tk.Text(f, height=5, font=FONT_MONO,
                                bg=BG_CARD2, fg=TEXT_WHITE,
                                insertbackground=ACCENT_PURP,
                                relief="flat", bd=0,
                                selectbackground=ACCENT_BLUE)
        self.xk_text.pack(fill="x", padx=20, ipady=6, ipadx=6)
        self.xk_text.insert("1.0", "10, -2+2j, -2, -2-2j")
        tk.Label(f, text="Enter DFT output X[k] — comma separated",
                 font=FONT_SMALL, bg=BG_CARD, fg=TEXT_MUTED).pack(anchor="w", padx=20, pady=(2, 12))

        # Tip: use DFT result
        tk.Label(f,
                 text="💡 Tip: Run the DFT Solver first, then paste X[k] values here",
                 font=FONT_SMALL, bg=BG_CARD, fg=ACCENT_GOLD,
                 wraplength=320, justify="left").pack(anchor="w", padx=20, pady=(0, 14))

        # N
        self._sec(f, "IDFT Size  N")
        n_row = tk.Frame(f, bg=BG_CARD)
        n_row.pack(fill="x", padx=20, pady=(0, 16))
        self.n_var = tk.StringVar(value="4")
        tk.Entry(n_row, textvariable=self.n_var,
                 font=("Segoe UI", 14, "bold"),
                 bg=BG_CARD2, fg=ACCENT_GOLD,
                 insertbackground=ACCENT_PURP,
                 relief="flat", bd=0, width=7, justify="center").pack(
                 side="left", ipady=8, ipadx=10)
        tk.Button(n_row, text="Auto", font=FONT_SMALL,
                  bg=BG_CARD2, fg=TEXT_MUTED,
                  bd=0, relief="flat", padx=8, pady=5, cursor="hand2",
                  command=self._auto_n).pack(side="left", padx=10)

        # Options
        self._sec(f, "Display Options")
        opts = tk.Frame(f, bg=BG_CARD)
        opts.pack(fill="x", padx=20, pady=(0, 16))
        self.show_steps = tk.BooleanVar(value=True)
        tk.Checkbutton(opts, text="Show step-by-step equations",
                       variable=self.show_steps, font=FONT_BODY,
                       bg=BG_CARD, fg=TEXT_WHITE, selectcolor=BG_CARD2,
                       activebackground=BG_CARD, cursor="hand2").pack(anchor="w")

        # Run
        tk.Button(f, text="  ▶  Run IDFT Simulation  ",
                  font=("Segoe UI", 13, "bold"),
                  bg="#6B21A8", fg=TEXT_WHITE,
                  activebackground="#7C3AED",
                  bd=0, relief="flat", pady=12, cursor="hand2",
                  command=self._run).pack(fill="x", padx=20, pady=(0, 8))

        tk.Button(f, text="🗑  Clear",
                  font=("Segoe UI", 10),
                  bg=BTN_RED, fg=TEXT_WHITE,
                  activebackground="#B91C1C",
                  bd=0, relief="flat", pady=8, cursor="hand2",
                  command=self._clear).pack(fill="x", padx=20, pady=(0, 20))

    def _sec(self, parent, label):
        tk.Label(parent, text=label, font=("Segoe UI", 10, "bold"),
                 bg=BG_CARD, fg=TEXT_MUTED).pack(anchor="w", padx=20, pady=(0, 4))
    def _build_right(self, parent):
        style = ttk.Style()
        style.configure("IDFT.TNotebook", background=BG_DARK, borderwidth=0)
        style.configure("IDFT.TNotebook.Tab",
                        background=BG_CARD, foreground=TEXT_MUTED,
                        padding=[16, 8], font=("Segoe UI", 10))
        style.map("IDFT.TNotebook.Tab",
                  background=[("selected", BG_CARD2)],
                  foreground=[("selected", ACCENT_PURP)])

        self.nb = ttk.Notebook(parent, style="IDFT.TNotebook")
        self.nb.pack(fill="both", expand=True, padx=6, pady=6)

        self.tab_mat  = tk.Frame(self.nb, bg=BG_DARK)
        self.tab_eq   = tk.Frame(self.nb, bg=BG_DARK)
        self.tab_plot = tk.Frame(self.nb, bg=BG_DARK)
        self.nb.add(self.tab_mat,  text="📋  IDFT Matrix")
        self.nb.add(self.tab_eq,   text="📐  IDFT Equations & Results")
        self.nb.add(self.tab_plot, text="📊  Reconstructed Signal Plot")

        for tab, msg in [(self.tab_mat,  "Run IDFT simulation to see the matrix →"),
                         (self.tab_eq,   "Run IDFT simulation to see equations →"),
                         (self.tab_plot, "Run IDFT simulation to see reconstructed signal →")]:
            tk.Label(tab, text=msg, font=("Segoe UI", 13),
                     bg=BG_DARK, fg=TEXT_MUTED).pack(expand=True)
    def _auto_n(self):
        raw = self.xk_text.get("1.0", "end").strip()
        n = len([v for v in raw.split(",") if v.strip()])
        self.n_var.set(str(n))

    def _clear(self):
        self.xk_text.delete("1.0", "end")
        self.xk_text.insert("1.0", "10, -2+2j, -2, -2-2j")
        self.n_var.set("4")
    def _run(self):
        raw = self.xk_text.get("1.0", "end").strip()
        try:
            X = parse_signal(raw)
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
            return
        try:
            N = int(self.n_var.get())
            if N <= 0: raise ValueError
        except Exception:
            messagebox.showerror("Input Error", "N must be a positive integer.")
            return

        # Pad/truncate
        if len(X) < N:
            X = list(X) + [0+0j] * (N - len(X))
        else:
            X = list(X[:N])

        x_rec  = compute_idft(X, N)
        W_inv  = build_idft_w_matrix(N)
        W_base = cmath.exp(-2j * math.pi / N)

        self._render_idft_matrix(X, x_rec, N)
        self._render_equations(X, x_rec, W_inv, W_base, N)
        self._render_plot(x_rec, N)
        self.nb.select(self.tab_mat)
    def _render_idft_matrix(self, X, x_rec, N):
        """Show the IDFT bracket-matrix equation in two forms:
          1. Initial  — raw exponents W^(-nk), e.g. W^0, W^-1 … W^-9
          2. Reduced  — exponents after mod(N), W^((-nk) mod N)
        """
        for w in self.tab_mat.winfo_children():
            w.destroy()

        from tkinter import ttk as _ttk
        import math as _math, cmath as _cmath
        outer = tk.Canvas(self.tab_mat, bg=BG_DARK, highlightthickness=0)
        vsb   = _ttk.Scrollbar(self.tab_mat, orient="vertical",   command=outer.yview)
        hsb   = _ttk.Scrollbar(self.tab_mat, orient="horizontal", command=outer.xview)
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
        hdr = tk.Frame(inner, bg=BG_DARK, pady=14, padx=22)
        hdr.pack(fill="x")
        tk.Label(hdr, text="IDFT Matrix Equation",
                 font=("Segoe UI", 15, "bold"),
                 bg=BG_DARK, fg=ACCENT_PURP).pack(side="left")
        tk.Label(hdr, text=f"   N = {N}    W_N = e^(−j·2π/{N})",
                 font=("Consolas", 11), bg=BG_DARK, fg=TEXT_MUTED).pack(side="left")
        tk.Frame(inner, bg=BORDER, height=1).pack(fill="x", padx=22, pady=(0, 10))

        # formula reminder
        box = tk.Frame(inner, bg=BG_CARD2, padx=18, pady=12)
        box.pack(fill="x", padx=22, pady=(0, 14))
        tk.Label(box, text="x[n]  =  (1/N) Σ  X[k] · W_N^(−n·k)       k = 0, 1, …, N−1",
                 font=("Consolas", 12, "bold"), bg=BG_CARD2, fg=ACCENT_PURP).pack(anchor="w")
        tk.Label(box, text=f"W_N  =  e^(−j·2π/N)  =  e^(−j·2π/{N})         N = {N}",
                 font=("Consolas", 10), bg=BG_CARD2, fg=TEXT_MUTED).pack(anchor="w", pady=(4, 0))
        sec1 = tk.Frame(inner, bg=BG_CARD, padx=18, pady=10)
        sec1.pack(fill="x", padx=22, pady=(0, 8))
        tk.Label(sec1,
                 text="📋  Step 1 — Initial Matrix  (raw exponents, before mod reduction)",
                 font=("Segoe UI", 11, "bold"), bg=BG_CARD, fg=ACCENT_GOLD).pack(anchor="w")
        tk.Label(sec1,
                 text="Each cell shows W^(−n·k) with the full (unreduced) exponent",
                 font=("Segoe UI", 9), bg=BG_CARD, fg=TEXT_MUTED).pack(anchor="w")

        self._draw_idft_bracket(inner, X, x_rec, N, reduced=False)
        sec2 = tk.Frame(inner, bg=BG_CARD, padx=18, pady=10)
        sec2.pack(fill="x", padx=22, pady=(16, 8))
        tk.Label(sec2,
                 text="🔢  Step 2 — W Matrix  (exponents reduced with mod N)",
                 font=("Segoe UI", 11, "bold"), bg=BG_CARD, fg=ACCENT_TEAL).pack(anchor="w")
        tk.Label(sec2,
                 text=f"W^(−nk) = W^((−nk) mod {N})   because W^N = 1",
                 font=("Segoe UI", 9), bg=BG_CARD, fg=TEXT_MUTED).pack(anchor="w")

        self._draw_idft_bracket(inner, X, x_rec, N, reduced=True)
        tk.Label(inner, text="Exponent reduction table  (−nk) mod N",
                 font=("Segoe UI", 11, "bold"),
                 bg=BG_DARK, fg=ACCENT_BLUE).pack(anchor="w", padx=22, pady=(18, 6))
        self._draw_mod_table(inner, N)

    def _draw_idft_bracket(self, parent, X, x_rec, N, reduced: bool):
        """Bracket-style matrix for IDFT.  reduced=False → raw W^(-nk) exponents."""
        import math as _math, cmath as _cmath

        CELL_W = max(90, min(120, 700 // max(N, 1)))
        CELL_H = 44
        PAD_X  = 32
        PAD_Y  = 16

        mat_px_w = N * CELL_W
        mat_px_h = N * CELL_H
        total_h  = mat_px_h + PAD_Y * 2
        vec_w    = CELL_W + PAD_X * 2
        eq_w     = 46
        scale_w  = 60          # (1/N) label width
        total_w  = vec_w + eq_w + scale_w + (mat_px_w + PAD_X*2) + eq_w + vec_w + 60

        c = tk.Canvas(parent, width=min(total_w, 1200),
                      height=total_h + 20, bg=BG_DARK, highlightthickness=0)
        c.pack(padx=22, pady=6)

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

        mid_y = PAD_Y + total_h // 2 - PAD_Y // 2
        ox = 10
        oy = PAD_Y
        bracket(ox, oy, ox+vec_w, oy+total_h-PAD_Y, left=True,  color=ACCENT_PURP, lw=3)
        bracket(ox, oy, ox+vec_w, oy+total_h-PAD_Y, left=False, color=ACCENT_PURP, lw=3)
        for n in range(N):
            cy = oy + n*CELL_H + CELL_H//2
            val  = x_rec[n] if n < len(x_rec) else 0+0j
            vstr = f"{val.real:.2f}" if abs(val.imag) < 1e-9 else f"{val.real:.1f}{val.imag:+.1f}j"
            c.create_text(ox+PAD_X+CELL_W//2, cy-6,
                          text=f"x({n})", fill=ACCENT_PURP, font=("Consolas", 9))
            c.create_text(ox+PAD_X+CELL_W//2, cy+8,
                          text=vstr, fill=TEXT_WHITE, font=("Consolas", 11, "bold"))
        ox += vec_w
        c.create_text(ox+eq_w//2, mid_y, text="=",
                      fill=TEXT_WHITE, font=("Segoe UI", 20, "bold"))
        ox += eq_w
        c.create_text(ox + scale_w//2 - 4, mid_y - 8,
                      text=f"1", fill=ACCENT_GOLD, font=("Consolas", 11, "bold"))
        c.create_line(ox + 6, mid_y, ox + scale_w - 10, mid_y,
                      fill=ACCENT_GOLD, width=2)
        c.create_text(ox + scale_w//2 - 4, mid_y + 10,
                      text=f"{N}", fill=ACCENT_GOLD, font=("Consolas", 11, "bold"))
        ox += scale_w
        w_ox = ox
        col  = ACCENT_TEAL if reduced else ACCENT_BLUE
        bracket(w_ox, oy, w_ox+mat_px_w+PAD_X*2, oy+total_h-PAD_Y, left=True,  color=col, lw=3)
        bracket(w_ox, oy, w_ox+mat_px_w+PAD_X*2, oy+total_h-PAD_Y, left=False, color=col, lw=3)

        for n in range(N):
            for k in range(N):
                raw_exp  = -(n * k)            # e.g. 0, -1, -2, ..., -9
                red_exp  = (-n * k) % N        # reduced to 0..N-1

                cx = w_ox + PAD_X + k*CELL_W + CELL_W//2
                cy = oy + n*CELL_H + CELL_H//2

                # cell bg
                bg_col = BG_CARD2 if not reduced else "#1a2535"
                c.create_rectangle(
                    w_ox+PAD_X + k*CELL_W + 3, oy + n*CELL_H + 3,
                    w_ox+PAD_X + (k+1)*CELL_W - 3, oy + (n+1)*CELL_H - 3,
                    fill=bg_col, outline=BORDER)

                # exponent label
                if reduced:
                    exp_str = str(red_exp)
                    exp_col = ACCENT_TEAL
                    c.create_text(cx-6, cy, text="W",
                                  fill=TEXT_WHITE, font=("Consolas", 11, "bold"))
                    c.create_text(cx+8, cy-6, text=exp_str,
                                  fill=exp_col, font=("Consolas", 8, "bold"))
                else:
                    # Show as W^(-exp) with a minus sign
                    exp_str = str(raw_exp)   # e.g. "0", "-3", "-6"
                    c.create_text(cx-6, cy, text="W",
                                  fill=TEXT_WHITE, font=("Consolas", 11, "bold"))
                    c.create_text(cx+8, cy-6, text=exp_str,
                                  fill=ACCENT_BLUE, font=("Consolas", 8, "bold"))

        ox += mat_px_w + PAD_X * 2
        c.create_text(ox+eq_w//2, mid_y, text="×",
                      fill=TEXT_WHITE, font=("Segoe UI", 16))
        ox += eq_w
        bracket(ox, oy, ox+vec_w, oy+total_h-PAD_Y, left=True,  color=ACCENT_GOLD, lw=3)
        bracket(ox, oy, ox+vec_w, oy+total_h-PAD_Y, left=False, color=ACCENT_GOLD, lw=3)
        for k in range(N):
            cy  = oy + k*CELL_H + CELL_H//2
            val = X[k] if k < len(X) else 0+0j
            vstr = f"{val.real:.2f}" if abs(val.imag) < 1e-9 else f"{val.real:.1f}{val.imag:+.1f}j"
            c.create_text(ox+PAD_X+CELL_W//2, cy-6,
                          text=f"X({k})", fill=ACCENT_GOLD, font=("Consolas", 9))
            c.create_text(ox+PAD_X+CELL_W//2, cy+8,
                          text=vstr, fill=TEXT_WHITE, font=("Consolas", 11, "bold"))

    def _draw_mod_table(self, parent, N):
        """Show a grid: rows=n, cols=k, cell = (−nk) mod N"""
        from tkinter import ttk as _ttk
        style = _ttk.Style()
        style.configure("ModT.Treeview",
                        background=BG_CARD, foreground=TEXT_WHITE,
                        fieldbackground=BG_CARD, rowheight=26,
                        font=("Consolas", 10))
        style.configure("ModT.Treeview.Heading",
                        background=BG_CARD2, foreground=ACCENT_PURP,
                        font=("Segoe UI", 10, "bold"), relief="flat")
        style.map("ModT.Treeview", background=[("selected", ACCENT_BLUE)])

        cols = ["n\\k"] + [str(k) for k in range(N)]
        tree = _ttk.Treeview(parent, columns=cols, show="headings",
                              style="ModT.Treeview", height=min(N+1, 8))
        tree.heading("n\\k", text="n \\ k")
        tree.column("n\\k", width=60, anchor="center")
        for k in range(N):
            tree.heading(str(k), text=f"k={k}")
            tree.column(str(k), width=90, anchor="center")

        for n in range(N):
            row = [f"n={n}"] + [f"({-(n*k)}) mod {N} = {(-n*k)%N}" for k in range(N)]
            tree.insert("", "end", values=row)
        tree.pack(padx=22, pady=(0, 20))
    def _render_equations(self, X, x_rec, W_inv, W_base, N):
        for w in self.tab_eq.winfo_children():
            w.destroy()

        t = scrolledtext.ScrolledText(
            self.tab_eq, font=FONT_MONO, bg=BG_CARD, fg=TEXT_WHITE,
            insertbackground=ACCENT_PURP, relief="flat", bd=0,
            selectbackground=ACCENT_BLUE, wrap="none")
        t.pack(fill="both", expand=True, padx=4, pady=4)

        t.tag_configure("title",  font=("Consolas", 13, "bold"), foreground=ACCENT_PURP)
        t.tag_configure("head",   font=("Consolas", 11, "bold"), foreground=ACCENT_BLUE)
        t.tag_configure("eq",     font=("Consolas", 10),          foreground=TEXT_WHITE)
        t.tag_configure("result", font=("Consolas", 10, "bold"),  foreground=ACCENT_GOLD)
        t.tag_configure("muted",  font=("Consolas", 9),           foreground=TEXT_MUTED)

        def w(text, tag="eq"):
            t.insert("end", text, tag)

        w("╔══════════════════════════════════════════════════════════════╗\n", "title")
        w("   INVERSE DISCRETE FOURIER TRANSFORM — STEP-BY-STEP\n",            "title")
        w("╚══════════════════════════════════════════════════════════════╝\n\n","title")

        w("  Governing Equation:\n", "head")
        w("  x[n] = (1/N) · Σ  X[k] · W_N^(−n·k)      k = 0 .. N-1\n", "eq")
        w(f"  W_N = e^(−j·2π/{N}) = {W_base:.6f}\n", "muted")
        w(f"  N = {N}\n\n", "muted")

        w("━" * 66 + "\n", "muted")
        w("  INPUT FREQUENCY COEFFICIENTS  X[k]\n", "head")
        w("━" * 66 + "\n", "muted")
        for k, val in enumerate(X):
            mag = abs(val)
            ph  = math.degrees(cmath.phase(val))
            s   = f"  X[{k:2d}] = {val.real:+.4f} {val.imag:+.4f}j"
            s  += f"   |X|={mag:.4f}   ∠={ph:+.2f}°"
            w(s + "\n", "eq")

        if self.show_steps.get():
            w("\n" + "━" * 66 + "\n", "muted")
            w("  COMPUTATION  x[n] — Step by Step\n", "head")
            w("━" * 66 + "\n", "muted")
            for n in range(N):
                w(f"\n  ── x[{n}]  (n = {n}) ──\n", "head")
                w(f"  x[{n}] = (1/{N}) × ( ", "eq")
                terms = [f"X[{k}]·W^(−{(n*k)%N})" for k in range(N)]
                w(" + ".join(terms) + " )\n", "eq")

                w(f"       = (1/{N}) × ( ", "eq")
                num_parts = []
                for k in range(N):
                    exp_val = (-(n * k)) % N
                    ww = (W_base ** (-(n * k)))
                    num_parts.append(
                        f"({X[k].real:.2f}{X[k].imag:+.2f}j)·({ww.real:+.3f}{ww.imag:+.3f}j)")
                w(" +\n              ".join(num_parts) + " )\n", "eq")

                res = x_rec[n]
                w(f"  x[{n}] = {res.real:+.6f}", "result")
                if abs(res.imag) > 1e-9:
                    w(f" {res.imag:+.6f}j", "result")
                w("\n", "result")

        w("\n" + "━" * 66 + "\n", "muted")
        w("  RECONSTRUCTED SIGNAL  x[n]\n", "head")
        w("━" * 66 + "\n", "muted")
        for n, val in enumerate(x_rec):
            real_str = f"{val.real:+.6f}"
            imag_str = f"{val.imag:+.6f}j" if abs(val.imag) > 1e-9 else ""
            w(f"  x[{n:2d}] = {real_str}{imag_str}\n", "result")

        t.configure(state="disabled")
    def _render_plot(self, x_rec, N):
        for w in self.tab_plot.winfo_children():
            w.destroy()

        ns    = list(range(N))
        reals = [v.real for v in x_rec]
        imags = [v.imag for v in x_rec]

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 5.5), facecolor=BG_DARK)
        fig.subplots_adjust(hspace=0.45)

        for ax, yd, color, title, yl in [
            (ax1, reals, ACCENT_PURP, "Reconstructed Signal  Re{x[n]}", "Re{x[n]}"),
            (ax2, imags, ACCENT_PINK, "Imaginary Part  Im{x[n]}",        "Im{x[n]}"),
        ]:
            ax.set_facecolor(BG_CARD)
            for sp in ax.spines.values():
                sp.set_edgecolor(BORDER)
            ax.tick_params(colors=TEXT_MUTED, labelsize=8)
            ax.set_title(title, color=TEXT_WHITE, fontsize=10, fontweight="bold", pad=8)
            ax.set_xlabel("n  (sample index)", color=TEXT_MUTED, fontsize=8)
            ax.set_ylabel(yl, color=TEXT_MUTED, fontsize=8)
            ax.grid(True, color=BORDER, linestyle="--", linewidth=0.5, alpha=0.6)
            ml, sl, bl = ax.stem(ns, yd)
            plt.setp(sl, color=color, linewidth=2)
            plt.setp(ml, color=color, markersize=7)
            plt.setp(bl, color=BORDER)

        self._fig = fig
        fig.patch.set_facecolor(BG_DARK)

        cv = FigureCanvasTkAgg(fig, master=self.tab_plot)
        cv.draw()
        cv.get_tk_widget().pack(fill="both", expand=True)

        btn_row = tk.Frame(self.tab_plot, bg=BG_DARK)
        btn_row.pack(fill="x")
        tk.Button(btn_row, text="💾  Save Plot",
                  font=FONT_SMALL, bg=BG_CARD2, fg=ACCENT_PURP,
                  bd=0, relief="flat", padx=12, pady=6, cursor="hand2",
                  command=self._save_plot).pack(side="right", padx=12, pady=8)

    def _save_plot(self):
        if not self._fig: return
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("PDF", "*.pdf")])
        if path:
            self._fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=BG_DARK)
            messagebox.showinfo("Saved", f"Saved to:\n{path}")
