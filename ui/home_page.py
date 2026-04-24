"""
ui/home_page.py
Interactive Home Page with animated hero and live mini-DFT demo.
"""

import tkinter as tk
from tkinter import ttk
import math
import cmath

from assets.themes.theme import *


class HomePage(tk.Frame):
    def __init__(self, parent, nav_callback):
        super().__init__(parent, bg=BG_DARK)
        self._nav = nav_callback
        self._anim_angle = 0
        self._anim_id    = None
        self._build()

    def _build(self):
        # Scrollable canvas
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

        # ── 1. HERO ──────────────────────────────────────────────────────
        self._build_hero(f)

        # ── 2. FEATURE CARDS ─────────────────────────────────────────────
        self._build_cards(f)

        # ── 3. LIVE SIGNAL DEMO ──────────────────────────────────────────
        self._build_live_demo(f)

        # ── 4. DFT FORMULA BLOCK ─────────────────────────────────────────
        self._build_formula(f)

        # ── 5. HOW IT WORKS ──────────────────────────────────────────────
        self._build_steps(f)

        # Start animation
        self._animate()

    # ── HERO ─────────────────────────────────────────────────────────────
    def _build_hero(self, f):
        hero = tk.Frame(f, bg=BG_HERO, pady=0)
        hero.pack(fill="x", padx=30, pady=(28, 0))

        # Left: text
        left = tk.Frame(hero, bg=BG_HERO, pady=36, padx=40)
        left.pack(side="left", fill="both", expand=True)

        tk.Label(left, text="Discrete Fourier", font=("Segoe UI", 36, "bold"),
                 bg=BG_HERO, fg=ACCENT_TEAL).pack(anchor="w")
        tk.Label(left, text="Transform Visualizer", font=("Segoe UI", 28),
                 bg=BG_HERO, fg=TEXT_WHITE).pack(anchor="w")
        tk.Label(left,
                 text="Compute · Visualize · Understand  —  step by step",
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

        # Right: animated canvas
        right = tk.Frame(hero, bg=BG_HERO, pady=20, padx=20)
        right.pack(side="right")
        self._hero_canvas = tk.Canvas(right, width=280, height=160,
                                       bg=BG_HERO, highlightthickness=0)
        self._hero_canvas.pack()

    def _animate(self):
        """Draw an animated sine wave on the hero canvas."""
        c = self._hero_canvas
        c.delete("wave")
        w, h = 280, 160
        pts = []
        for px in range(w):
            t = px / w * 4 * math.pi + self._anim_angle
            py = h/2 - 50 * math.sin(t) - 20 * math.sin(2*t + 0.5)
            pts.extend([px, py])
        if len(pts) >= 4:
            c.create_line(*pts, fill=ACCENT_TEAL, width=2, smooth=True, tags="wave")
        # Frequency bins as vertical bars
        for i in range(8):
            bx = 20 + i * 32
            mag = abs(20 * math.sin(i * self._anim_angle * 0.3 + i))
            c.create_rectangle(bx, h - mag - 5, bx + 18, h - 5,
                                fill=ACCENT_BLUE, outline="", tags="wave")

        self._anim_angle += 0.05
        self._anim_id = self.after(40, self._animate)

    def destroy(self):
        if self._anim_id:
            self.after_cancel(self._anim_id)
        super().destroy()

    # ── FEATURE CARDS ────────────────────────────────────────────────────
    def _build_cards(self, f):
        cards_row = tk.Frame(f, bg=BG_DARK)
        cards_row.pack(fill="x", padx=30, pady=28)

        cards = [
            ("📡", "What is DFT?",      ACCENT_TEAL,
             "Converts a finite signal sequence into complex frequency components."
             " Backbone of all digital signal processing."),
            ("🧮", "Twiddle (W) Matrix", ACCENT_BLUE,
             "W_N^(nk) = e^(−j·2π·nk/N). This tool builds, colours, and annotates"
             " the full W matrix like the textbook."),
            ("📊", "4 Spectrum Plots",   ACCENT_PURP,
             "Magnitude, Phase, Real, and Imaginary spectra rendered as"
             " interactive stem plots after every run."),
            ("📂", "Flexible Input",     ACCENT_GOLD,
             "Type values manually or import CSV / TXT / Excel."
             " Perfect for EEG and biomedical signal workflows."),
        ]

        for i, (icon, title, color, desc) in enumerate(cards):
            card = tk.Frame(cards_row, bg=BG_CARD, padx=18, pady=18)
            card.grid(row=0, column=i, padx=8, sticky="nsew")
            cards_row.columnconfigure(i, weight=1)

            # Hover effect
            def _enter(e, c=card, col=color):
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

    # ── LIVE MINI DFT DEMO ───────────────────────────────────────────────
    def _build_live_demo(self, f):
        demo = tk.Frame(f, bg=BG_CARD, padx=28, pady=22)
        demo.pack(fill="x", padx=30, pady=(0, 8))

        tk.Label(demo, text="⚡  Live DFT Preview",
                 font=("Segoe UI", 13, "bold"),
                 bg=BG_CARD, fg=ACCENT_GOLD).pack(anchor="w")
        tk.Label(demo, text="Type comma-separated values below and see the magnitude spectrum update instantly.",
                 font=FONT_SMALL, bg=BG_CARD, fg=TEXT_MUTED).pack(anchor="w", pady=(2, 10))

        row = tk.Frame(demo, bg=BG_CARD)
        row.pack(fill="x")

        self._demo_entry = tk.Entry(row, font=("Consolas", 11),
                                    bg=BG_CARD2, fg=ACCENT_TEAL,
                                    insertbackground=ACCENT_TEAL,
                                    relief="flat", bd=0)
        self._demo_entry.insert(0, "1, 2, 3, 4")
        self._demo_entry.pack(side="left", fill="x", expand=True,
                               ipady=8, ipadx=10)
        self._demo_entry.bind("<KeyRelease>", self._update_demo)

        self._demo_canvas = tk.Canvas(demo, height=90,
                                       bg=BG_CARD2, highlightthickness=0)
        self._demo_canvas.pack(fill="x", pady=(10, 0))
        self._update_demo()

    def _update_demo(self, _=None):
        raw = self._demo_entry.get()
        try:
            vals = [complex(v.strip()) for v in raw.split(",") if v.strip()]
            if not vals: return
            N  = len(vals)
            wn = cmath.exp(-2j * math.pi / N)
            X  = [sum(vals[n] * wn**(n*k) for n in range(N)) for k in range(N)]
            mags = [abs(v) for v in X]
            mx = max(mags) if max(mags) > 0 else 1
        except Exception:
            return

        c = self._demo_canvas
        c.delete("all")
        cw = c.winfo_width() or 600
        ch = 90
        bar_w = max(4, cw // (N + 1) - 4)
        gap   = cw / (N + 1)

        colors = [ACCENT_TEAL, ACCENT_BLUE, ACCENT_PURP, ACCENT_GOLD,
                  ACCENT_PINK, ACCENT_TEAL, ACCENT_BLUE, ACCENT_PURP]

        for k, mag in enumerate(mags):
            bh = int((mag / mx) * (ch - 20))
            bx = int(gap * (k + 1))
            col = colors[k % len(colors)]
            c.create_rectangle(bx - bar_w//2, ch - bh - 5,
                                bx + bar_w//2, ch - 5,
                                fill=col, outline="")
            c.create_text(bx, ch - bh - 14,
                          text=f"k={k}", fill=TEXT_MUTED,
                          font=("Segoe UI", 7))

    # ── FORMULA BLOCK ─────────────────────────────────────────────────────
    def _build_formula(self, f):
        eq = tk.Frame(f, bg=BG_CARD, padx=30, pady=22)
        eq.pack(fill="x", padx=30, pady=(0, 8))

        tk.Label(eq, text="Core DFT Formula", font=("Segoe UI", 13, "bold"),
                 bg=BG_CARD, fg=TEXT_WHITE).pack(anchor="w")
        tk.Frame(eq, bg=ACCENT_TEAL, height=2).pack(fill="x", pady=(4, 14))

        box = tk.Frame(eq, bg=BG_CARD2, padx=24, pady=18)
        box.pack(fill="x")

        formulas = [
            ("X[k]  =  Σ  x[n] · W_N^(n·k)",         ACCENT_TEAL, "Consolas", 15),
            ("W_N   =  e^(−j · 2π / N)",               ACCENT_BLUE, "Consolas", 12),
            ("|X[k]|  =  √( Re²{X[k]} + Im²{X[k]} )", ACCENT_PURP, "Consolas", 11),
            ("∠X[k]  =  arctan( Im{X[k]} / Re{X[k]} )", ACCENT_GOLD, "Consolas", 11),
        ]
        for text, color, font, size in formulas:
            tk.Label(box, text=text, font=(font, size, "bold"),
                     bg=BG_CARD2, fg=color).pack(anchor="w", pady=3)

    # ── HOW IT WORKS ──────────────────────────────────────────────────────
    def _build_steps(self, f):
        outer = tk.Frame(f, bg=BG_DARK)
        outer.pack(fill="x", padx=30, pady=(0, 36))

        tk.Label(outer, text="How This Tool Works",
                 font=("Segoe UI", 14, "bold"),
                 bg=BG_DARK, fg=TEXT_WHITE).pack(anchor="w", pady=(0, 14))

        steps = [
            ("01", ACCENT_TEAL,  "Enter Signal x[n]",
             "Type values like  1, 2, 3, 4  or import from CSV / TXT / Excel"),
            ("02", ACCENT_BLUE,  "Set DFT Size N",
             "Enter N or click Auto to match signal length. Zero-padding applied if N > signal."),
            ("03", ACCENT_PURP,  "W Matrix Built",
             "Twiddle matrix W_N^(n·k) assembled and rendered as a colour-mapped bracket matrix."),
            ("04", ACCENT_GOLD,  "X[k] Computed Step-by-Step",
             "Each X[k] expansion shown symbolically with actual twiddle values substituted."),
            ("05", ACCENT_PINK,  "Spectrum Visualized",
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
