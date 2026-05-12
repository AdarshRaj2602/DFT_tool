# ui/home_page.py — homepage: hero, feature cards, live preview, formula, steps

import tkinter as tk
from tkinter import ttk
import math
import cmath

from assets.themes.theme import *


class HomePage(tk.Frame):
    def __init__(self, parent, nav_callback):
        super().__init__(parent, bg=BG_DARK)
        self._nav        = nav_callback
        self._anim_angle = 0
        self._anim_id    = None
        self._demo_mode  = tk.StringVar(value="magnitude")
        self._build()

    def _build(self):
        canvas = tk.Canvas(self, bg=BG_DARK, highlightthickness=0)
        sb = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self._scroll_frame = tk.Frame(canvas, bg=BG_DARK)
        self._scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self._scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        canvas.bind_all("<MouseWheel>",
            lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))

        f = self._scroll_frame
        self._build_hero(f)
        self._build_cards(f)
        self._build_live_demo(f)
        self._build_formula(f)
        self._build_steps(f)
        self._animate()

    def _build_hero(self, f):
        hero = tk.Frame(f, bg=BG_HERO)
        hero.pack(fill="x", padx=30, pady=(28, 0))

        left = tk.Frame(hero, bg=BG_HERO, pady=36, padx=40)
        left.pack(side="left", fill="both", expand=True)

        tk.Label(left, text="Discrete Fourier", font=("Segoe UI", 36, "bold"),
                 bg=BG_HERO, fg=ACCENT_TEAL).pack(anchor="w")
        tk.Label(left, text="Transform Visualizer", font=("Segoe UI", 28),
                 bg=BG_HERO, fg=TEXT_WHITE).pack(anchor="w")
        tk.Label(left, text="Compute · Visualize · Understand  —  step by step",
                 font=("Segoe UI", 12), bg=BG_HERO, fg=TEXT_MUTED).pack(anchor="w", pady=(8, 20))

        btn_row = tk.Frame(left, bg=BG_HERO)
        btn_row.pack(anchor="w")
        tk.Button(btn_row, text="  ▶  Launch Solver  ",
                  font=("Segoe UI", 12, "bold"),
                  bg=ACCENT_TEAL, fg="#000000", bd=0, relief="flat",
                  padx=16, pady=10, cursor="hand2",
                  command=lambda: self._nav("solver")).pack(side="left")
        tk.Button(btn_row, text="  ℹ  About  ",
                  font=("Segoe UI", 12),
                  bg=BG_CARD2, fg=TEXT_WHITE, bd=0, relief="flat",
                  padx=16, pady=10, cursor="hand2",
                  command=lambda: self._nav("about")).pack(side="left", padx=10)

        right = tk.Frame(hero, bg=BG_HERO, pady=20, padx=20)
        right.pack(side="right")
        self._hero_canvas = tk.Canvas(right, width=280, height=160,
                                      bg=BG_HERO, highlightthickness=0)
        self._hero_canvas.pack()

    def _animate(self):
        # animated sine wave + freq bars on the hero card
        c = self._hero_canvas
        c.delete("wave")
        w, h = 280, 160
        pts = []
        for px in range(w):
            t  = px / w * 4 * math.pi + self._anim_angle
            py = h/2 - 50*math.sin(t) - 20*math.sin(2*t + 0.5)
            pts.extend([px, py])
        if len(pts) >= 4:
            c.create_line(*pts, fill=ACCENT_TEAL, width=2, smooth=True, tags="wave")
        for i in range(8):
            bx  = 20 + i * 32
            mag = abs(20 * math.sin(i * self._anim_angle * 0.3 + i))
            c.create_rectangle(bx, h - mag - 5, bx + 18, h - 5,
                                fill=ACCENT_BLUE, outline="", tags="wave")
        self._anim_angle += 0.05
        self._anim_id = self.after(40, self._animate)

    def destroy(self):
        if self._anim_id:
            self.after_cancel(self._anim_id)
        super().destroy()

    def _build_cards(self, f):
        row = tk.Frame(f, bg=BG_DARK)
        row.pack(fill="x", padx=30, pady=28)

        cards = [
            ("📡", "What is DFT?",       ACCENT_TEAL,
             "Converts a finite signal into complex frequency components — "
             "the backbone of digital signal processing."),
            ("🧮", "Twiddle (W) Matrix", ACCENT_BLUE,
             "W_N^(nk) = e^(−j·2π·nk/N). Builds, colours, and annotates "
             "the full W matrix like the textbook."),
            ("📊", "4 Spectrum Plots",   ACCENT_PURP,
             "Magnitude, Phase, Real, and Imaginary spectra as "
             "interactive stem plots after every run."),
            ("📂", "Flexible Input",     ACCENT_GOLD,
             "Type values manually or import CSV / TXT / Excel. "
             "Works well for EEG and biomedical signals."),
        ]

        for i, (icon, title, color, desc) in enumerate(cards):
            card = tk.Frame(row, bg=BG_CARD, padx=18, pady=18)
            card.grid(row=0, column=i, padx=8, sticky="nsew")
            row.columnconfigure(i, weight=1)

            def _enter(e, c=card):
                c.configure(bg=BG_CARD2)
                for ch in c.winfo_children():
                    try: ch.configure(bg=BG_CARD2)
                    except: pass
            def _leave(e, c=card):
                c.configure(bg=BG_CARD)
                for ch in c.winfo_children():
                    try: ch.configure(bg=BG_CARD)
                    except: pass
            card.bind("<Enter>", _enter)
            card.bind("<Leave>", _leave)

            tk.Label(card, text=icon, font=("Segoe UI", 28),
                     bg=BG_CARD, fg=color).pack(anchor="w")
            tk.Label(card, text=title, font=("Segoe UI", 12, "bold"),
                     bg=BG_CARD, fg=color).pack(anchor="w", pady=(4, 6))
            tk.Label(card, text=desc, font=FONT_SMALL,
                     bg=BG_CARD, fg=TEXT_MUTED,
                     wraplength=210, justify="left").pack(anchor="w")

    def _build_live_demo(self, f):
        outer = tk.Frame(f, bg=BG_DARK, padx=30)
        outer.pack(fill="x", pady=(0, 8))

        # header row: title on left, magnitude/phase toggle on right
        hdr = tk.Frame(outer, bg=BG_DARK)
        hdr.pack(fill="x", pady=(0, 10))

        left_hdr = tk.Frame(hdr, bg=BG_DARK)
        left_hdr.pack(side="left", fill="y")
        tk.Label(left_hdr, text="⚡  Live DFT Preview",
                 font=("Segoe UI", 13, "bold"),
                 bg=BG_DARK, fg=ACCENT_GOLD).pack(anchor="w")
        tk.Label(left_hdr,
                 text="Type comma-separated values and watch the spectrum update live.",
                 font=FONT_SMALL, bg=BG_DARK, fg=TEXT_MUTED).pack(anchor="w", pady=(2, 0))

        toggle = tk.Frame(hdr, bg=BG_DARK)
        toggle.pack(side="right", anchor="s")
        self._btn_mag = tk.Button(toggle, text="Magnitude",
                                   font=("Segoe UI", 9, "bold"),
                                   bg=ACCENT_TEAL, fg="#000", bd=0, relief="flat",
                                   padx=12, pady=4, cursor="hand2",
                                   command=lambda: self._set_mode("magnitude"))
        self._btn_mag.pack(side="left")
        self._btn_phase = tk.Button(toggle, text="Phase",
                                     font=("Segoe UI", 9, "bold"),
                                     bg=BG_CARD2, fg=TEXT_MUTED, bd=0, relief="flat",
                                     padx=12, pady=4, cursor="hand2",
                                     command=lambda: self._set_mode("phase"))
        self._btn_phase.pack(side="left", padx=(2, 0))

        # card body
        card = tk.Frame(outer, bg=BG_CARD, padx=22, pady=18)
        card.pack(fill="x")

        # input row with inline label
        entry_row = tk.Frame(card, bg=BG_CARD2, padx=12, pady=2)
        entry_row.pack(fill="x", pady=(0, 14))
        tk.Label(entry_row, text="x[n]  =", font=("Consolas", 10),
                 bg=BG_CARD2, fg=TEXT_MUTED).pack(side="left")
        self._demo_entry = tk.Entry(entry_row, font=("Consolas", 12),
                                     bg=BG_CARD2, fg=ACCENT_TEAL,
                                     insertbackground=ACCENT_TEAL,
                                     relief="flat", bd=0)
        self._demo_entry.insert(0, "1, 2, 3, 4")
        self._demo_entry.pack(side="left", fill="x", expand=True, ipady=8, ipadx=6)
        self._demo_entry.bind("<KeyRelease>", self._update_demo)

        self._demo_canvas = tk.Canvas(card, height=130,
                                       bg="#0D1117", highlightthickness=0)
        self._demo_canvas.pack(fill="x")

        # one-liner stats below the chart
        self._status_var = tk.StringVar(value="")
        tk.Label(card, textvariable=self._status_var,
                 font=("Consolas", 9), bg=BG_CARD,
                 fg=TEXT_MUTED).pack(anchor="w", pady=(8, 0))

        self._update_demo()

    def _set_mode(self, mode):
        self._demo_mode.set(mode)
        if mode == "magnitude":
            self._btn_mag.configure(bg=ACCENT_TEAL, fg="#000")
            self._btn_phase.configure(bg=BG_CARD2, fg=TEXT_MUTED)
        else:
            self._btn_mag.configure(bg=BG_CARD2, fg=TEXT_MUTED)
            self._btn_phase.configure(bg=ACCENT_PURP, fg="#000")
        self._update_demo()

    def _update_demo(self, _=None):
        raw = self._demo_entry.get()
        try:
            vals = [complex(v.strip()) for v in raw.split(",") if v.strip()]
            if not vals:
                return
            N  = len(vals)
            wn = cmath.exp(-2j * math.pi / N)
            X  = [sum(vals[n] * wn**(n*k) for n in range(N)) for k in range(N)]

            if self._demo_mode.get() == "magnitude":
                data   = [abs(v) for v in X]
                unit   = ""
                colors = [ACCENT_TEAL, ACCENT_BLUE, ACCENT_PURP, ACCENT_GOLD,
                          ACCENT_PINK, ACCENT_TEAL, ACCENT_BLUE, ACCENT_PURP]
            else:
                data   = [math.degrees(cmath.phase(v)) for v in X]
                unit   = "°"
                colors = [ACCENT_PURP] * 8

            mx = max(abs(d) for d in data) if data else 1
            if mx == 0:
                mx = 1

            peak_k = max(range(N), key=lambda i: abs(X[i]))
            total  = sum(abs(v) for v in X)
            mode_label = "|X[k]|" if self._demo_mode.get() == "magnitude" else "∠X[k]"
            self._status_var.set(
                f"N = {N}   |   {mode_label}   |   "
                f"peak at k={peak_k}  ({abs(X[peak_k]):.2f})   |   "
                f"Σ|X| = {total:.2f}")
        except Exception:
            return

        c   = self._demo_canvas
        c.delete("all")
        cw  = c.winfo_width() or 620
        ch  = 130
        pad = 36
        bot = ch - 18  # baseline y

        # faint grid lines
        for ratio in [0.25, 0.5, 0.75, 1.0]:
            gy = bot - (bot - 14) * ratio
            c.create_line(pad, gy, cw - pad, gy, fill="#1e2a38", dash=(4, 4))

        slot_w = (cw - pad * 2) / max(N, 1)
        bar_w  = max(8, int(slot_w * 0.55))

        for k, val in enumerate(data):
            ratio = abs(val) / mx
            bh    = max(3, int((bot - 18) * ratio))
            bx    = int(pad + slot_w * k + slot_w / 2)
            col   = colors[k % len(colors)]

            # bar body
            c.create_rectangle(bx - bar_w//2, bot - bh,
                                bx + bar_w//2, bot,
                                fill=col, outline="")
            # thin bright cap for depth
            c.create_rectangle(bx - bar_w//2, bot - bh,
                                bx + bar_w//2, bot - bh + 3,
                                fill="#ffffff", outline="", stipple="gray25")

            disp = f"{val:.1f}{unit}"
            c.create_text(bx, bot - bh - 9, text=disp,
                          fill=col, font=("Consolas", 7, "bold"))
            c.create_text(bx, bot + 6, text=f"k={k}",
                          fill=TEXT_MUTED, font=("Segoe UI", 7))

    def _build_formula(self, f):
        outer = tk.Frame(f, bg=BG_DARK, padx=30)
        outer.pack(fill="x", pady=(0, 8))

        tk.Label(outer, text="Core DFT Formula",
                 font=("Segoe UI", 13, "bold"),
                 bg=BG_DARK, fg=TEXT_WHITE).pack(anchor="w")
        tk.Frame(outer, bg=ACCENT_TEAL, height=2).pack(fill="x", pady=(4, 12))

        card = tk.Frame(outer, bg=BG_CARD)
        card.pack(fill="x")
        card.columnconfigure(0, weight=3)
        card.columnconfigure(1, weight=2)

        # left: main summation + W_N definition
        left = tk.Frame(card, bg=BG_CARD, padx=28, pady=26)
        left.grid(row=0, column=0, sticky="nsew")

        tk.Label(left, text="Synthesis",
                 font=("Segoe UI", 9, "bold"),
                 bg=BG_CARD, fg=TEXT_MUTED).pack(anchor="w")

        main_row = tk.Frame(left, bg=BG_CARD)
        main_row.pack(anchor="w", pady=(4, 0))
        tk.Frame(main_row, bg=ACCENT_TEAL, width=4).pack(side="left", fill="y", padx=(0, 14))
        fcol = tk.Frame(main_row, bg=BG_CARD)
        fcol.pack(side="left")
        tk.Label(fcol, text="X[k]  =  Σ  x[n] · W_N^(n·k)",
                 font=("Consolas", 16, "bold"),
                 bg=BG_CARD, fg=ACCENT_TEAL).pack(anchor="w")
        tk.Label(fcol, text="n = 0, 1, …, N−1",
                 font=("Consolas", 10),
                 bg=BG_CARD, fg=TEXT_MUTED).pack(anchor="w", pady=(3, 0))

        tk.Frame(left, bg=BORDER, height=1).pack(fill="x", pady=(18, 14))

        def_row = tk.Frame(left, bg=BG_CARD)
        def_row.pack(anchor="w")
        tk.Frame(def_row, bg=ACCENT_BLUE, width=4).pack(side="left", fill="y", padx=(0, 14))
        tk.Label(def_row, text="W_N  =  e^(−j · 2π / N)",
                 font=("Consolas", 13, "bold"),
                 bg=BG_CARD, fg=ACCENT_BLUE).pack(side="left")

        # right: magnitude + phase in polar form
        right = tk.Frame(card, bg="#111820", padx=28, pady=26)
        right.grid(row=0, column=1, sticky="nsew")

        tk.Label(right, text="Polar form",
                 font=("Segoe UI", 9, "bold"),
                 bg="#111820", fg=TEXT_MUTED).pack(anchor="w", pady=(0, 10))

        for sym, expr, col in [
            ("|X[k]|", "=  √( Re²{X[k]} + Im²{X[k]} )", ACCENT_PURP),
            ("∠X[k]",  "=  arctan( Im{X[k]} / Re{X[k]} )", ACCENT_GOLD),
        ]:
            rf = tk.Frame(right, bg="#111820", pady=6)
            rf.pack(fill="x")
            tk.Frame(rf, bg=col, width=3).pack(side="left", fill="y", padx=(0, 12))
            inner = tk.Frame(rf, bg="#111820")
            inner.pack(side="left")
            tk.Label(inner, text=sym,
                     font=("Consolas", 11, "bold"),
                     bg="#111820", fg=col).pack(anchor="w")
            tk.Label(inner, text=expr,
                     font=("Consolas", 9),
                     bg="#111820", fg=TEXT_MUTED).pack(anchor="w")

    def _build_steps(self, f):
        outer = tk.Frame(f, bg=BG_DARK)
        outer.pack(fill="x", padx=30, pady=(0, 36))

        tk.Label(outer, text="How This Tool Works",
                 font=("Segoe UI", 14, "bold"),
                 bg=BG_DARK, fg=TEXT_WHITE).pack(anchor="w", pady=(0, 14))

        steps = [
            ("01", ACCENT_TEAL, "Enter Signal x[n]",
             "Type values like  1, 2, 3, 4  or import from CSV / TXT / Excel."),
            ("02", ACCENT_BLUE, "Set DFT Size N",
             "Enter N or click Auto to match signal length. Zero-padding applied if N > signal."),
            ("03", ACCENT_PURP, "W Matrix Built",
             "Twiddle matrix W_N^(n·k) assembled and rendered as a colour-mapped bracket matrix."),
            ("04", ACCENT_GOLD, "X[k] Computed Step-by-Step",
             "Each X[k] expansion shown symbolically with actual twiddle values substituted."),
            ("05", ACCENT_PINK, "Spectrum Visualized",
             "Magnitude, Phase, Real, and Imaginary spectra plotted and ready to export."),
        ]

        for num, color, title, desc in steps:
            row = tk.Frame(outer, bg=BG_CARD, pady=12, padx=16)
            row.pack(fill="x", pady=3)
            tk.Label(row, text=num, font=("Consolas", 20, "bold"),
                     bg=BG_CARD, fg=color, width=3).pack(side="left")
            tk.Frame(row, bg=color, width=3).pack(side="left", fill="y", padx=14)
            info = tk.Frame(row, bg=BG_CARD)
            info.pack(side="left", fill="x", expand=True)
            tk.Label(info, text=title, font=("Segoe UI", 11, "bold"),
                     bg=BG_CARD, fg=TEXT_WHITE).pack(anchor="w")
            tk.Label(info, text=desc, font=FONT_SMALL,
                     bg=BG_CARD, fg=TEXT_MUTED).pack(anchor="w")
