from __future__ import annotations

import os
import subprocess
import tempfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
from matplotlib.ticker import FuncFormatter
import numpy as np

# ── Paleta kolorów ──────────────────────────────────────────────────────────
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

# Ciemny motyw — tło i akcenty
BG_DARK   = "#12121E"
BG_PANEL  = "#1C1C2E"
BG_AXES   = "#22223A"
GRID_LINE = "#2E2E4A"
TEXT_MAIN = "#EAEAF0"
TEXT_DIM  = "#7878A0"
ACCENT    = "#6C63FF"

# ── Funkcja pomocnicza: styl globalny ────────────────────────────────────────
def _apply_base_style() -> None:
    """Ustawia globalne parametry stylu matplotlib dla spójnego wyglądu."""
    plt.rcParams.update({
        "font.family":          "DejaVu Sans",
        "font.size":            10,
        "axes.titlesize":       14,
        "axes.titleweight":     "bold",
        "axes.titlecolor":      TEXT_MAIN,
        "axes.labelcolor":      TEXT_DIM,
        "axes.facecolor":       BG_AXES,
        "axes.edgecolor":       GRID_LINE,
        "axes.grid":            True,
        "axes.axisbelow":       True,
        "grid.color":           GRID_LINE,
        "grid.linewidth":       0.6,
        "grid.linestyle":       "--",
        "xtick.color":          TEXT_DIM,
        "ytick.color":          TEXT_DIM,
        "xtick.labelsize":      9,
        "ytick.labelsize":      9,
        "figure.facecolor":     BG_DARK,
        "figure.dpi":           110,
        "savefig.facecolor":    BG_DARK,
        "legend.framealpha":    0.3,
        "legend.facecolor":     BG_PANEL,
        "legend.edgecolor":     GRID_LINE,
        "legend.labelcolor":    TEXT_MAIN,
        "legend.fontsize":      9,
    })


def _formatter_tco2(x, *_):
    """Formatuje oś Y: duże liczby jako k lub M."""
    if x >= 1_000_000:
        return f"{x/1_000_000:.1f}M"
    if x >= 1_000:
        return f"{x/1_000:.1f}k"
    return f"{x:.0f}"

def plot_companies_comparison(summaries: list[dict], year: int) -> None:
    """Stacked bar chart: porównanie emisji Scope 1+2 wszystkich spółek."""
    if not summaries:
        print("[!] Brak danych do wykresu.")
        return

    _apply_base_style()

    companies = [s["company"] for s in summaries]
    n = len(companies)

    cat_values = {
        "Stacjonarne":      np.array([float(s["scope1_stationary"]) for s in summaries]),
        "Mobilne":          np.array([float(s["scope1_mobile"])      for s in summaries]),
        "Niezorganizowane": np.array([float(s["scope1_fugitive"])    for s in summaries]),
        "Procesowe":        np.array([float(s["scope1_process"])     for s in summaries]),
        "Energia (S2)":     np.array([float(s["scope2_energy"])      for s in summaries]),
    }

    totals = sum(cat_values.values())
    avg_total = totals.mean()

    x      = np.arange(n)
    width  = 0.55

    fig = plt.figure(figsize=(max(12, n * 2.0 + 4), 8))
    gs  = gridspec.GridSpec(
        1, 2, width_ratios=[max(3, n * 0.7), 1.4],
        wspace=0.05, left=0.07, right=0.97, top=0.88, bottom=0.14,
    )
    ax   = fig.add_subplot(gs[0])
    ax_r = fig.add_subplot(gs[1])
    bottoms = np.zeros(n)
    for label, color in zip(CATEGORY_LABELS, CATEGORY_COLORS):
        vals = cat_values[label]
        bars = ax.bar(
            x, vals, width=width,
            bottom=bottoms, color=color,
            edgecolor=BG_DARK, linewidth=0.5,
            label=label, zorder=3,
        )

        for i, (bar, v) in enumerate(zip(bars, vals)):
            if totals[i] > 0 and v / totals[i] > 0.06:
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    bottoms[i] + v / 2,
                    f"{v:.0f}",
                    ha="center", va="center",
                    fontsize=7, color="white",
                    fontweight="bold", zorder=4,
                )
        bottoms += vals

    # Etykiety sum na górze słupka
    for i, (xi, total) in enumerate(zip(x, totals)):
        if total > 0:
            ax.text(
                xi, total + totals.max() * 0.015,
                f"{total:.1f}",
                ha="center", va="bottom",
                fontsize=8.5, color=TEXT_MAIN,
                fontweight="bold", zorder=5,
            )

    ax.axhline(
        avg_total, color=ACCENT, linewidth=1.5,
        linestyle=":", zorder=5, alpha=0.85,
    )
    ax.text(
        n - 0.5, avg_total * 1.02,
        f"śr. {avg_total:.1f}",
        color=ACCENT, fontsize=8, va="bottom", ha="right", zorder=5,
    )

    ax.set_xticks(x)
    ax.set_xticklabels(
        [_shorten(c, 18) for c in companies],
        rotation=20, ha="right", fontsize=8.5, color=TEXT_MAIN,
    )
    ax.set_xlim(-0.55, n - 0.45)
    ax.set_ylabel("tCO₂e", color=TEXT_DIM, fontsize=11)
    ax.yaxis.set_major_formatter(FuncFormatter(_formatter_tco2))

    ax.set_title(
        f"Emisje Scope 1 + Scope 2 — {year}",
        pad=14, loc="left",
    )
    fig.text(
        0.07, 0.93,
        "Porównanie spółek | dane w tCO₂e",
        color=TEXT_DIM, fontsize=9,
    )

    # Legenda pod wykresem (lewa strona)
    ax.legend(
        handles=[mpatches.Patch(color=c, label=l)
                 for c, l in zip(CATEGORY_COLORS, CATEGORY_LABELS)],
        loc="upper left", ncol=3,
        framealpha=0.25,
    )

    # Panel rankingowy (prawa strona)
    ax_r.set_facecolor(BG_PANEL)
    ax_r.set_xlim(0, 1)
    ax_r.set_ylim(0, n + 0.5)
    ax_r.axis("off")

    ranked = sorted(zip(companies, totals), key=lambda t: t[1], reverse=True)
    ax_r.text(
        0.5, n + 0.3, "Ranking emisji",
        ha="center", fontsize=10, fontweight="bold",
        color=TEXT_MAIN,
    )
    ax_r.text(
        0.5, n + 0.05, "(łącznie tCO₂e)",
        ha="center", fontsize=8, color=TEXT_DIM,
    )

    max_val = ranked[0][1] if ranked else 1
    for rank, (comp, val) in enumerate(ranked):
        y_pos = n - rank - 0.2
        bar_len = val / max_val * 0.8 if max_val > 0 else 0
        # Pasek tła
        ax_r.barh(y_pos, 0.82, left=0.09, height=0.5,
                  color=BG_AXES, zorder=1)
        # Pasek wartości
        color = CATEGORY_COLORS[0] if rank == 0 else (
            CATEGORY_COLORS[2] if rank == len(ranked) - 1 else "#4A4A70"
        )
        ax_r.barh(y_pos, bar_len * 0.82, left=0.09, height=0.5,
                  color=color, alpha=0.8, zorder=2)
        ax_r.text(
            0.09, y_pos,
            f"#{rank+1}  {_shorten(comp, 16)}",
            va="center", fontsize=8, color=TEXT_MAIN, zorder=3,
        )
        ax_r.text(
            0.91, y_pos,
            f"{val:.0f}",
            va="center", ha="right", fontsize=8,
            color=TEXT_MAIN, fontweight="bold", zorder=3,
        )

    _save_and_open(fig, "emission_chart_")

# Donut chart
def plot_pie_chart(summary: dict, year: int) -> None:
    """Nowoczesny donut chart z panelem legendy i łączną emisją w środku."""
    categories = [
        ("Stacjonarne",      float(summary["scope1_stationary"]), "#E07B39"),
        ("Mobilne",          float(summary["scope1_mobile"]),     "#4A90D9"),
        ("Niezorganizowane", float(summary["scope1_fugitive"]),   "#7BC67E"),
        ("Procesowe",        float(summary["scope1_process"]),    "#C05780"),
        ("Energia (S2)",     float(summary["scope2_energy"]),     "#F5C542"),
    ]

    active = [(l, v, c) for l, v, c in categories if v > 0]
    if not active:
        print("[!] Brak danych do wykresu kołowego.")
        return

    _apply_base_style()

    labels, sizes, colors = zip(*active)
    total = sum(sizes)

    fig = plt.figure(figsize=(11, 7))
    gs  = gridspec.GridSpec(
        1, 2, width_ratios=[1.1, 1],
        wspace=0.04, left=0.03, right=0.97, top=0.88, bottom=0.06,
    )
    ax      = fig.add_subplot(gs[0])
    ax_leg  = fig.add_subplot(gs[1])

    # Donut chart
    wedge_props = {
        "edgecolor": BG_DARK,
        "linewidth": 3,
    }
    wedges, _ = ax.pie(
        sizes,
        colors=colors,
        startangle=90,
        counterclock=False,
        wedgeprops=wedge_props,
        pctdistance=0.82,
    )

    # Wyróżnij największy segment
    max_idx = sizes.index(max(sizes))
    wedges[max_idx].set_radius(1.08)
    wedges[max_idx].set_linewidth(4)

    # Biały krąg wewnętrzny — efekt donut
    centre_circle = plt.Circle((0, 0), 0.62, fc=BG_PANEL, zorder=10)
    ax.add_patch(centre_circle)
    ax.text(0, 0.12, f"{total:.1f}", ha="center", va="center",
            fontsize=22, fontweight="bold", color=TEXT_MAIN, zorder=11)
    ax.text(0, -0.15, "tCO₂e", ha="center", va="center",
            fontsize=11, color=TEXT_DIM, zorder=11)
    ax.text(0, -0.36, "łącznie", ha="center", va="center",
            fontsize=9, color=TEXT_DIM, zorder=11)

    ax.set_aspect("equal")

    company = summary.get("company", "")
    ax.set_title(
        f"Struktura emisji — {_shorten(company, 28)} ({year})",
        pad=14,
    )

    ax_leg.set_facecolor(BG_PANEL)
    ax_leg.set_xlim(0, 1)
    ax_leg.set_ylim(-0.5, len(active) + 0.5)
    ax_leg.axis("off")

    ax_leg.text(0.5, len(active) + 0.2, "Szczegółowe dane",
                ha="center", fontsize=10, fontweight="bold", color=TEXT_MAIN)

    sorted_cats = sorted(zip(labels, sizes, colors), key=lambda t: t[1], reverse=True)

    for i, (label, val, color) in enumerate(sorted_cats):
        y = len(active) - 1 - i
        pct = val / total * 100 if total > 0 else 0
        ax_leg.barh(y, pct / 100 * 0.72, left=0.06, height=0.55,
                    color=color, alpha=0.85, zorder=2)
        ax_leg.add_patch(mpatches.FancyBboxPatch(
            (0.06, y - 0.27), 0.04, 0.54,
            boxstyle="round,pad=0.01",
            fc=color, ec="none", zorder=3,
        ))
        ax_leg.text(0.13, y + 0.1, label,
                    va="center", fontsize=9, color=TEXT_MAIN, fontweight="bold", zorder=4)
        ax_leg.text(0.13, y - 0.18,
                    f"{val:.2f} tCO₂e  ({pct:.1f}%)",
                    va="center", fontsize=8.5, color=TEXT_DIM, zorder=4)

    scope1 = sum(v for l, v, _ in active if "S2" not in l)
    scope2 = sum(v for l, v, _ in active if "S2" in l)
    ax_leg.axhline(-0.2, color=GRID_LINE, linewidth=0.8)
    ax_leg.text(0.06, -0.38, f"Scope 1: {scope1:.2f} tCO₂e",
                fontsize=9, color="#E07B39", fontweight="bold")
    ax_leg.text(0.06, -0.62, f"Scope 2: {scope2:.2f} tCO₂e",
                fontsize=9, color="#F5C542", fontweight="bold")

    _save_and_open(fig, "emission_pie_")

def plot_trend_chart(trends: list[dict], company: str) -> None:
    """Area chart z trendami emisji: Scope 1, Scope 2, łącznie + zmiany r/r."""
    if not trends:
        print("[!] Brak danych do wykresu trendów.")
        return

    _apply_base_style()

    years  = [t["year"] for t in trends]
    scope1 = np.array([float(t["scope1_total"])  for t in trends])
    scope2 = np.array([float(t["scope2_energy"]) for t in trends])
    totals = np.array([float(t["total"])         for t in trends])

    fig = plt.figure(figsize=(max(10, len(years) * 1.8), 8))
    gs  = gridspec.GridSpec(
        2, 1, height_ratios=[3, 1],
        hspace=0.08, left=0.09, right=0.97, top=0.82, bottom=0.09,
    )
    ax_main  = fig.add_subplot(gs[0])
    ax_delta = fig.add_subplot(gs[1], sharex=ax_main)

    x = np.array(years, dtype=float)
    ax_main.fill_between(x, 0, scope1, alpha=0.30, color="#E07B39", zorder=2)
    ax_main.fill_between(x, 0, scope2, alpha=0.22, color="#F5C542", zorder=2)
    ax_main.plot(x, scope2, "s--", color="#F5C542", label="Scope 2",
                 linewidth=1.8, markersize=6, zorder=4)
    ax_main.plot(x, scope1, "o-", color="#E07B39", label="Scope 1",
                 linewidth=2.2, markersize=7, zorder=4)
    ax_main.plot(x, totals, "D-", color=TEXT_MAIN, label="Łącznie (S1+S2)",
                 linewidth=2.8, markersize=8, zorder=5)

    if len(totals) > 1:
        i_max = int(np.argmax(totals))
        i_min = int(np.argmin(totals))
    else:
        i_max = i_min = 0

    for i, (xi, yi) in enumerate(zip(x, totals)):
        # Przy MAX i MIN pomijamy zwykłą etykietę (zastąpi ją adnotacja)
        if len(totals) > 1 and i in (i_max, i_min):
            continue
        ax_main.annotate(
            f"{yi:.1f}",
            (xi, yi),
            textcoords="offset points", xytext=(0, 10),
            ha="center", fontsize=8, color=TEXT_MAIN, fontweight="bold",
        )

    if len(totals) > 1:
        n_pts = len(x)
        for idx, marker, color, tag in [
            (i_max, "▲", "#FF6B6B", "MAX"),
            (i_min, "▼", "#6BFFB8", "MIN"),
        ]:
            # Dla punktów po lewej połowie → adnotacja w prawo; dla prawych → w lewo
            is_left = idx < n_pts / 2
            x_off   = 38 if is_left else -38
            ha      = "left" if is_left else "right"
            ax_main.annotate(
                f"{marker} {tag}: {totals[idx]:.1f}",
                xy=(x[idx], totals[idx]),
                xytext=(x_off, 18), textcoords="offset points",
                ha=ha, va="center",
                fontsize=8, color=color, fontweight="bold",
                arrowprops=dict(arrowstyle="-", color=color, lw=1, alpha=0.6),
            )

    ax_main.yaxis.set_major_formatter(FuncFormatter(_formatter_tco2))
    ax_main.set_ylabel("tCO₂e", fontsize=11)

    # Tytuł + podtytuł w jednym (unikamy nakładania fig.text na ax.title)
    ax_main.set_title(
        f"Trendy emisji — {_shorten(company, 35)}\n"
        + r"$\mathdefault{Scope\ 1\ +\ Scope\ 2\ |\ dane\ w\ tCO_2e}$",
        pad=12, loc="left", linespacing=1.5,
    )

    trend_dir = totals[-1] - totals[0] if len(totals) > 1 else 0
    legend_loc = "lower left" if trend_dir < 0 else "upper right"
    ax_main.legend(loc=legend_loc, framealpha=0.35)

    plt.setp(ax_main.get_xticklabels(), visible=False)

    # ── Panel zmian r/r (dolny) ──
    ax_delta.set_facecolor(BG_AXES)

    if len(totals) > 1:
        deltas     = np.diff(totals)
        delta_pct  = deltas / totals[:-1] * 100
        x_delta    = x[1:]

        bar_colors = ["#6BFFB8" if d <= 0 else "#FF6B6B" for d in deltas]
        bars = ax_delta.bar(
            x_delta, delta_pct, color=bar_colors,
            width=0.55, edgecolor=BG_DARK, linewidth=0.5, zorder=3,
        )
        ax_delta.axhline(0, color=TEXT_DIM, linewidth=0.8, zorder=4)

        for bar, dp in zip(bars, delta_pct):
            y_off = 1 if dp >= 0 else -3
            ax_delta.text(
                bar.get_x() + bar.get_width() / 2,
                dp + y_off,
                f"{dp:+.1f}%",
                ha="center", va="bottom" if dp >= 0 else "top",
                fontsize=8, color=TEXT_MAIN, fontweight="bold",
            )

    ax_delta.set_ylabel("Δ r/r %", fontsize=9)
    ax_delta.set_xticks(x)
    ax_delta.set_xticklabels([str(y) for y in years], color=TEXT_MAIN, fontsize=9)
    ax_delta.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:+.0f}%"))

    _save_and_open(fig, "emission_trend_")

def _save_and_open(fig: plt.Figure, prefix: str) -> None:
    """Zapisuje wykres do pliku tymczasowego i otwiera go."""
    tmp = tempfile.NamedTemporaryFile(suffix=".png", prefix=prefix, delete=False)
    tmp.close()
    fig.savefig(tmp.name, dpi=140, bbox_inches="tight")
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
            subprocess.Popen(
                [opener, path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
    except Exception as e:
        print(f"  [!] Nie można otworzyć pliku automatycznie: {e}")
        print(f"  Otwórz ręcznie: {path}")


def _cmd_exists(cmd: str) -> bool:
    from shutil import which
    return which(cmd) is not None


def _shorten(name: str, max_len: int = 20) -> str:
    """Skraca długą nazwę firmy na etykiecie osi X."""
    return name if len(name) <= max_len else name[:max_len - 1] + "…"
