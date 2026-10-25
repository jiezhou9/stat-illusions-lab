<p align="center">
  <img src="assets/banner.svg" alt="Statistical Illusions Lab" width="100%">
</p>

<h1 align="center">Statistical Illusions Lab</h1>

<p align="center">
  <strong>Interactive simulations for the moments when the math is right — and the interpretation is wrong.</strong>
</p>

<p align="center">
  <a href="https://stat-illusions-lab.streamlit.app/">
    <img src="https://static.streamlit.io/badges/streamlit_badge_black_white.svg" alt="Live Demo">
  </a>
  <a href="https://github.com/jiezhou9/stat-illusions-lab/actions/workflows/ci.yml">
    <img src="https://github.com/jiezhou9/stat-illusions-lab/actions/workflows/ci.yml/badge.svg" alt="CI">
  </a>
  <img src="https://img.shields.io/badge/Python-3.10%2B-14213D" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/License-MIT-2A9D8F" alt="MIT License">
</p>

**Live demo:** [stat-illusions-lab.streamlit.app](https://stat-illusions-lab.streamlit.app/)

[中文 README](README.md) · [Methods](docs/methods.md) · [Publishing checklist](docs/publishing.md) · [Contributing](CONTRIBUTING.md)

---

<p align="center">
  <img src="assets/screenshots/home.png" alt="Statistical Illusions Lab home page" width="86%">
</p>

## What is this?

Statistical Illusions Lab is an open-source, interactive collection of five statistical traps. Each experiment starts with an intuition, lets you change the parameters, and then shows where the intuition breaks.

**Interface language:** the current UI is Chinese-only; this README documents the project in English.

| # | Experiment | The surprise | Concepts |
|---|------------|--------------|----------|
| 01 | **Simpson's paradox** | A treatment is better in every subgroup but worse overall | confounding, stratification, causal inference |
| 02 | **Base-rate fallacy** | A 99% sensitive test can still produce mostly false positives | Bayes' rule, natural frequencies, PPV |
| 03 | **p-hacking** | 100 A/A tests with no real effect still produce "significant" results | multiple testing, FWER, selective reporting |
| 04 | **Regression to the mean** | Top performers score lower on a second measurement | measurement error, selection, extreme groups |
| 05 | **Confidence intervals** | About 95 of 100 repeated intervals cover the truth — but not each interval with 95% probability | sampling distribution, interval estimation, frequentist interpretation |

### Methods at a glance

| Experiment | Model | What is shown | Key assumption |
|------------|-------|---------------|----------------|
| Simpson's paradox | Recovery rates weighted by patient mix | stratum vs aggregate rates | expected rates, no sampling error |
| Base-rate fallacy | Bayes' rule with natural frequencies | PPV, false-positive share | fixed sensitivity/specificity |
| p-hacking | two-sided z-tests on independent A/A samples | p-value distribution, FWER | known variance, independent tests |
| Regression to the mean | latent ability + two independent measurement errors | selected-group means | bivariate normal, equal noise |
| Confidence intervals | z-intervals with known σ | repeated-sample coverage | normal, i.i.d. samples |

See [docs/methods.md](docs/methods.md) for derivations and limitations.

## Quick start

Requires Python 3.10+.

```bash
git clone https://github.com/jiezhou9/stat-illusions-lab.git
cd stat-illusions-lab

python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -e ".[dev]"
streamlit run app.py
```

On Windows, if PowerShell blocks `Activate.ps1`, you do not need to activate the environment. Run the executable directly:

```powershell
.\.venv\Scripts\streamlit.exe run app.py
```

Do not launch the app with `python app.py`; Streamlit apps require `streamlit run`.

Or run the app without installing the package:

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Project structure

```text
.
├── app.py                     # Streamlit entry point
├── src/stat_illusions/
│   ├── app.py                 # pages and layout
│   ├── content.py             # copy and references
│   ├── plots.py               # Plotly figures
│   └── simulations.py         # pure, testable simulations
├── tests/
├── docs/methods.md            # models, assumptions, limitations
├── assets/banner.svg
└── .github/workflows/ci.yml
```

## Design principles

- **Simulation is separate from presentation.** The simulation layer has no Streamlit dependency and is reproducible from a seed.
- **Narrative before formulas.** Every experiment begins with a concrete question, then adds controls and visual feedback, then the method.
- **Reproducibility is a feature.** Seeds are exposed, and tests cover statistical properties as well as page rendering.
- **Clarity over spectacle.** Each chart supports one specific conceptual turn.

## Tests

```bash
pytest
ruff check .
```

CI runs on Python 3.10, 3.11 and 3.12.

## Limitations

- This is a **teaching simulation**, not research-grade statistical software, and it does not replace a real study design or causal analysis.
- The models are deliberately simplified: expected rates in the Simpson page, known-variance z-tests in the p-hacking page, and a known σ in the confidence-interval page.
- The experiments show how a mechanism can produce an illusion; they are not empirical conclusions about real data.
- See [docs/methods.md](docs/methods.md) for assumptions, edge cases and references.

## Deploy (live)

Live app: <https://stat-illusions-lab.streamlit.app/>

This app is designed for Streamlit Community Cloud:

1. Push the repository to GitHub.
2. Create an app at [share.streamlit.io](https://share.streamlit.io).
3. Use `app.py` as the entry point and `requirements.txt` as the dependency file.
4. Add the live demo link near the top of this README (done).

## License

[MIT](LICENSE) © 2026 The stat-illusions-lab contributors
