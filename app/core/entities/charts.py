from __future__ import annotations

import os
import subprocess
import tempfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

CATEGORY_LABELS = [
    "Stacjonarne",
    "Mobilne",
    "Niezorganizowane",
    "Procesowe",
    "Energia (S2)",
]

CATEGORY_COLORS = [
    "#E07B39",  # pomarańczowy  — spalanie stacjonarne
    "#4A90D9",  # niebieski     — spalanie mobilne
    "#7BC67E",  # zielony       — emisje niezorganizowane
    "#C05780",  # różowy        — emisje procesowe
    "#F5C542",  # żółty         — zużycie energii (Scope 2)
]

def plot_companies_comparison(summaries: list[dict], year: int) -> None:

    if not summaries:
        print("[!] Brak danych do wykresu.")
        return

    companies = [s["company"] for s in summaries]
    n = len(companies)

    values = {
        "Stacjonarne":      [float(s["scope1_stationary"]) for s in summaries],
        "Mobilne":          [float(s["scope1_mobile"])      for s in summaries],
        "Niezorganizowane": [float(s["scope1_fugitive"])    for s in summaries],
        "Procesowe":        [float(s["scope1_process"])     for s in summaries],
        "Energia (S2)":     [float(s["scope2_energy"])      for s in summaries],
    }

    x = np.arange(n)
    bar_width = 0.15
    offsets = np.array([-2, -1, 0, 1, 2]) * bar_width

    fig, ax = plt.subplots(figsize=(max(10, n * 2.2), 7))
    fig.patch.set_facecolor("#1E1E2E")
    ax.set_facecolor("#2A2A3E")

    for label, color, offset in zip(CATEGORY_LABELS, CATEGORY_COLORS, offsets):
        vals = values[label]
        max_val = max(vals) if any(v > 0 for v in vals) else 1.0
        bars = ax.bar(
            x + offset,
            vals,
            width=bar_width,
            color=color,
            alpha=0.92,
            edgecolor="#1E1E2E",
            linewidth=0.6,
            label=label,
            zorder=3,
        )
        for bar in bars:
            h = bar.get_height()
            if h > 0:
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    h + max_val * 0.012,
                    f"{h:.2f}",
                    ha="center",
                    va="bottom",
                    fontsize=7,
                    color="#CCCCCC",
                    rotation=45,
                    zorder=4,
                )

    ax.set_xticks(x)
    ax.set_xticklabels(
        [_shorten(c) for c in companies],
        color="#EEEEEE",
        fontsize=9,
        rotation=15,
        ha="right",
    )
    ax.tick_params(axis="y", colors="#AAAAAA", labelsize=9)
    ax.tick_params(axis="x", colors="#555555")

    ax.set_ylabel("tCO₂e", color="#CCCCCC", fontsize=11)
    ax.set_title(
        f"Porównanie emisji Scope 1 + Scope 2 — {year}",
        color="#FFFFFF",
        fontsize=14,
        fontweight="bold",
        pad=18,
    )

    ax.yaxis.grid(True, color="#444466", linewidth=0.5, linestyle="--", zorder=0)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_edgecolor("#444466")

    ax.legend(
        handles=[
            mpatches.Patch(color=c, label=l)
            for c, l in zip(CATEGORY_COLORS, CATEGORY_LABELS)
        ],
        loc="upper right",
        framealpha=0.25,
        facecolor="#2A2A3E",
        edgecolor="#666688",
        labelcolor="#EEEEEE",
        fontsize=9,
    )

    plt.tight_layout()

    tmp = tempfile.NamedTemporaryFile(
        suffix=".png", prefix="emission_chart_", delete=False
    )
    tmp.close()
    plt.savefig(tmp.name, dpi=130, bbox_inches="tight")
    plt.close(fig)

    print(f"  Wykres zapisany: {tmp.name}")
    _open_file(tmp.name)


def _open_file(path: str) -> None:
    """Otwiera plik domyślną aplikacją systemu."""
    try:
        if os.name == "nt":
            os.startfile(path)
        else:
            opener = "xdg-open" if _cmd_exists("xdg-open") else "open"
            subprocess.Popen([opener, path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"  [!] Nie można otworzyć pliku automatycznie: {e}")
        print(f"  Otwórz ręcznie: {path}")


def _cmd_exists(cmd: str) -> bool:
    from shutil import which
    return which(cmd) is not None


def _shorten(name: str, max_len: int = 20) -> str:
    """Skraca długą nazwę firmy na etykiecie osi X."""
    return name if len(name) <= max_len else name[:max_len - 1] + "…"
