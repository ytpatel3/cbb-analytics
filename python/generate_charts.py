"""
Generates three static visualizations (Viz 1–3) and one Altair visualization (Viz 4)

Requirements:
    pip install pandas numpy matplotlib seaborn altair
"""

import os
import json
import warnings

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import matplotlib.patheffects as pe

import seaborn as sns
import altair as alt

warnings.filterwarnings("ignore")

ROOT      = os.path.join(os.path.dirname(__file__), "..")
DATA_IN   = os.path.join(ROOT, "data", "cbb.csv")
DATA_OUT  = os.path.join(ROOT, "data", "cbb_clean.csv")
CHART_DIR = os.path.join(ROOT, "charts")
os.makedirs(CHART_DIR, exist_ok=True)

# Design constants from css/style.css)
BG      = "#0c1420"
CARD    = "#111d2e"
BORDER  = "#1e3050"
ACCENT  = "#d4890a"
TEXT    = "#dce3ee"
MUTED   = "#7a90aa"
GRID_C  = "#1e3050"

ROUND_ORDER = [
    "No Tournament", "R68", "R64", "R32", "S16", "E8", "F4", "2ND", "Champions"
]
ROUND_COLORS = {
    "No Tournament": "#2d3f55",
    "R68":           "#445e7a",
    "R64":           "#5b7ea0",
    "R32":           "#6096c4",
    "S16":           "#3cb87a",
    "E8":            "#d4890a",
    "F4":            "#e06b1a",
    "2ND":           "#c03a2b",
    "Champions":     "#f0c040",
}

CONF_COLORS = {
    "ACC": "#4a90d9",
    "B10": "#d94a4a",
    "B12": "#e08030",
    "SEC": "#4ab87a",
    "BE":  "#9b6fd4",
    "P12": "#d4c030",
    "A10": "#d47a4a",
}


def set_style() -> None:
    """Apply consistent dark matplotlib style."""
    plt.rcParams.update({
        "figure.facecolor":  BG,
        "axes.facecolor":    CARD,
        "axes.edgecolor":    BORDER,
        "axes.labelcolor":   TEXT,
        "axes.titlecolor":   TEXT,
        "axes.titlesize":    13,
        "axes.titleweight":  "bold",
        "axes.labelsize":    11,
        "xtick.color":       MUTED,
        "ytick.color":       MUTED,
        "xtick.labelsize":   10,
        "ytick.labelsize":   10,
        "grid.color":        GRID_C,
        "grid.linewidth":    0.6,
        "text.color":        TEXT,
        "font.family":       "DejaVu Sans",
        "figure.dpi":        150,
        "legend.facecolor":  CARD,
        "legend.edgecolor":  BORDER,
        "legend.labelcolor": TEXT,
        "legend.fontsize":   9,
    })


# Data loading and cleaning
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_IN)

    # Fill non-tournament teams
    df["POSTSEASON"] = df["POSTSEASON"].fillna("No Tournament")
    df["POSTSEASON"] = pd.Categorical(
        df["POSTSEASON"], categories=ROUND_ORDER, ordered=True
    )

    # Numeric types
    df["YEAR"] = df["YEAR"].astype(int)
    df["SEED"] = pd.to_numeric(df["SEED"], errors="coerce")

    # BARTHAG quintile tiers (used by Viz 5 / D3)
    df["BARTHAG_TIER"] = pd.qcut(
        df["BARTHAG"], q=5,
        labels=["Tier 1", "Tier 2", "Tier 3", "Tier 4", "Tier 5"]
    )
    df["ADJOE_TIER"] = pd.qcut(
        df["ADJOE"], q=5,
        labels=["Tier 1", "Tier 2", "Tier 3", "Tier 4", "Tier 5"]
    )
    # ADJDE: lower = better, so reverse the tier label assignment
    df["ADJDE_TIER"] = pd.qcut(
        df["ADJDE"], q=5,
        labels=["Tier 5", "Tier 4", "Tier 3", "Tier 2", "Tier 1"]
    )

    df.to_csv(DATA_OUT, index=False)
    print(f"  Cleaned data saved → {DATA_OUT}  ({df.shape[0]} rows, {df.shape[1]} cols)")
    return df


# VIZ 1 — Boxplot: BARTHAG distribution by major conference
def viz1_boxplot(df: pd.DataFrame) -> None:
    major_confs = ["ACC", "B10", "B12", "SEC", "BE", "P12", "A10"]
    cdf = df[df["CONF"].isin(major_confs)].copy()

    conf_order = (
        cdf.groupby("CONF")["BARTHAG"]
        .median()
        .sort_values(ascending=False)
        .index.tolist()
    )

    fig, ax = plt.subplots(figsize=(11, 6))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(CARD)

    box_data = [cdf.loc[cdf["CONF"] == c, "BARTHAG"].dropna().values for c in conf_order]

    bp = ax.boxplot(
        box_data,
        patch_artist=True,
        notch=False,
        widths=0.52,
        medianprops=dict(color=ACCENT, linewidth=2.5, zorder=5),
        whiskerprops=dict(color=MUTED, linewidth=1.2),
        capprops=dict(color=MUTED, linewidth=1.2),
        flierprops=dict(
            marker="o", markerfacecolor=ACCENT, markeredgewidth=0,
            markersize=3.5, alpha=0.45
        ),
        boxprops=dict(linewidth=1.2),
    )
    for patch, conf in zip(bp["boxes"], conf_order):
        patch.set_facecolor(CONF_COLORS.get(conf, "#4a5568"))
        patch.set_alpha(0.70)

    # Median value annotations
    for i, conf in enumerate(conf_order, start=1):
        med = cdf.loc[cdf["CONF"] == conf, "BARTHAG"].median()
        txt = ax.text(
            i, med + 0.006, f"{med:.3f}",
            ha="center", va="bottom",
            fontsize=8, color=ACCENT, fontweight="bold", zorder=6
        )

        txt.set_path_effects([
            pe.Stroke(linewidth=2.2, foreground="black"),
            pe.Normal()
        ])

    ax.set_xticks(range(1, len(conf_order) + 1))
    ax.set_xticklabels(conf_order, fontsize=11, color=TEXT)
    ax.set_xlabel("Athletic Conference", labelpad=8, color=TEXT)
    ax.set_ylabel("BARTHAG (Power Rating)", labelpad=8, color=TEXT)
    ax.set_title(
        "Power Rating Distribution Across Major Conferences (2013–2024)",
        pad=12
    )
    ax.yaxis.grid(True, linestyle="--", alpha=0.45)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_edgecolor(BORDER)

    # Conference legend
    patches = [
        mpatches.Patch(facecolor=CONF_COLORS.get(c, "#4a5568"), alpha=0.7,
                       edgecolor=BORDER, label=c)
        for c in conf_order
    ]
    ax.legend(
        handles=patches, ncol=7, loc="lower center",
        bbox_to_anchor=(0.5, -0.18), frameon=True,
        fontsize=9, title="Conference", title_fontsize=9
    )

    fig.tight_layout()
    out = os.path.join(CHART_DIR, "viz1_boxplot.png")
    fig.savefig(out, dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print(f"  Viz 1 saved → {out}")


# VIZ 2 — Radar: Champions vs. Runners-Up performance profiles
def viz2_radar(df: pd.DataFrame) -> None:
    METRICS      = ["EFG_O", "TOR", "ORB", "FTR", "ADJDE", "ADJOE"]
    LOWER_BETTER = {"TOR", "ADJDE"}
    LABELS       = [
        "EFG%\n(Off)", "Turnover\nRate*", "Off Reb\nRate",
        "Free Throw\nRate", "Def Eff*", "Adj Off\nEff"
    ]

    def scale_to_percentile(series_val, col):
        """Scale a raw value to [0,1] percentile across the full dataset."""
        pct = (series_val - df[col].min()) / (df[col].max() - df[col].min())
        return 1.0 - float(pct) if col in LOWER_BETTER else float(pct)

    def build_profiles(group_df):
        rows = []
        for _, row in group_df.iterrows():
            rows.append({m: scale_to_percentile(row[m], m) for m in METRICS})
        return pd.DataFrame(rows)

    champs  = df[df["POSTSEASON"] == "Champions"].copy()
    runners = df[df["POSTSEASON"] == "2ND"].copy()

    champ_prof  = build_profiles(champs)
    runner_prof = build_profiles(runners)

    N      = len(METRICS)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    angles += angles[:1]

    def close(vals):
        v = list(vals)
        return v + [v[0]]

    fig, axes = plt.subplots(1, 2, figsize=(14, 7), subplot_kw={"polar": True})
    fig.patch.set_facecolor(BG)

    datasets = [
        (champ_prof,  "#f0c040", "NCAA Champions",   axes[0]),
        (runner_prof, "#9ca3af", "Runner-Up Teams",  axes[1]),
    ]

    for profiles, color, title, ax in datasets:
        ax.set_facecolor(CARD)

        # Individual team polygons (faint)
        for _, row in profiles.iterrows():
            vals = close([row[m] for m in METRICS])
            ax.plot(angles, vals, color=color, linewidth=0.7, alpha=0.20)
            ax.fill(angles, vals, color=color, alpha=0.03)

        # Median polygon (bold)
        med_vals = close([profiles[m].median() for m in METRICS])
        ax.plot(angles, med_vals, color=color, linewidth=2.8)
        ax.fill(angles, med_vals, color=color, alpha=0.22)

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(LABELS, fontsize=9.5, color=TEXT)
        ax.set_yticks([0.25, 0.50, 0.75, 1.00])
        ax.set_yticklabels(
            ["25th", "50th", "75th", "100th"],
            fontsize=7.5, color=MUTED
        )
        ax.set_ylim(0, 1)
        ax.tick_params(colors=MUTED)
        ax.grid(color=GRID_C, linewidth=0.6)
        ax.spines["polar"].set_color(BORDER)
        ax.set_title(title, pad=20, color=TEXT, fontsize=13, fontweight="bold")
        ax.text(
            0.5, -0.09,
            f"n = {len(profiles)} team-seasons | bold = group median | faint lines = individual teams",
            ha="center", transform=ax.transAxes,
            fontsize=8, color=MUTED
        )

    fig.suptitle(
        "Performance Profiles: NCAA Champions vs. Runner-Up Teams\n"
        "Metrics expressed as dataset-wide percentiles  (* = inverted; higher always = better)",
        fontsize=12, color=TEXT, y=1.01, fontweight="bold"
    )
    fig.tight_layout()
    out = os.path.join(CHART_DIR, "viz2_radar.png")
    fig.savefig(out, dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print(f"  Viz 2 saved → {out}")


# VIZ 3 — Multi-faceted scatter: WAB vs. key offensive/efficiency attributes
def viz3_scatter_facet(df: pd.DataFrame) -> None:
    PANELS = [
        ("WAB", "ADJOE", "Adjusted Offensive Efficiency (ADJOE)"),
        ("WAB", "2P_O",  "Two-Point Field Goal % (2P_O)"),
        ("WAB", "3P_O",  "Three-Point Field Goal % (3P_O)"),
    ]

    # Simplified postseason color groups
    def color_group(ps):
        if str(ps) == "No Tournament": return "#2d3f55"
        if str(ps) in ("R68", "R64"):  return "#5b7ea0"
        if str(ps) in ("R32", "S16"):  return "#3cb87a"
        if str(ps) in ("E8", "F4"):    return "#d4890a"
        return "#f0c040"  # 2ND / Champions

    GROUP_LABELS  = ["No Tournament", "R68/R64", "R32/S16", "E8/F4", "2ND/Champions"]
    GROUP_COLORS  = ["#2d3f55", "#5b7ea0", "#3cb87a", "#d4890a", "#f0c040"]

    colors = df["POSTSEASON"].map(color_group)

    fig, axes = plt.subplots(1, 3, figsize=(17, 5.5))
    fig.patch.set_facecolor(BG)

    for ax, (x_col, y_col, y_label) in zip(axes, PANELS):
        ax.set_facecolor(CARD)
        ax.scatter(
            df[x_col], df[y_col],
            c=colors, s=13, alpha=0.55, linewidths=0, rasterized=True
        )

        # OLS trend line
        mask = df[[x_col, y_col]].notna().all(axis=1)
        m, b = np.polyfit(df.loc[mask, x_col], df.loc[mask, y_col], 1)
        xs = np.linspace(df[x_col].min(), df[x_col].max(), 300)
        ax.plot(xs, m * xs + b, color=ACCENT, linewidth=1.8,
                linestyle="--", alpha=0.9, label="OLS fit")

        r = df.loc[mask, [x_col, y_col]].corr().iloc[0, 1]
        ax.text(
            0.05, 0.95, f"r = {r:.3f}",
            transform=ax.transAxes, fontsize=9.5,
            color=ACCENT, va="top", fontweight="bold"
        )

        ax.set_xlabel("Wins Above Bubble (WAB)", labelpad=6, color=TEXT)
        ax.set_ylabel(y_label, labelpad=6, color=TEXT)
        ax.set_title(f"WAB vs. {y_col}", pad=9)
        ax.yaxis.grid(True, linestyle="--", alpha=0.35)
        ax.set_axisbelow(True)
        for spine in ax.spines.values():
            spine.set_edgecolor(BORDER)

    # Shared legend
    patches = [
        mpatches.Patch(facecolor=c, edgecolor=BORDER, label=g)
        for g, c in zip(GROUP_LABELS, GROUP_COLORS)
    ]
    fig.legend(
        handles=patches, loc="lower center", ncol=5,
        frameon=True, fontsize=9,
        title="Tournament Round Group", title_fontsize=9,
        bbox_to_anchor=(0.5, -0.06)
    )

    fig.suptitle(
        "Wins Above Bubble (WAB) vs. Key Offensive & Efficiency Metrics\n"
        "(All teams, 2013–2024 — colored by tournament outcome)",
        fontsize=13, color=TEXT, fontweight="bold", y=1.02
    )
    fig.tight_layout()
    out = os.path.join(CHART_DIR, "viz3_scatter_facet.png")
    fig.savefig(out, dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print(f"  Viz 3 saved → {out}")


# VIZ 4 — Altair (interactive): ADJOE vs. ADJDE, colored by postseason round
def viz4_altair(df: pd.DataFrame) -> None:
    cols = ["TEAM", "CONF", "YEAR", "ADJOE", "ADJDE", "BARTHAG",
            "POSTSEASON", "SEED", "W", "WAB"]
    plot_df = df[cols].copy()
    plot_df["POSTSEASON"] = plot_df["POSTSEASON"].astype(str)
    plot_df["YEAR"]       = plot_df["YEAR"].astype(str)
    plot_df["SEED"]       = plot_df["SEED"].fillna("N/A").astype(str)
    plot_df = plot_df.dropna(subset=["ADJOE", "ADJDE", "BARTHAG"])

    color_scale = alt.Scale(
        domain=ROUND_ORDER,
        range=[ROUND_COLORS[r] for r in ROUND_ORDER]
    )

    # Year dropdown — 'All' shows every season
    year_opts = ["All"] + sorted(plot_df["YEAR"].unique().tolist())
    year_bind = alt.binding_select(options=year_opts, name="Season: ")
    year_param = alt.param(name="year_sel", bind=year_bind, value="All")

    # Legend click for postseason filtering
    legend_sel = alt.selection_point(fields=["POSTSEASON"], bind="legend")

    base = (
        alt.Chart(plot_df)
        .transform_filter(
            "year_sel === 'All' || datum.YEAR === year_sel"
        )
    )

    scatter = (
        base.mark_circle(stroke=None)
        .encode(
            x=alt.X(
                "ADJOE:Q",
                scale=alt.Scale(zero=False),
                title="Adjusted Offensive Efficiency (ADJOE)",
            ),
            y=alt.Y(
                "ADJDE:Q",
                scale=alt.Scale(zero=False, reverse=True),
                title="Adjusted Defensive Efficiency (ADJDE)  ←  lower is better",
            ),
            color=alt.Color(
                "POSTSEASON:N",
                scale=color_scale,
                sort=ROUND_ORDER,
                legend=alt.Legend(
                    title="Tournament Round",
                    orient="right",
                    symbolSize=80,
                ),
            ),
            size=alt.Size(
                "BARTHAG:Q",
                scale=alt.Scale(range=[18, 200]),
                legend=alt.Legend(title="BARTHAG (power rating)", orient="right"),
            ),
            opacity=alt.condition(legend_sel, alt.value(0.78), alt.value(0.08)),
            tooltip=[
                alt.Tooltip("TEAM:N",       title="Team"),
                alt.Tooltip("CONF:N",       title="Conference"),
                alt.Tooltip("YEAR:O",       title="Season"),
                alt.Tooltip("ADJOE:Q",      title="Adj. Off. Efficiency", format=".1f"),
                alt.Tooltip("ADJDE:Q",      title="Adj. Def. Efficiency", format=".1f"),
                alt.Tooltip("BARTHAG:Q",    title="Power Rating",         format=".4f"),
                alt.Tooltip("WAB:Q",        title="Wins Above Bubble",    format=".1f"),
                alt.Tooltip("POSTSEASON:N", title="Tournament Round"),
                alt.Tooltip("SEED:N",       title="Seed"),
                alt.Tooltip("W:Q",          title="Wins"),
            ],
        )
        .add_params(year_param, legend_sel)
        .properties(width=720, height=500)
    )

    chart = scatter.configure(
        background="#0c1420",
        font="IBM Plex Sans, sans-serif",
    ).configure_view(
        stroke="#1e3050",
    ).configure_axis(
        gridColor="#1e3050",
        domainColor="#1e3050",
        tickColor="#1e3050",
        labelColor="#7a90aa",
        titleColor="#dce3ee",
        labelFontSize=11,
        titleFontSize=12,
    ).configure_legend(
        fillColor="#111d2e",
        strokeColor="#1e3050",
        labelColor="#dce3ee",
        titleColor="#dce3ee",
        labelFontSize=11,
        titleFontSize=11,
        padding=10,
    ).configure_title(
        color="#dce3ee",
    )

    out = os.path.join(CHART_DIR, "viz4_altair.json")
    chart.save(out)
    print(f"  Viz 4 saved → {out}")


if __name__ == "__main__":
    print("\n=== NCAA Basketball Analytics — Chart Generator ===\n")
    set_style()
    df = load_data()
    print(f"  Loaded {len(df)} rows\n")
    viz1_boxplot(df)
    # viz2_radar(df)
    # viz3_scatter_facet(df)
    # viz4_altair(df)
    print("\nDone. All assets written to charts/ and data/\n")
