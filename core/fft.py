"""
core/fft.py
FFT via NumPy — fast path for large N.
"""

import numpy as np


def compute_fft(x: list) -> list[complex]:
    """Return the N-point FFT of x using NumPy."""
    return list(np.fft.fft(x))
