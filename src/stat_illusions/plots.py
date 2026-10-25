"""Plotly figures for the interactive experiments."""

from __future__ import annotations

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .simulations import (
    BaseRateResult,
    CoverageResult,
    MultipleTestingResult,
    RegressionResult,
    SimpsonResult,
)

INK = "#1F2937"
MUTED = "#6B7280"
GRID = "#E7E1D6"
PAPER = "rgba(0,0,0,0)"
CORAL = "#D65A3A"
CORAL_INK = "#A8432D"
TEAL = "#2A9D8F"
GOLD = "#E9C46A"
GOLD_INK = "#8A6518"
BLUE = "#457B9D"
PURPLE = "#8E7DBE"
PURPLE_INK = "#5E4B8B"
SAND = "#D9D2C3"

# Colour-blind-friendly outcome colours for the base-rate grid.
TP_BLUE = "#0072B2"
FP_VERMILLION = "#D55E00"
TN_GRAY = "#CFC8B8"
FN_PINK = "#CC79A7"

FONT = (
    '"Noto Sans SC", "Source Han Sans SC", "PingFang SC", '
    '"Microsoft YaHei", "Segoe UI", sans-serif'
)


def _style(
    fig: go.Figure,
    height: int = 440,
    *,
    legend: bool = True,
    margin_left: int = 56,
) -> go.Figure:
    fig.update_layout(
        template=None,
        height=height,
        paper_bgcolor=PAPER,
        plot_bgcolor=PAPER,
        font=dict(family=FONT, size=13, color=INK),
        margin=dict(l=margin_left, r=28, t=56, b=52),
        hoverlabel=dict(
            bgcolor="#FFFFFF",
            bordercolor=GRID,
            font=dict(family=FONT, size=12, color=INK),
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            font=dict(size=12, color=MUTED),
            bgcolor=PAPER,
        ),
        showlegend=legend,
    )
    fig.update_xaxes(
        showgrid=False,
        linecolor=GRID,
        tickfont=dict(color=MUTED, size=12),
        title_font=dict(color=MUTED, size=12),
        zeroline=False,
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor=GRID,
        gridwidth=1,
        linecolor=GRID,
        tickfont=dict(color=MUTED, size=12),
        title_font=dict(color=MUTED, size=12),
        zeroline=False,
    )
    return fig


def simpson_figure(result: SimpsonResult) -> go.Figure:
    """Grouped bars showing the reversal between strata and the aggregate."""

    groups = result.table["group"].tolist()
    treatment = result.table["treatment"].tolist()
    control = result.table["control"].tolist()

    fig = go.Figure()
    fig.add_bar(
        x=groups,
        y=treatment,
        name="治疗组",
        marker_color=CORAL,
        marker_line_width=0,
        text=[f"{v:.1%}" for v in treatment],
        textposition="outside",
        textfont=dict(size=13, color=INK),
        hovertemplate="治疗组 · %{x}<br>康复率 %{y:.1%}<extra></extra>",
    )
    fig.add_bar(
        x=groups,
        y=control,
        name="对照组",
        marker_color=TEAL,
        marker_line_width=0,
        text=[f"{v:.1%}" for v in control],
        textposition="outside",
        textfont=dict(size=13, color=INK),
        hovertemplate="对照组 · %{x}<br>康复率 %{y:.1%}<extra></extra>",
    )

    if result.is_reversal:
        fig.add_vrect(
            x0=1.5,
            x1=2.5,
            fillcolor=CORAL,
            opacity=0.055,
            line_width=0,
            layer="below",
        )
        fig.add_annotation(
            x=2,
            y=1.04,
            text="合并后反转",
            showarrow=False,
            font=dict(size=12, color=CORAL_INK),
            bgcolor="rgba(214,90,58,0.10)",
            borderpad=4,
        )
    fig.update_layout(
        barmode="group",
        bargap=0.34,
        bargroupgap=0.08,
        yaxis=dict(
            title="康复率",
            range=[0, 1.12],
            tickformat=".0%",
            gridcolor=GRID,
        ),
        xaxis=dict(title=None),
    )
    fig.update_yaxes(rangemode="tozero")
    _style(fig, height=440)
    return fig


def base_rate_figure(result: BaseRateResult) -> go.Figure:
    """A 1,000-square icon grid of test outcomes."""

    categories = (
        ("真阳性", result.true_positive, TP_BLUE),
        ("假阳性", result.false_positive, FP_VERMILLION),
        ("真阴性", result.true_negative, TN_GRAY),
        ("假阴性", result.false_negative, FN_PINK),
    )
    labels: list[str] = []
    for label, count, _color in categories:
        labels.extend([label] * count)

    # Shuffle deterministically so the grid does not imply a meaningful order.
    order = np.random.default_rng(2024).permutation(len(labels))
    labels_arr = np.asarray(labels, dtype=object)[order]

    cols = 40
    rows = int(np.ceil(len(labels_arr) / cols))
    x = np.tile(np.arange(cols), rows)[: len(labels_arr)]
    y = np.repeat(np.arange(rows), cols)[: len(labels_arr)]

    fig = go.Figure()
    for label, count, color in categories:
        mask = labels_arr == label
        fig.add_scatter(
            x=x[mask],
            y=y[mask],
            mode="markers",
            marker=dict(symbol="square", size=8, color=color, line_width=0),
            name=f"{label} {count}",
            hoverinfo="skip",
        )

    fig.update_layout(
        xaxis=dict(visible=False, range=[-1, cols]),
        yaxis=dict(visible=False, range=[-1, rows], autorange="reversed"),
        margin=dict(l=12, r=12, t=24, b=36),
        height=390,
    )
    fig.update_yaxes(scaleanchor="x", scaleratio=1, showgrid=False)
    _style(fig, height=390, margin_left=12)
    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.02,
            xanchor="center",
            x=0.5,
            font=dict(size=12, color=MUTED),
        ),
        margin=dict(l=12, r=12, t=24, b=60),
    )
    return fig


def multiple_testing_figure(result: MultipleTestingResult) -> go.Figure:
    """Histogram of null p-values plus the running minimum.

    The two panels are stacked vertically so the figure remains readable in a
    narrow mobile column; side-by-side subplots become too cramped below 600px.
    """

    fig = make_subplots(
        rows=2,
        cols=1,
        row_heights=[0.46, 0.54],
        vertical_spacing=0.17,
        subplot_titles=(
            f"{result.n_tests} 次实验的 p 值",
            "连续检验中的最小 p 值",
        ),
    )

    fig.add_trace(
        go.Histogram(
            x=result.p_values,
            xbins=dict(start=0, end=1.0001, size=0.05),
            marker_color=PURPLE,
            marker_line_width=0,
            opacity=0.82,
            name="p 值",
            hovertemplate="p 值区间 %{x}<br>次数 %{y}<extra></extra>",
        ),
        row=1,
        col=1,
    )
    fig.add_vline(
        x=result.alpha,
        line_width=2,
        line_dash="dash",
        line_color=CORAL,
        row=1,
        col=1,
    )
    counts, _ = np.histogram(result.p_values, bins=np.arange(0, 1.05, 0.05))
    peak = max(int(counts.max()), 1)
    fig.add_annotation(
        x=result.alpha,
        y=peak * 0.92,
        xref="x",
        yref="y",
        text=f"α = {result.alpha:g}",
        showarrow=False,
        xanchor="left",
        yanchor="bottom",
        font=dict(size=11, color=CORAL_INK),
    )

    tests = np.arange(1, result.n_tests + 1)
    fig.add_trace(
        go.Scatter(
            x=tests,
            y=result.running_min,
            mode="lines",
            line=dict(color=TEAL, width=2.4),
            name="最小 p 值",
            hovertemplate="第 %{x} 次<br>最小 p = %{y:.3f}<extra></extra>",
        ),
        row=2,
        col=1,
    )
    fig.add_hline(
        y=result.alpha,
        line_width=1.5,
        line_dash="dash",
        line_color=CORAL,
        row=2,
        col=1,
    )
    fig.add_hrect(
        y0=0,
        y1=result.alpha,
        fillcolor=CORAL,
        opacity=0.06,
        line_width=0,
        row=2,
        col=1,
    )

    if result.n_significant:
        first_hit = int(np.argmax(result.significant))
        fig.add_trace(
            go.Scatter(
                x=[first_hit + 1],
                y=[result.running_min[first_hit]],
                mode="markers",
                marker=dict(color=GOLD, size=13, line=dict(color=INK, width=1)),
                name="首次显著",
                hovertemplate=(
                    "第 %{x} 次首次显著<br>p = %{y:.3f}<extra></extra>"
                ),
            ),
            row=2,
            col=1,
        )

    fig.update_xaxes(title="p 值", range=[0, 1], row=1, col=1)
    fig.update_yaxes(title="次数", row=1, col=1)
    fig.update_xaxes(title="已进行的检验次数", row=2, col=1)
    fig.update_yaxes(title=None, range=[0, 1], row=2, col=1)

    _style(fig, height=620)
    fig.update_layout(
        bargap=0.08,
        margin=dict(l=56, r=24, t=80, b=52),
        showlegend=False,
    )
    return fig


def regression_figure(result: RegressionResult) -> go.Figure:
    """Scatter of two noisy measurements with the selected group highlighted."""

    data = result.data
    selected = data[data["selected"]]
    others = data[~data["selected"]]
    low = float(min(data["first"].min(), data["second"].min())) - 0.15
    high = float(max(data["first"].max(), data["second"].max())) + 0.15

    fig = go.Figure()
    fig.add_scatter(
        x=others["first"],
        y=others["second"],
        mode="markers",
        marker=dict(color=BLUE, size=6, opacity=0.30, line_width=0),
        name="其他参与者",
        hovertemplate="第一次 %{x:.2f}<br>第二次 %{y:.2f}<extra></extra>",
    )
    fig.add_scatter(
        x=selected["first"],
        y=selected["second"],
        mode="markers",
        marker=dict(color=CORAL, size=8, opacity=0.85, line_width=0),
        name=f"第一次前 {result.top_fraction:.0%}",
        hovertemplate="第一次 %{x:.2f}<br>第二次 %{y:.2f}<extra></extra>",
    )
    fig.add_scatter(
        x=[low, high],
        y=[low, high],
        mode="lines",
        line=dict(color=MUTED, width=1, dash="dot"),
        name="y = x",
        hoverinfo="skip",
    )
    fig.add_scatter(
        x=[result.first_mean_selected],
        y=[result.second_mean_selected],
        mode="markers",
        marker=dict(color=GOLD, size=18, symbol="star", line=dict(color=INK, width=1)),
        name="选中组均值",
        hovertemplate=(
            "第一次均值 %{x:.2f}<br>第二次均值 %{y:.2f}<extra></extra>"
        ),
    )
    fig.add_annotation(
        x=result.first_mean_selected,
        y=result.second_mean_selected,
        text="选中组均值",
        showarrow=False,
        yshift=18,
        bgcolor="rgba(255,253,248,0.9)",
        bordercolor=GRID,
        borderwidth=1,
        borderpad=4,
        font=dict(size=12, color=INK),
    )
    fig.add_annotation(
        x=result.first_mean_selected,
        y=result.second_mean_selected,
        ax=result.first_mean_selected,
        ay=result.first_mean_selected,
        xref="x",
        yref="y",
        axref="x",
        ayref="y",
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=1.5,
        arrowcolor=CORAL,
        text="",
        opacity=0.7,
    )

    fig.update_layout(
        xaxis=dict(title="第一次成绩", range=[low, high], showgrid=True, gridcolor=GRID),
        yaxis=dict(title="第二次成绩", range=[low, high], showgrid=True, gridcolor=GRID),
    )
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    _style(fig, height=500)
    return fig


def coverage_figure(result: CoverageResult) -> go.Figure:
    """Vertical confidence intervals, coloured by whether they cover the truth."""

    intervals = result.intervals
    fig = go.Figure()

    for label, mask, color in (
        ("覆盖真值", intervals["captured"], TEAL),
        ("未覆盖", ~intervals["captured"], CORAL),
    ):
        subset = intervals[mask]
        if subset.empty:
            continue
        x: list[float | None] = []
        y: list[float | None] = []
        for row in subset.itertuples(index=False):
            x.extend([row.lower, row.upper, None])
            y.extend([row.interval, row.interval, None])
        fig.add_scatter(
            x=x,
            y=y,
            mode="lines",
            line=dict(color=color, width=2.2),
            name=f"{label} {len(subset)}",
            hoverinfo="skip",
        )

    fig.add_vline(
        x=result.population_mean,
        line_width=1.5,
        line_dash="dash",
        line_color=INK,
    )
    fig.add_annotation(
        x=result.population_mean,
        y=1,
        yref="paper",
        text="真实均值",
        showarrow=False,
        xanchor="left",
        yanchor="bottom",
        font=dict(size=11, color=INK),
    )
    fig.update_layout(
        xaxis=dict(title="估计值", showgrid=True, gridcolor=GRID),
        yaxis=dict(title="重复样本", showticklabels=False, range=[0, len(intervals) + 1]),
    )
    _style(fig, height=500)
    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            font=dict(size=12, color=MUTED),
        )
    )
    return fig
