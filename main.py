"""
main.py  —  Entry point for the DFT Visualizer Tool.
Run:  python main.py
"""

import sys
import os

# Make sure imports resolve from project root
sys.path.insert(0, os.path.dirname(__file__))

from ui.app import DFTApp

if __name__ == "__main__":
    app = DFTApp()
    app.mainloop()
