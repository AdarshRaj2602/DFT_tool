# 🔢 DFT Visualizer — Signal Processing Lab

> An interactive desktop tool for computing and visualizing the **Discrete Fourier Transform** step-by-step, built with Python + Tkinter.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Tkinter](https://img.shields.io/badge/Tkinter-GUI-informational?style=for-the-badge)
![NumPy](https://img.shields.io/badge/NumPy-Scientific-013243?style=for-the-badge&logo=numpy&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-Plots-11557c?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge)

---

## ✨ Features

- 🧮 **Bracket-style W matrix** — textbook layout with magnitude & phase heatmaps
- 📐 **Step-by-step DFT expansion** — every X[k] derived symbolically on screen
- 📊 **4-panel spectrum plots** — Magnitude, Phase, Real, Imaginary
- 📂 **Flexible input** — CSV / TXT / Excel import + PNG / PDF export
- ⚡ **Live DFT preview** — bar chart updates as you type on the Home page
- 🔢 **Zero-padding support** — for N > signal length

---

## 🚀 Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/AdarshRaj2602/DFT_tool.git
cd DFT_tool

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
python main.py
```

---

## 🗂️ Project Structure

DFT_tool/
├── assets/
│   ├── icons/                  # App icons
│   └── themes/
│       └── theme.py            # Colours, fonts, design tokens
├── core/
│   ├── dft.py                  # Pure DFT engine — build_w_matrix, compute_dft
│   └── fft.py                  # NumPy FFT wrapper
├── ui/
│   ├── app.py                  # Main window, sidebar, navigation router
│   ├── home_page.py            # Animated home + live DFT preview
│   ├── input_panel.py          # Signal entry + controls
│   ├── matrix_panel.py         # W-matrix bracket display + heatmaps
│   ├── output_panel.py         # Step-by-step equations + results table
│   ├── plot_panel.py           # Spectrum plots
│   └── about_page.py           # Technical overview
├── utils/
│   └── validators.py           # Signal parsing, file loading
├── main.py                     # Entry point
├── requirements.txt
└── README.md

---

## 🧮 The DFT Formula

$$X[k] = \sum_{n=0}^{N-1} x[n] \cdot W_N^{nk} \qquad W_N = e^{-j2\pi/N}$$

| Term | Description |
|------|-------------|
| `x[n]` | Input signal samples |
| `N` | DFT size |
| `W_N` | Twiddle factor |
| `X[k]` | Frequency domain output |

---

## 📦 Dependencies

```txt
numpy
pandas
matplotlib
openpyxl
```

Install all at once:
```bash
pip install -r requirements.txt
```

---

## 🛠️ How It Works

| Step | Action |
|------|--------|
| 1️⃣ | Enter signal `x[n]` manually or import from file |
| 2️⃣ | Set DFT size `N` (or click Auto) |
| 3️⃣ | W matrix is built and displayed in bracket notation |
| 4️⃣ | Each `X[k]` expansion shown symbolically with twiddle values |
| 5️⃣ | Magnitude, Phase, Real & Imaginary spectra plotted |

---

## 👨‍💻 Developer

**Adarsh Raj Verma**
M.Tech — Machine Intelligence & Automation
NIT Jalandhar

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/adarsh-raj-verma-99b71436a/)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/AdarshRaj2602)

---

⭐ **If you found this useful, give it a star!**
