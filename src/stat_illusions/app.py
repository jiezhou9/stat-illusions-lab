"""Streamlit application for the Statistical Illusions Lab."""

from __future__ import annotations

import html
import math

import streamlit as st

from .content import (
    HOME_INTRO,
    HOME_PRINCIPLES,
    MODULE_BY_KEY,
    MODULES,
    Module,
    explanation_for,
)
from .plots import (
    base_rate_figure,
    coverage_figure,
    multiple_testing_figure,
    regression_figure,
    simpson_figure,
)
from .simulations import (
    base_rate,
    confidence_interval_coverage,
    regression_to_mean,
    simpson_paradox,
    simulate_null_tests,
)

PLOT_CONFIG = {
    "displayModeBar": False,
    "responsive": True,
    "scrollZoom": False,
}

NAV_ITEMS: list[tuple[str, str]] = [("home", "开始 · 总览")] + [
    (module.key, f"{module.number} · {module.title}") for module in MODULES
]

CSS = """
<style>
:root {
  --ink: #1F2937;
  --muted: #6B7280;
  --paper: #F7F4EC;
  --card: #FFFDF8;
  --line: #E5DED0;
  --navy: #14213D;
  --coral: #D65A3A;
  --coral-ink: #A8432D;
  --teal: #2A9D8F;
  --teal-ink: #1B6B62;
  --gold: #E9C46A;
  --gold-ink: #8A6518;
}

html, body, [class*="css"] {
  font-family: "Noto Sans SC", "Source Han Sans SC", "PingFang SC",
    "Microsoft YaHei", "Segoe UI", sans-serif;
}

.stApp {
  background:
    radial-gradient(circle at 98% 0%, rgba(231, 111, 81, 0.07), transparent 28rem),
    radial-gradient(circle at 0% 30%, rgba(42, 157, 143, 0.055), transparent 26rem),
    var(--paper);
  color: var(--ink);
}

[data-testid="stHeader"] {
  background: transparent;
}

[data-testid="stToolbarActions"],
[data-testid="stBaseButton-header"],
[data-testid="stMainMenu"],
[data-testid="stDecoration"],
#MainMenu {
  display: none;
}

.block-container {
  max-width: 1180px;
  padding-top: 2.1rem;
  padding-bottom: 4rem;
}

h1, h2, h3, h4 {
  letter-spacing: -0.025em;
  color: var(--ink);
}

p, li {
  line-height: 1.75;
}

a {
  color: #B44A32;
  text-decoration: none;
  border-bottom: 1px solid rgba(180, 74, 50, 0.28);
}

a:hover {
  border-bottom-color: #B44A32;
}

[data-testid="stSidebar"] {
  background: var(--navy);
  border-right: 1px solid rgba(255, 255, 255, 0.08);
}

[data-testid="stSidebar"] * {
  color: #F4EFE4;
}

[data-testid="stSidebar"] .block-container {
  padding-top: 1.5rem;
}

[data-testid="stSidebar"] [role="radiogroup"] {
  gap: 0.22rem;
}

[data-testid="stSidebar"] [role="radiogroup"] label {
  padding: 0.56rem 0.7rem;
  border-radius: 0.55rem;
  border-left: 3px solid transparent;
  transition: background 120ms ease, border-color 120ms ease;
}

[data-testid="stSidebar"] [role="radiogroup"] label:hover {
  background: rgba(255, 255, 255, 0.07);
}

[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
  background: rgba(255, 255, 255, 0.10);
  border-left-color: var(--coral);
}

.brand {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  padding: 0.2rem 0 1.2rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.13);
  margin-bottom: 1rem;
}

.brand-mark {
  width: 2.55rem;
  height: 2.55rem;
  display: grid;
  place-items: center;
  border-radius: 0.8rem;
  background: var(--coral);
  color: white;
  font-family: Georgia, "Times New Roman", serif;
  font-size: 1.55rem;
  font-weight: 700;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.22);
}

.brand-title {
  font-size: 1.02rem;
  font-weight: 700;
  letter-spacing: 0.01em;
}

.brand-sub {
  margin-top: 0.2rem;
  font-size: 0.59rem;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: rgba(244, 239, 228, 0.56) !important;
}

.sidebar-note {
  margin-top: 1.3rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.12);
  font-size: 0.74rem;
  line-height: 1.9;
  color: rgba(244, 239, 228, 0.62) !important;
}

.hero {
  position: relative;
  overflow: hidden;
  border: 1px solid var(--line);
  border-radius: 1.6rem;
  padding: 3.2rem 3.1rem 2.7rem;
  background:
    radial-gradient(circle at 88% 8%, rgba(231, 111, 81, 0.20), transparent 36%),
    radial-gradient(circle at 12% 95%, rgba(42, 157, 143, 0.16), transparent 32%),
    #FCFAF4;
  box-shadow: 0 18px 50px rgba(20, 33, 61, 0.06);
}

.hero::after {
  content: "";
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(20, 33, 61, 0.035) 1px, transparent 1px),
    linear-gradient(90deg, rgba(20, 33, 61, 0.035) 1px, transparent 1px);
  background-size: 34px 34px;
  mask-image: linear-gradient(120deg, transparent 20%, black 95%);
  pointer-events: none;
}

.hero > * {
  position: relative;
  z-index: 1;
}

.kicker {
  font-size: 0.67rem;
  font-weight: 800;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--coral-ink);
}

.hero h1 {
  margin: 0.65rem 0 0.1rem;
  font-size: clamp(2.9rem, 7.2vw, 5.4rem);
  line-height: 0.98;
  font-weight: 900;
  letter-spacing: -0.065em;
}

.hero h1 .accent {
  color: var(--coral);
}

.hero-en {
  margin-top: 0.45rem;
  font-family: Georgia, "Times New Roman", serif;
  font-style: italic;
  font-size: clamp(1rem, 2.1vw, 1.35rem);
  color: #6B5E4B;
}

.hero p.lead {
  max-width: 39rem;
  margin: 1.35rem 0 1.55rem;
  font-size: 1.03rem;
  line-height: 1.95;
  color: #4B5563;
}

.hero-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 0.55rem;
}

.hero-badges span {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.37rem 0.72rem;
  border: 1px solid var(--line);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.52);
  font-size: 0.75rem;
  color: #5B5346;
}

.stat-strip {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0;
  margin: 1.25rem 0 2.4rem;
  border: 1px solid var(--line);
  border-radius: 1rem;
  background: rgba(255, 253, 248, 0.72);
  overflow: hidden;
}

.stat-strip > div {
  padding: 1.05rem 1.2rem;
  border-right: 1px solid var(--line);
}

.stat-strip > div:last-child {
  border-right: 0;
}

.stat-strip b {
  display: block;
  font-size: 1.55rem;
  line-height: 1.1;
  letter-spacing: -0.04em;
  color: var(--navy);
}

.stat-strip span {
  display: block;
  margin-top: 0.25rem;
  font-size: 0.75rem;
  color: var(--muted);
}

.section-heading {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 1rem;
  margin: 2.2rem 0 1rem;
}

.section-heading h2 {
  margin: 0;
  font-size: 1.65rem;
}

.section-heading span {
  font-size: 0.75rem;
  color: var(--muted);
}

.mobile-only {
  display: none;
}

.module-card {
  position: relative;
  min-height: 255px;
  padding: 1.25rem 1.25rem 1.1rem;
  margin-bottom: 1rem;
  border: 1px solid var(--line);
  border-radius: 1.05rem;
  background: rgba(255, 253, 248, 0.9);
  box-shadow: 0 8px 26px rgba(20, 33, 61, 0.035);
  transition: transform 160ms ease, box-shadow 160ms ease;
}

.module-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 16px 34px rgba(20, 33, 61, 0.08);
}

.module-card::before {
  content: "";
  position: absolute;
  left: 0;
  top: 1.15rem;
  bottom: 1.15rem;
  width: 4px;
  border-radius: 0 4px 4px 0;
  background: var(--accent);
}

.module-num {
  font-family: Georgia, "Times New Roman", serif;
  font-size: 0.78rem;
  letter-spacing: 0.08em;
  color: var(--accent-ink);
}

.module-title {
  margin-top: 0.28rem;
  font-size: 1.28rem;
  font-weight: 800;
  letter-spacing: -0.03em;
}

.module-sub {
  margin-top: 0.15rem;
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--accent-ink);
}

.module-hook {
  margin: 0.8rem 0 1rem;
  font-size: 0.84rem;
  line-height: 1.7;
  color: #5B6472;
}

.tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.32rem;
}

.tag {
  padding: 0.18rem 0.48rem;
  border-radius: 999px;
  background: #F2EEE5;
  font-size: 0.66rem;
  color: #6B6254;
}

.experiment-head {
  display: flex;
  gap: 1.5rem;
  align-items: flex-start;
  margin: 0.2rem 0 1.7rem;
  padding-bottom: 1.25rem;
  border-bottom: 1px solid var(--line);
}

.experiment-number {
  flex: 0 0 auto;
  font-family: Georgia, "Times New Roman", serif;
  font-size: clamp(3.6rem, 8vw, 5.8rem);
  line-height: 0.85;
  font-weight: 700;
  letter-spacing: -0.06em;
  color: var(--accent);
  opacity: 0.9;
}

.experiment-title {
  font-size: clamp(2rem, 4.4vw, 3.35rem);
  line-height: 1.05;
  font-weight: 900;
  letter-spacing: -0.05em;
  margin: 0.2rem 0 0.25rem;
}

.experiment-sub {
  font-size: 1.02rem;
  font-weight: 600;
  color: var(--accent-ink);
}

.experiment-hook {
  max-width: 46rem;
  margin-top: 0.7rem;
  font-size: 0.92rem;
  color: #5B6472;
}

.panel-title {
  margin: 0 0 0.2rem;
  font-size: 0.69rem;
  font-weight: 800;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--muted);
}

.callout {
  margin: 0.8rem 0 1rem;
  padding: 0.95rem 1rem 0.95rem 1.1rem;
  border-left: 4px solid var(--coral);
  border-radius: 0 0.65rem 0.65rem 0;
  background: rgba(231, 111, 81, 0.07);
}

.callout.teal {
  border-left-color: var(--teal);
  background: rgba(42, 157, 143, 0.07);
}

.callout.gold {
  border-left-color: #C79A2E;
  background: rgba(233, 196, 106, 0.14);
}

.callout-label {
  margin-bottom: 0.25rem;
  font-size: 0.65rem;
  font-weight: 800;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #9A4A35;
}

.callout.teal .callout-label {
  color: #1B6B62;
}

.callout.gold .callout-label {
  color: #8A6518;
}

.callout p {
  margin: 0;
  font-size: 0.86rem;
  line-height: 1.75;
  color: #3F4855;
}

.metric-card {
  min-height: 112px;
  padding: 0.85rem 0.9rem;
  border: 1px solid var(--line);
  border-radius: 0.75rem;
  background: rgba(255, 253, 248, 0.82);
}

.metric-label {
  font-size: 0.68rem;
  line-height: 1.45;
  color: var(--muted);
}

.metric-value {
  margin-top: 0.3rem;
  font-size: 1.42rem;
  line-height: 1.15;
  font-weight: 800;
  letter-spacing: -0.04em;
  color: var(--navy);
}

.metric-note {
  margin-top: 0.25rem;
  font-size: 0.65rem;
  color: #6F6659;
}

[data-testid="stButton"] > button {
  min-height: 2.2rem;
  border-color: var(--line);
  border-radius: 0.6rem;
  background: rgba(255, 253, 248, 0.72);
  color: var(--navy);
  font-size: 0.8rem;
  font-weight: 600;
}

[data-testid="stButton"] > button:hover {
  border-color: var(--coral);
  background: #FFFDF8;
  color: var(--coral-ink);
}

.section-rule {
  height: 1px;
  margin: 2.4rem 0 1.4rem;
  background: var(--line);
}

.footer {
  margin-top: 3.2rem;
  padding-top: 1.2rem;
  border-top: 1px solid var(--line);
  font-size: 0.74rem;
  color: #5B6472;
}

.note-box {
  padding: 0.9rem 1rem;
  border: 1px dashed #D8CFBE;
  border-radius: 0.7rem;
  background: rgba(255, 253, 248, 0.55);
  font-size: 0.78rem;
  line-height: 1.75;
  color: #6B6254;
}

@media (max-width: 720px) {
  .desktop-only {
    display: none;
  }
  .mobile-only {
    display: inline;
  }
  .block-container {
    padding-top: 1.1rem;
  }
  .hero {
    padding: 2rem 1.35rem 1.8rem;
    border-radius: 1.2rem;
  }
  .hero h1 {
    font-size: 3rem;
  }
  .stat-strip {
    grid-template-columns: 1fr;
  }
  .stat-strip > div {
    border-right: 0;
    border-bottom: 1px solid var(--line);
  }
  .stat-strip > div:last-child {
    border-bottom: 0;
  }
  .experiment-head {
    gap: 0.9rem;
  }
  .experiment-number {
    font-size: 3.4rem;
  }
}
</style>
"""


def _safe(text: str) -> str:
    return html.escape(text, quote=True)


def _inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def _scroll_to_top() -> None:
    """Reset Streamlit's internal main scroll container on page changes."""

    st.html(
        """
        <script>
          const root = window.parent !== window ? window.parent : window;
          const reset = () => {
            try {
              const main = root.document.querySelector('[data-testid="stMain"]');
              if (main) main.scrollTo(0, 0);
              root.scrollTo(0, 0);
            } catch (error) {
              // Cross-origin iframe: nothing to reset from here.
            }
          };
          setTimeout(reset, 0);
          setTimeout(reset, 250);
          setTimeout(reset, 800);
        </script>
        """,
        unsafe_allow_javascript=True,
    )


def _sync_query_params() -> None:
    """Keep the current experiment in the URL so a page can be shared."""

    label = st.session_state.get("nav_label")
    key = next((key for key, candidate in NAV_ITEMS if candidate == label), "home")
    if st.query_params.get("page") != key:
        st.query_params["page"] = key


def _sidebar() -> str:
    years = "2026"
    st.sidebar.markdown(
        """
        <div class="brand">
          <div class="brand-mark">Σ</div>
          <div>
            <div class="brand-title">统计错觉实验室</div>
            <div class="brand-sub">Statistical Illusions</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    labels = [label for _, label in NAV_ITEMS]
    requested = st.query_params.get("page", "home")
    if isinstance(requested, list):
        requested = requested[0] if requested else "home"
    requested_index = next(
        (index for index, (key, _label) in enumerate(NAV_ITEMS) if key == requested),
        0,
    )
    radio_kwargs: dict[str, object] = {
        "label_visibility": "collapsed",
        "key": "nav_label",
        "on_change": _sync_query_params,
    }
    # Passing both index= and an already-populated widget key triggers a
    # Streamlit policy warning when a card button navigates.
    if "nav_label" not in st.session_state:
        radio_kwargs["index"] = requested_index
    selected = st.sidebar.radio("实验目录", labels, **radio_kwargs)
    st.sidebar.markdown(
        f"""
        <div class="sidebar-note">
          5 个交互实验<br>
          Python · NumPy · Plotly · Streamlit<br>
          MIT License · {years}
        </div>
        """,
        unsafe_allow_html=True,
    )
    return next(key for key, label in NAV_ITEMS if label == selected)


def _hero() -> None:
    st.markdown(
        f"""
        <section class="hero">
          <div class="kicker">Interactive Statistics · 2026</div>
          <h1>统计错觉<br><span class="accent">实验室</span></h1>
          <div class="hero-en">Statistical Illusions Lab</div>
          <p class="lead">{HOME_INTRO}</p>
          <div class="hero-badges">
            <span>◆ 5 个可交互实验</span>
            <span>◆ 固定种子，同环境可复现</span>
            <span>◆ Python + Streamlit</span>
            <span>◆ MIT 开源</span>
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def _stat_strip() -> None:
    st.markdown(
        """
        <div class="stat-strip">
          <div><b>05</b><span>核心统计错觉</span></div>
          <div><b>可复现</b><span>固定种子 · 同一环境</span></div>
          <div><b>0</b><span>需要注册或上传数据</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _module_card(module: Module) -> None:
    tags = "".join(f'<span class="tag">{_safe(tag)}</span>' for tag in module.tags)
    st.markdown(
        f"""
        <div class="module-card"
             style="--accent: {module.accent}; --accent-ink: {module.accent_ink};">
          <div class="module-num">EXPERIMENT {module.number}</div>
          <div class="module-title">{_safe(module.title)}</div>
          <div class="module-sub">{_safe(module.subtitle)}</div>
          <p class="module-hook">{_safe(module.hook)}</p>
          <div class="tag-row">{tags}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _experiment_header(module: Module) -> None:
    st.markdown(
        f"""
        <header class="experiment-head"
                style="--accent: {module.accent}; --accent-ink: {module.accent_ink};">
          <div class="experiment-number">{module.number}</div>
          <div>
            <div class="kicker">Experiment {module.number}</div>
            <h1 class="experiment-title">{_safe(module.title)}</h1>
            <div class="experiment-sub">{_safe(module.subtitle)}</div>
            <div class="experiment-hook">{_safe(module.hook)}</div>
          </div>
        </header>
        """,
        unsafe_allow_html=True,
    )


def _panel_title(text: str) -> None:
    st.markdown(f'<div class="panel-title">{_safe(text)}</div>', unsafe_allow_html=True)


def _callout(label: str, text: str, tone: str = "") -> None:
    tone_class = f" {tone}" if tone else ""
    st.markdown(
        f"""
        <div class="callout{tone_class}">
          <div class="callout-label">{_safe(label)}</div>
          <p>{text}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _metric_card(
    label: str,
    value: str,
    note: str = "",
    color: str = "#14213D",
) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
          <div class="metric-label">{label}</div>
          <div class="metric-value" style="color: {color};">{value}</div>
          <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _metric_row(cards: list[tuple[str, str, str, str]]) -> None:
    columns = st.columns(len(cards), gap="small")
    for column, (label, value, note, color) in zip(columns, cards, strict=True):
        with column:
            _metric_card(label, value, note, color)


def _sign_color(value: float) -> str:
    if abs(value) < 1e-9:
        return "#5B6472"
    return "#1B6B62" if value > 0 else "#A8432D"


def _pp_value(value: float) -> str:
    if abs(value) < 1e-9:
        return "0.0 pp"
    return f"{value * 100:+.1f} pp"


def _render_explanation(key: str, result: object) -> None:
    content = explanation_for(key, result)
    st.markdown('<div class="section-rule"></div>', unsafe_allow_html=True)
    st.markdown("## 读懂这个实验")
    tabs = st.tabs(["你看到了什么", "为什么会这样", "如何避免", "方法细节"])
    with tabs[0]:
        st.markdown(content["see"])
    with tabs[1]:
        st.markdown(content["why"])
    with tabs[2]:
        st.markdown(content["avoid"])
    with tabs[3]:
        st.markdown(content["method"])
        st.latex(content["formula"])


def _render_references(module: Module) -> None:
    st.markdown("### 延伸阅读")
    for reference in module.references:
        st.markdown(
            f'- <a href="{reference.url}" target="_blank" rel="noopener">'
            f"{_safe(reference.label)}</a>",
            unsafe_allow_html=True,
        )
    st.markdown(
        '<div class="note-box">模拟逻辑位于 '
        "<code>src/stat_illusions/simulations.py</code>，"
        "单元测试位于 <code>tests/</code>。每个随机实验都使用可控制的种子，"
        "在相同依赖环境下结果可以重复。</div>",
        unsafe_allow_html=True,
    )


def _footer() -> None:
    st.markdown(
        """
        <div class="footer">
          Statistical Illusions Lab · 用模拟对抗统计直觉 ·
          欢迎 Issue、PR 与教学使用
        </div>
        """,
        unsafe_allow_html=True,
    )


def _go_to_module(key: str) -> None:
    label = next(label for candidate, label in NAV_ITEMS if candidate == key)
    st.session_state["nav_label"] = label
    st.query_params["page"] = key


def page_home() -> None:
    _hero()
    _stat_strip()

    st.markdown(
        """
        <div class="section-heading">
          <h2>五个实验，五种思维陷阱</h2>
          <span class="desktop-only">从左侧目录进入，或点击卡片下方按钮</span>
          <span class="mobile-only">点卡片下方按钮，或点左上角 ›› 打开目录</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    for start in range(0, len(MODULES), 3):
        columns = st.columns(3, gap="medium")
        for column, module in zip(columns, MODULES[start : start + 3], strict=False):
            with column:
                _module_card(module)
                st.button(
                    "打开实验 →",
                    key=f"open_{module.key}",
                    on_click=_go_to_module,
                    args=(module.key,),
                    width="stretch",
                )

    st.markdown(
        """
        <div class="section-heading">
          <h2>怎么使用</h2>
          <span>每个实验约 3–5 分钟</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    columns = st.columns(3, gap="medium")
    for column, (title, body) in zip(columns, HOME_PRINCIPLES, strict=True):
        with column:
            st.markdown(f"#### {title}")
            st.markdown(body)

    st.markdown(
        """
        <div class="section-heading">
          <h2>适合谁</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )
    cols = st.columns(3, gap="medium")
    with cols[0]:
        st.markdown("**统计初学者**")
        st.markdown("用可调参数建立直觉，而不是背公式。")
    with cols[1]:
        st.markdown("**数据从业者**")
        st.markdown("在做 A/B 测试、报表和因果判断时避开常见坑。")
    with cols[2]:
        st.markdown("**教学者**")
        st.markdown("可直接用于课堂演示；代码和解释均可复用。")

    _footer()


def page_simpson() -> None:
    module = MODULE_BY_KEY["simpson"]
    _experiment_header(module)
    left, right = st.columns([1.0, 1.62], gap="large")

    with left:
        _callout(
            "先猜一猜",
            "一种新药在轻症和重症患者中都比旧药有效。把两组病人合并后，"
            "新药的整体康复率却可能更低。这可能吗？",
        )
        _panel_title("调节参数")
        mild_treatment = st.slider(
            "轻症康复率 · 治疗组",
            50,
            100,
            92,
            format="%d%%",
            key="simp_mild_t",
        )
        mild_control = st.slider(
            "轻症康复率 · 对照组",
            50,
            100,
            85,
            format="%d%%",
            key="simp_mild_c",
        )
        severe_treatment = st.slider(
            "重症康复率 · 治疗组",
            20,
            90,
            62,
            format="%d%%",
            key="simp_severe_t",
        )
        severe_control = st.slider(
            "重症康复率 · 对照组",
            20,
            90,
            50,
            format="%d%%",
            key="simp_severe_c",
        )
        st.markdown("**患者构成**")
        share_treatment = st.slider(
            "治疗组中重症患者的比例",
            0,
            100,
            75,
            format="%d%%",
            key="simp_share_t",
        )
        share_control = st.slider(
            "对照组中重症患者的比例",
            0,
            100,
            25,
            format="%d%%",
            key="simp_share_c",
        )
        st.caption("只要两层都是治疗组更好，把两组重症比例调成一样，反转一定消失。")

    result = simpson_paradox(
        mild_treatment=mild_treatment / 100,
        severe_treatment=severe_treatment / 100,
        mild_control=mild_control / 100,
        severe_control=severe_control / 100,
        severe_share_treatment=share_treatment / 100,
        severe_share_control=share_control / 100,
    )

    with right:
        st.plotly_chart(
            simpson_figure(result),
            width="stretch",
            config=PLOT_CONFIG,
        )
        _metric_row(
            [
                (
                    "轻症：治疗 − 对照",
                    _pp_value(result.advantages["mild"]),
                    "百分点差异",
                    _sign_color(result.advantages["mild"]),
                ),
                (
                    "重症：治疗 − 对照",
                    _pp_value(result.advantages["severe"]),
                    "百分点差异",
                    _sign_color(result.advantages["severe"]),
                ),
                (
                    "整体：治疗 − 对照",
                    _pp_value(result.advantages["overall"]),
                    "合并后的结果",
                    _sign_color(result.advantages["overall"]),
                ),
            ]
        )
        mild_sign, severe_sign, overall_sign = result.signs
        if result.is_reversal:
            if mild_sign == 1 and severe_sign == 1:
                _callout(
                    "反转发生了",
                    "治疗组在两个分层里都更好，但合并后的整体康复率更低。"
                    "差异来自两组患者构成的失衡，而不是治疗效果本身。",
                    tone="teal",
                )
            else:
                _callout(
                    "反方向的反转",
                    "治疗组在两个分层里都更差，但合并后的整体康复率更高。"
                    "合并数字同样不能替代分层结论。",
                    tone="teal",
                )
        elif mild_sign == 0 or severe_sign == 0:
            _callout(
                "至少一个分层持平",
                "至少一个分层里，治疗组和对照组的康复率相同。"
                "合并结果由另一层和患者构成共同决定，不能归因于“两层方向相反”。",
                tone="gold",
            )
        elif overall_sign == 0:
            _callout(
                "合并后基本持平",
                "分层结果与合并结果并不冲突，只是整体差值约为 0；"
                "不要把它解释成某一层更好或更差。",
                tone="gold",
            )
        elif mild_sign == 1 and severe_sign == 1:
            _callout(
                "这次没有反转",
                "两个分层都更好，合并后也更好。调整两组重症比例，观察合并结果如何变化。",
                tone="gold",
            )
        elif mild_sign == -1 and severe_sign == -1:
            _callout(
                "两层都更差，整体也更差",
                "当前分层和整体方向一致。调整两组重症比例，可能出现反方向的反转。",
                tone="gold",
            )
        else:
            _callout(
                "分层方向不一致",
                "一个分层更好、另一个更差时，合并数字会把两种相反的效果混在一起；"
                "这时更不应该只看整体结果。",
                tone="gold",
            )

    _render_explanation("simpson", result)
    _render_references(module)
    _footer()


def page_base_rate() -> None:
    module = MODULE_BY_KEY["base_rate"]
    _experiment_header(module)
    left, right = st.columns([1.0, 1.62], gap="large")

    with left:
        _callout(
            "先猜一猜 · 默认参数",
            "一种病的患病率是 1%。检测灵敏度 99%、特异度 95%。"
            "如果一个人检测呈阳性，他真正患病的概率大约是多少？",
        )
        _panel_title("调节参数")
        prevalence = st.slider(
            "患病率",
            0.1,
            20.0,
            1.0,
            0.1,
            format="%.1f%%",
            key="br_prev",
        )
        sensitivity = st.slider(
            "灵敏度 P(阳性 | 患病)",
            50,
            100,
            99,
            format="%d%%",
            key="br_sens",
        )
        specificity = st.slider(
            "特异度 P(阴性 | 健康)",
            50,
            100,
            95,
            format="%d%%",
            key="br_spec",
        )
        guess = st.slider(
            "你的直觉：阳性者患病概率",
            0,
            100,
            80,
            format="%d%%",
            key="br_guess",
        )

    result = base_rate(
        prevalence=prevalence / 100,
        sensitivity=sensitivity / 100,
        specificity=specificity / 100,
        population=1000,
    )

    with right:
        st.plotly_chart(
            base_rate_figure(result),
            width="stretch",
            config=PLOT_CONFIG,
        )
        ppv_defined = not math.isnan(result.ppv)
        gap = guess / 100 - result.ppv if ppv_defined else float("nan")
        _metric_row(
            [
                (
                    "阳性者真正患病",
                    f"{result.ppv:.1%}" if ppv_defined else "—",
                    "阳性预测值 PPV（精确计算）",
                    "#A8432D",
                ),
                (
                    "阳性结果中的假阳性",
                    f"{1 - result.ppv:.1%}" if ppv_defined else "—",
                    "精确概率；不以取整人数为准",
                    "#B44A32",
                ),
                (
                    "每 1,000 人的真阳性",
                    f"{result.true_positive}",
                    "被正确找出的患者（取整示意）",
                    "#1B6B62",
                ),
            ]
        )
        st.caption(
            "方块数量按 1,000 人取整，仅作示意；PPV 与假阳性占比使用精确概率，"
            "小概率事件下取整可能造成明显差异。"
        )
        if not ppv_defined:
            _callout(
                "阳性预测值没有定义",
                "当前参数下没有阳性结果，因此无法计算 P(患病 | 阳性)。",
                tone="gold",
            )
        elif abs(gap) >= 0.10:
            direction = "高估" if gap > 0 else "低估"
            if result.ppv < 0.5 - 1e-9:
                explanation = (
                    "在这个参数下，假阳性的比例超过真阳性；"
                    "低基础率会把这种效应放大。"
                )
            elif abs(result.ppv - 0.5) <= 1e-9:
                explanation = "在这个参数下，真阳性和假阳性正好各占一半。"
            else:
                explanation = (
                    "在这个参数下，真阳性仍占多数；把患病率调低，"
                    "可以看到假阳性如何逐渐占据阳性结果。"
                )
            _callout(
                f"直觉{direction}了",
                f"你猜 {guess}%，实际约为 {result.ppv:.1%}。{explanation}",
                tone="teal" if gap < 0 else "gold",
            )
        else:
            _callout(
                "很接近",
                "你的直觉与贝叶斯计算结果相差不到 10 个百分点。"
                "试着把患病率调到 10% 以上，看看 PPV 如何变化。",
                tone="teal",
            )

    _render_explanation("base_rate", result)
    _render_references(module)
    _footer()


def page_multiple_testing() -> None:
    module = MODULE_BY_KEY["multiple"]
    _experiment_header(module)
    left, right = st.columns([1.0, 1.72], gap="large")

    with left:
        _callout(
            "先猜一猜 · 默认参数",
            "你做了 100 次 A/A 测试：两组来自完全相同的分布，没有任何真实差异。"
            "其中大约会有多少次得到 p < 0.05？",
        )
        _panel_title("调节参数")
        n_tests = st.slider(
            "实验次数",
            10,
            300,
            100,
            10,
            key="mt_tests",
        )
        n_per_group = st.slider(
            "每组样本量",
            5,
            100,
            30,
            5,
            key="mt_n",
        )
        alpha = st.select_slider(
            "显著性水平 α",
            options=[0.001, 0.01, 0.05, 0.10],
            value=0.05,
            format_func=lambda value: f"{value:g}",
            key="mt_alpha",
        )
        seed = st.number_input(
            "随机种子",
            min_value=0,
            max_value=9999,
            value=42,
            step=1,
            key="mt_seed",
        )
        st.caption("改变种子会重新抽取一批完全无效的 A/A 实验。")

    result = simulate_null_tests(
        n_tests=int(n_tests),
        n_per_group=int(n_per_group),
        alpha=float(alpha),
        seed=int(seed),
    )

    with right:
        st.plotly_chart(
            multiple_testing_figure(result),
            width="stretch",
            config=PLOT_CONFIG,
        )
        _metric_row(
            [
                (
                    "“显著”结果",
                    f"{result.n_significant} / {result.n_tests}",
                    "全部来自零假设",
                    "#A8432D",
                ),
                (
                    "预期假阳性",
                    f"{result.expected_false_positives:.1f}",
                    f"{result.n_tests} × α",
                    "#5E4B8B",
                ),
                (
                    "至少一次假阳性",
                    f"{result.familywise_error:.1%}",
                    "族错误率 FWER",
                    "#8A6518",
                ),
            ]
        )
        if result.n_significant:
            _callout(
                "你抓到了一只“显著”的噪声",
                f"这 {result.n_significant} 个显著结果都来自没有任何真实效应的实验。"
                "如果只报告它们，你就会得到一个看起来很有说服力、实际却是假阳性的结论。",
                tone="gold",
            )
        else:
            _callout(
                "这次很幸运",
                "这一批实验没有出现 p < 0.05 的结果。但改变随机种子、增加实验次数，"
                "迟早会撞上假阳性。",
                tone="teal",
            )

    _render_explanation("multiple", result)
    _render_references(module)
    _footer()


def page_regression() -> None:
    module = MODULE_BY_KEY["regression"]
    _experiment_header(module)
    left, right = st.columns([1.0, 1.62], gap="large")

    with left:
        _callout(
            "先猜一猜 · 默认参数",
            "你按第一次考试成绩选出前 10% 的学生，再考一次。"
            "即使他们的真实能力完全没变，第二次平均分也会下降。为什么？",
        )
        _panel_title("调节参数")
        n = st.slider(
            "参与人数",
            100,
            2000,
            500,
            50,
            key="rt_n",
        )
        noise = st.slider(
            "测量噪声",
            0.0,
            2.0,
            1.0,
            0.1,
            key="rt_noise",
        )
        top_fraction = st.slider(
            "选拔比例：第一次前百分之几",
            1,
            50,
            10,
            1,
            format="%d%%",
            key="rt_top",
        )
        seed = st.number_input(
            "随机种子",
            min_value=0,
            max_value=9999,
            value=7,
            step=1,
            key="rt_seed",
        )
        st.caption("噪声设为 0 时，两次测量完全一致，回落会消失。")

    result = regression_to_mean(
        n=int(n),
        noise=float(noise),
        top_fraction=top_fraction / 100,
        seed=int(seed),
    )

    with right:
        st.plotly_chart(
            regression_figure(result),
            width="stretch",
            config=PLOT_CONFIG,
        )
        _metric_row(
            [
                (
                    "选中组第一次均值",
                    f"{result.first_mean_selected:.2f}",
                    "按第一次成绩选拔",
                    "#A8432D",
                ),
                (
                    "选中组第二次均值",
                    f"{result.second_mean_selected:.2f}",
                    "同一个人，再测一次",
                    "#2F5F7A",
                ),
                (
                    "平均回落",
                    f"{result.regression_amount:.2f}",
                    (
                        "向总体均值靠近"
                        if result.regression_amount > 0
                        else "本次为抽样波动"
                    ),
                    "#8A6518",
                ),
            ]
        )
        if result.regression_amount > 0.15:
            _callout(
                "能力没变，成绩却回落了",
                f"选中组的平均分从 {result.first_mean_selected:.2f} 降到 "
                f"{result.second_mean_selected:.2f}。第一次选拔挑中了部分“运气好”的人，"
                "第二次测量时运气回归平均。",
                tone="teal",
            )
        elif result.regression_amount > 0:
            _callout(
                "回落幅度较小",
                "当前回落幅度较小，可能来自较低的测量噪声或较温和的选拔比例。"
                "把测量噪声调高，再观察极端组的后续表现。",
                tone="gold",
            )
        else:
            _callout(
                "这次没有出现回落",
                "理论上按第一次成绩选拔后应出现向均值回落的趋势，"
                "但本次样本的估计值略低于 0，属于有限样本的抽样波动。"
                "换一个随机种子，通常会看到正的回落。",
                tone="gold",
            )

    _render_explanation("regression", result)
    _render_references(module)
    _footer()


def page_ci() -> None:
    module = MODULE_BY_KEY["ci"]
    _experiment_header(module)
    left, right = st.columns([1.0, 1.62], gap="large")

    with left:
        _callout(
            "先猜一猜 · 默认参数",
            "重复抽样并计算 95% 置信区间 100 次，大约有多少个区间会盖住真实均值？"
            "某个已经算出的区间，盖住真值的概率又是多少？",
        )
        _panel_title("调节参数")
        n_intervals = st.slider(
            "重复抽样次数",
            20,
            300,
            100,
            10,
            key="ci_reps",
        )
        sample_size = st.slider(
            "每次抽样的样本量",
            5,
            200,
            30,
            5,
            key="ci_n",
        )
        confidence = st.select_slider(
            "置信水平",
            options=[80, 90, 95, 99],
            value=95,
            format_func=lambda value: f"{value}%",
            key="ci_conf",
        )
        seed = st.number_input(
            "随机种子",
            min_value=0,
            max_value=9999,
            value=11,
            step=1,
            key="ci_seed",
        )
        st.caption("提高置信水平会让区间变宽；增加样本量会让区间变窄。")

    result = confidence_interval_coverage(
        n_intervals=int(n_intervals),
        sample_size=int(sample_size),
        confidence=confidence / 100,
        seed=int(seed),
    )

    with right:
        st.plotly_chart(
            coverage_figure(result),
            width="stretch",
            config=PLOT_CONFIG,
        )
        _metric_row(
            [
                (
                    "实际覆盖率",
                    f"{result.coverage:.1%}",
                    f"{n_intervals} 次重复抽样",
                    "#1B6B62",
                ),
                (
                    "理论覆盖率",
                    f"{result.expected_coverage:.1%}",
                    "置信水平",
                    "#5E4B8B",
                ),
                (
                    "未覆盖次数",
                    f"{int((~result.intervals['captured']).sum())}",
                    "区间没有盖住真值",
                    "#A8432D",
                ),
            ]
        )
        _callout(
            f"{result.expected_coverage:.0%} 描述的是长期频率",
            f"在这 {n_intervals} 次重复抽样中，有 {result.coverage:.1%} 的区间覆盖了真实均值。"
            "置信水平不是“当前这个区间盖住真值的概率”，而是构造区间的方法在长期重复中的覆盖率。",
            tone="teal",
        )

    _render_explanation("ci", result)
    _render_references(module)
    _footer()


PAGES = {
    "home": page_home,
    "simpson": page_simpson,
    "base_rate": page_base_rate,
    "multiple": page_multiple_testing,
    "regression": page_regression,
    "ci": page_ci,
}


def main() -> None:
    st.set_page_config(
        page_title="统计错觉实验室 · Statistical Illusions Lab",
        page_icon="Σ",
        layout="wide",
        initial_sidebar_state="auto",
    )
    _inject_css()
    key = _sidebar()
    if st.session_state.get("_scroll_page") != key:
        st.session_state["_scroll_page"] = key
        _scroll_to_top()
    PAGES[key]()
