# 发布清单

这份清单把“本地项目”变成“可以发给别人看的 GitHub 开源项目”。建议按顺序完成。

## 1. 仓库标识

当前配置使用：

```text
jiezhou9/stat-illusions-lab
```

相关位置已经写入 README、`pyproject.toml` 和 `CITATION.cff`。如果你 fork 或改名，请同步更新：

- CI badge 的仓库地址；
- clone 命令；
- `pyproject.toml` 的 Homepage / Repository / Issues；
- `CITATION.cff` 的 `repository-code`。

## 2. 初始化 Git 仓库

如果当前目录还不是 Git 仓库：

```bash
git init
git branch -M main
git add .
git commit -m "feat: initial statistical illusions lab"
```

如果已经有仓库，直接提交即可。

建议仓库名：`stat-illusions-lab`。

## 3. 创建 GitHub 仓库

在 GitHub 新建空仓库，不要勾选自动生成 README、.gitignore 或 License（本地已经有了）。

```bash
git remote add origin https://github.com/jiezhou9/stat-illusions-lab.git
git push -u origin main
```

## 4. 配置仓库信息

- **Description**：`Interactive simulations that expose five common statistical illusions.`
- **Topics**：`statistics`, `statistics-education`, `data-visualization`, `simulation`, `streamlit`, `p-value`, `bayesian`, `causal-inference`, `reproducibility`
- **Social preview**：上传 `assets/banner.svg` 或它的 PNG 版本。
- **License**：确认 GitHub 识别为 MIT。
- **Actions**：确认 CI 在 push 后运行通过。

## 5. 部署 Demo

1. 打开 [share.streamlit.io](https://share.streamlit.io)；
2. 选择 “New app”；
3. Repository 选择刚推送的仓库；
4. Main file path 填 `app.py`；
5. 确认依赖文件是 `requirements.txt`；
6. 部署后测试首页、五个实验页和移动端；
7. 把线上地址写回 README 顶部，并替换 `?page=` 的本地示例。

## 6. 发布前检查

```bash
ruff check .
pytest
pytest --cov=stat_illusions --cov-report=term-missing
```

手动检查：

- [ ] 首页在 1440px 和 390px 宽度下都正常；
- [ ] 五个实验页都能通过左侧目录进入；
- [ ] `/?page=simpson` 等深链接能打开对应实验；
- [ ] 手机端左上角可以展开目录；
- [ ] 所有外部链接可访问；
- [ ] README 截图不是空白或过期版本；
- [ ] LICENSE 年份和署名正确；
- [ ] 没有把 `.venv`、`.dsh-acl-recovery`、临时截图目录提交进去。

## 7. 第一个 Release（可选）

```bash
git tag -a v0.1.0 -m "Statistical Illusions Lab v0.1.0"
git push origin v0.1.0
```

在 GitHub Releases 中粘贴更新说明，并附上首页截图。

## 8. 发布之后

- 把仓库链接加到简历、个人网站和求职材料；
- 在 README 顶部加 Demo 链接；
- 用 Issues 记录下一步实验，不要把所有想法塞进第一个版本；
- 如果收到统计解释方面的反馈，优先核对参考文献和模型假设，再改文案。
