"""
utils/validators.py
Signal parsing helpers — CSV / TXT / Excel / manual entry.
"""

import pandas as pd


def parse_signal(raw: str) -> list[complex]:
    """Parse a comma-separated string into a list of complex numbers."""
    tokens = [t.strip() for t in raw.replace("\n", ",").split(",") if t.strip()]
    if not tokens:
        raise ValueError("No signal values found.")
    result = []
    for t in tokens:
        try:
            result.append(complex(t))
        except ValueError:
            raise ValueError(f"Cannot parse '{t}' as a number.")
    return result


def load_signal_file(path: str) -> list[float]:
    """Load signal samples from CSV, TXT, or Excel file."""
    if path.endswith((".xlsx", ".xls")):
        df = pd.read_excel(path, header=None)
    elif path.endswith(".csv"):
        df = pd.read_csv(path, header=None)
    else:  # .txt or other text
        with open(path) as fp:
            raw = fp.read()
        tokens = [v.strip() for v in raw.replace("\n", ",").split(",") if v.strip()]
        return [float(v) for v in tokens]

    vals = df.values.flatten().tolist()
    return [float(v) for v in vals if str(v).strip() not in ("", "nan")]
