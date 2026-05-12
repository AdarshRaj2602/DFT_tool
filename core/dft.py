# core/dft.py Pure DFT computation — no UI dependencies.

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


def compute_idft(X: list[complex], N: int) -> list[complex]:
    """
    Compute the N-point Inverse DFT.
    x[n] = (1/N) * Σ X[k] · W_N^(-nk),   n = 0..N-1
    Returns reconstructed time-domain signal x[n].
    """
    if len(X) < N:
        X = list(X) + [0 + 0j] * (N - len(X))
    else:
        X = list(X[:N])

    W_N = cmath.exp(-2j * math.pi / N)   # same twiddle factor
    x = []
    for n in range(N):
        val = sum(X[k] * (W_N ** (-(n * k))) for k in range(N))
        x.append(val / N)
    return x


def build_idft_w_matrix(N: int) -> list[list[complex]]:
    """
    Build the N×N inverse twiddle matrix.
    W_inv[n][k] = (1/N) * e^(+j·2π·n·k / N)
    """
    W_N = cmath.exp(-2j * math.pi / N)
    return [[(W_N ** (-(n * k))) / N for k in range(N)] for n in range(N)]
