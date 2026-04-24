"""
ui/app.py
Main application window — sidebar + content router.
"""

import tkinter as tk
from tkinter import ttk

from assets.themes.theme import *
from ui.input_panel  import InputPanel
from ui.matrix_panel import MatrixPanel
from ui.output_panel import OutputPanel
from ui.plot_panel   import PlotPanel


class DFTApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DFT Visualizer — Signal Processing Lab")
        self.geometry("1340x820")
        self.minsize(1100, 700)
        self.configure(bg=BG_DARK)
        self.resizable(True, True)

        # Shared state (filled by InputPanel, read by matrix/output/plot)
        self.signal_data  = []
        self.dft_results  = []
        self.w_matrix     = []
        self.dft_N        = 4

        self._build_sidebar()
        self._build_content()
        self._nav("home")

    # ── SIDEBAR ──────────────────────────────────────────────────────────
    def _build_sidebar(self):
        self.sidebar = tk.Frame(self, bg=BG_CARD, width=230)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo
        logo = tk.Frame(self.sidebar, bg=BG_CARD, pady=24)
        logo.pack(fill="x")
        tk.Label(logo, text="◈", font=("Segoe UI", 32), bg=BG_CARD,
                 fg=ACCENT_TEAL).pack()
        tk.Label(logo, text="DFT TOOL", font=("Segoe UI", 15, "bold"),
                 bg=BG_CARD, fg=TEXT_WHITE).pack()
        tk.Label(logo, text="Signal Processing Lab", font=FONT_SMALL,
                 bg=BG_CARD, fg=TEXT_MUTED).pack()

        tk.Frame(self.sidebar, bg=BORDER, height=1).pack(fill="x", padx=16, pady=6)

        # Nav items
        self.nav_btns = {}
        items = [
            ("home",   "⌂", "Home"),
            ("solver", "⚙", "DFT Solver"),
            ("about",  "ℹ", "About"),
        ]
        for key, icon, label in items:
            btn = self._nav_button(key, icon, label)
            self.nav_btns[key] = btn

        tk.Frame(self.sidebar, bg=BORDER, height=1).pack(fill="x", padx=16, pady=6)

        # Version tag at bottom
        tk.Label(self.sidebar, text="v1.0  ·  NIT Jalandhar",
                 font=FONT_SMALL, bg=BG_CARD,
                 fg=TEXT_MUTED).pack(side="bottom", pady=16)

    def _nav_button(self, key, icon, label):
        frame = tk.Frame(self.sidebar, bg=BG_CARD, cursor="hand2")
        frame.pack(fill="x", padx=10, pady=2)

        icon_lbl = tk.Label(frame, text=icon, font=("Segoe UI", 14),
                            bg=BG_CARD, fg=TEXT_MUTED, width=3)
        icon_lbl.pack(side="left", padx=(10, 0), pady=10)
        text_lbl = tk.Label(frame, text=label, font=FONT_NAV,
                            bg=BG_CARD, fg=TEXT_MUTED, anchor="w")
        text_lbl.pack(side="left", fill="x", expand=True)

        def on_click(_=None):
            self._nav(key)
        def on_enter(_):
            if self._active != key:
                frame.configure(bg=BG_CARD2)
                icon_lbl.configure(bg=BG_CARD2)
                text_lbl.configure(bg=BG_CARD2)
        def on_leave(_):
            if self._active != key:
                frame.configure(bg=BG_CARD)
                icon_lbl.configure(bg=BG_CARD)
                text_lbl.configure(bg=BG_CARD)

        for w in (frame, icon_lbl, text_lbl):
            w.bind("<Button-1>", on_click)
            w.bind("<Enter>",    on_enter)
            w.bind("<Leave>",    on_leave)

        # Stash sub-widgets so _nav can recolour them
        frame._icon = icon_lbl
        frame._text = text_lbl
        return frame

    def _nav(self, key):
        self._active = key
        # Reset all buttons
        for k, frame in self.nav_btns.items():
            active = (k == key)
            bg = BG_CARD2 if active else BG_CARD
            fg = ACCENT_TEAL if active else TEXT_MUTED
            frame.configure(bg=bg)
            frame._icon.configure(bg=bg, fg=fg)
            frame._text.configure(bg=bg, fg=fg)

        for w in self.content.winfo_children():
            w.destroy()

        if key == "home":
            self._show_home()
        elif key == "solver":
            self._show_solver()
        elif key == "about":
            self._show_about()

    # ── CONTENT AREA ─────────────────────────────────────────────────────
    def _build_content(self):
        self.content = tk.Frame(self, bg=BG_DARK)
        self.content.pack(side="left", fill="both", expand=True)

    # ── HOME PAGE ─────────────────────────────────────────────────────────
    def _show_home(self):
        from ui.home_page import HomePage
        HomePage(self.content, nav_callback=self._nav).pack(fill="both", expand=True)

    # ── SOLVER PAGE ───────────────────────────────────────────────────────
    def _show_solver(self):
        """
        Layout:
          Left  →  InputPanel   (signal entry + controls)
          Right →  Notebook
                    Tab 1: MatrixPanel  (W-matrix heatmap)
                    Tab 2: OutputPanel  (step-by-step equations + results table)
                    Tab 3: PlotPanel    (spectrum plots)
        """
        pane = tk.PanedWindow(self.content, orient="horizontal",
                              bg=BG_DARK, sashrelief="flat",
                              sashwidth=6, sashpad=0)
        pane.pack(fill="both", expand=True)

        # ── LEFT: input controls ──────────────────────
        left = tk.Frame(pane, bg=BG_CARD, width=370)
        left.pack_propagate(False)
        pane.add(left, minsize=320)

        # ── RIGHT: tabbed results ─────────────────────
        right = tk.Frame(pane, bg=BG_DARK)
        pane.add(right, minsize=620)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("DFT.TNotebook",
                        background=BG_DARK, borderwidth=0)
        style.configure("DFT.TNotebook.Tab",
                        background=BG_CARD, foreground=TEXT_MUTED,
                        padding=[18, 8], font=("Segoe UI", 10))
        style.map("DFT.TNotebook.Tab",
                  background=[("selected", BG_CARD2)],
                  foreground=[("selected", ACCENT_TEAL)])

        nb = ttk.Notebook(right, style="DFT.TNotebook")
        nb.pack(fill="both", expand=True, padx=6, pady=6)

        # Tabs
        tab_matrix = tk.Frame(nb, bg=BG_DARK)
        tab_output = tk.Frame(nb, bg=BG_DARK)
        tab_plot   = tk.Frame(nb, bg=BG_DARK)

        nb.add(tab_matrix, text="🔢  W Matrix")
        nb.add(tab_output, text="📐  Equations & Results")
        nb.add(tab_plot,   text="📊  Spectrum Plots")

        # Instantiate panels
        self._matrix_panel = MatrixPanel(tab_matrix)
        self._matrix_panel.pack(fill="both", expand=True)

        self._output_panel = OutputPanel(tab_output)
        self._output_panel.pack(fill="both", expand=True)

        self._plot_panel = PlotPanel(tab_plot)
        self._plot_panel.pack(fill="both", expand=True)

        def on_result(signal, X, W_mat, N):
            self.signal_data = signal
            self.dft_results = X
            self.w_matrix    = W_mat
            self.dft_N       = N
            self._matrix_panel.render(W_mat, N)
            self._output_panel.render(signal, X, W_mat, N)
            self._plot_panel.render(signal, X, N)
            nb.select(tab_matrix)   # jump to matrix tab first

        InputPanel(left, on_result_callback=on_result).pack(
            fill="both", expand=True)

    # ── ABOUT PAGE ────────────────────────────────────────────────────────
    def _show_about(self):
        from ui.about_page import AboutPage
        AboutPage(self.content).pack(fill="both", expand=True)
