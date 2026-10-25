# 参与贡献

感谢你愿意改进这个项目。无论是统计解释、文案、可视化还是工程实现，都欢迎。

## 开发环境

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -e ".[dev]"
streamlit run app.py
```

## 提交之前

```bash
ruff check .
pytest
```

如果你修改了模拟逻辑，请同时补充或更新 `tests/test_simulations.py` 中的测试。如果你修改了页面结构，请确认 `tests/test_app.py` 仍然通过。

## 代码结构

- `src/stat_illusions/simulations.py`：纯模拟函数。不要在这里导入 Streamlit。
- `src/stat_illusions/plots.py`：Plotly 图表。只负责把结果画出来。
- `src/stat_illusions/content.py`：文案、实验元数据和参考文献。
- `src/stat_illusions/app.py`：页面布局和控件。
- `tests/`：统计性质测试和页面冒烟测试。

## 新增一个实验

1. 在 `simulations.py` 中写一个纯函数，接受显式参数和随机种子，返回 dataclass 或 DataFrame。
2. 在 `tests/test_simulations.py` 中测试正常路径、边界条件和可复现性。
3. 在 `plots.py` 中增加图表函数，保持现有配色和排版。
4. 在 `content.py` 中增加 `Module`、解释文案和至少两条参考文献。
5. 在 `app.py` 中增加页面函数，并加入 `PAGES` 与 `NAV_ITEMS`。
6. 更新 README 的实验表格和测试说明。

## 统计解释的准确性

如果你认为某个解释不严谨，请提供：

- 具体是哪一句、哪个实验；
- 为什么它不准确；
- 建议的替代表述；
- 可核查的参考文献或推导。

欢迎直接开 Issue，不必先写完整 PR。

## 提交信息

建议使用清晰的动词开头，例如：

```text
feat: add Bayesian A/B test experiment
fix: correct PPV rounding in base-rate grid
docs: clarify confidence-interval interpretation
test: cover zero-noise regression case
```

## 行为准则

请保持尊重、具体和就事论事。这个项目的目标是帮助人们更准确地理解统计，而不是赢得争论。
