"""
core/dft.py
Pure DFT computation — no UI dependencies.
"""

import cmath
import math


def build_w_matrix(N: int) -> list[list[complex]]:
    """
    Build the N×N twiddle-factor (W) matrix.
    W_mat[k][n] = e^(-j·2π·n·k / N)
    """
    W_N = cmath.exp(-2j * math.pi / N)
    return [[W_N ** (n * k) for n in range(N)] for k in range(N)]


def compute_dft(x: list[complex], N: int) -> tuple[list[complex], list[list[complex]]]:
    """
    Compute the N-point DFT of signal x (zero-padded / truncated to N).
    Returns (X, W_mat):
        X     — list of N complex DFT coefficients
        W_mat — the N×N twiddle matrix used
    """
    # Pad or truncate
    if len(x) < N:
        x = list(x) + [0 + 0j] * (N - len(x))
    else:
        x = list(x[:N])

    W_mat = build_w_matrix(N)
    X = [sum(x[n] * W_mat[k][n] for n in range(N)) for k in range(N)]
    return X, W_mat
