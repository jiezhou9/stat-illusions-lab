# 方法与局限

这个仓库是**教学用模拟**，不是研究级统计软件。目标是把每个错觉的机制讲清楚，因此模型刻意保持简单、透明、可复现。下面记录每个实验的模型、假设和边界。

所有随机模拟使用 NumPy 的 `Generator`（PCG64），并通过显式 `seed` 参数控制随机性。相同参数与种子在**同一依赖环境**下会得到相同结果；NumPy 不保证跨版本的随机数流完全一致。

---

## 01 辛普森悖论

### 模型

设分层变量 `S ∈ {轻症, 重症}`，处理变量 `T ∈ {治疗, 对照}`，结局 `R ∈ {康复, 未康复}`。每个分层内的康复率为：

$$
p_{t,s} = P(R=1 \mid T=t, S=s)
$$

处理组中重症患者的比例为 $\pi_t = P(S=1 \mid T=t)$。整体康复率是分层率的加权平均：

$$
p_t = \pi_t p_{t,1} + (1-\pi_t) p_{t,0}
$$

当

$$
p_{1,1} > p_{0,1}, \quad p_{1,0} > p_{0,0}
$$

但

$$
\pi_1 p_{1,1} + (1-\pi_1) p_{1,0}
<
\pi_0 p_{0,1} + (1-\pi_0) p_{0,0}
$$

时，就出现了辛普森悖论。

### 默认参数

| 参数 | 治疗组 | 对照组 |
|------|--------|--------|
| 轻症康复率 | 92% | 85% |
| 重症康复率 | 62% | 50% |
| 重症患者占比 | 75% | 25% |

治疗组在两个分层内分别高出 7 和 12 个百分点，但整体康复率为 69.5%，低于对照组的 76.25%。

### 解释与局限

- 图中的数字是**期望率**，不是抽样结果；因此没有抽样误差和置信区间。
- “整体更差”描述的是这批混合人群的合并经验，不是治疗的因果效应。
- 要估计因果效应，需要明确因果问题、调整混杂变量，最好通过随机化保证组间可比。
- 分层不是万能的：如果存在未测量的混杂，或分层变量本身受处理影响，简单分层仍可能有偏。

### 参考文献

- Simpson, E. H. (1951). The Interpretation of Interaction in Contingency Tables.
- Pearl, J. (2009). *Causality*.

---

## 02 基础率谬误

### 模型

设 `D` 表示患病，`+` 表示检测阳性。已知：

- 患病率 $P(D)$；
- 灵敏度 $P(+ \mid D)$；
- 特异度 $P(- \mid \neg D)$。

阳性预测值（PPV）为：

$$
P(D \mid +) =
\frac{P(+ \mid D)P(D)}
{P(+ \mid D)P(D) + P(+ \mid \neg D)P(\neg D)}
$$

其中 $P(+ \mid \neg D) = 1 - \text{特异度}$。

### 自然频数

假设 1,000 人：

- 真阳性 $= 1000 \times P(D) \times \text{灵敏度}$
- 假阴性 $= 1000 \times P(D) \times (1-\text{灵敏度})$
- 假阳性 $= 1000 \times (1-P(D)) \times (1-\text{特异度})$
- 真阴性 $= 1000 \times (1-P(D)) \times \text{特异度}$

四类人数用最大余数法取整，保证总和为 1,000。图中的方块是示意，不表示真实个体顺序。PPV 和 NPV 用精确概率计算，不使用取整后的人数，避免小概率事件被四舍五入放大。

### 默认参数

患病率 1%、灵敏度 99%、特异度 95%：

$$
PPV = \frac{0.99 \times 0.01}{0.99 \times 0.01 + 0.05 \times 0.99}
= \frac{1}{6} \approx 16.7\%
$$

### 解释与局限

- 假设灵敏度、特异度在人群中固定，且检测结果只通过这两个参数与患病状态关联。
- 没有考虑检测的重复使用、不同亚组的准确率差异、谱偏倚（spectrum bias）和患病率估计的不确定性。
- PPV 会随患病率变化；把患病率调高，PPV 会显著上升。
- “检测准确率”是一个模糊说法，必须区分灵敏度、特异度、PPV 和总体准确率。

### 参考文献

- Gigerenzer, G., & Hoffrage, U. (1995). How to Improve Bayesian Reasoning Without Instruction.
- Kahneman, D., & Tversky, A. (1973). On the Psychology of Prediction.

---

## 03 p 值狩猎

### 模型

每次 A/A 实验从同一标准正态分布独立抽取两组：

$$
X_i \sim N(0,1), \quad Y_i \sim N(0,1), \quad i=1,\dots,n
$$

比较均值差：

$$
z = \frac{\bar{Y}-\bar{X}}{\sqrt{2/n}}
$$

双侧 p 值为：

$$
p = 2\left(1-\Phi(|z|)\right) = \operatorname{erfc}\left(\frac{|z|}{\sqrt{2}}\right)
$$

零假设为真时，p 值服从 Uniform(0,1)。因此

$$
P(p < \alpha) = \alpha
$$

做 $m$ 次独立检验时，至少出现一次假阳性的族错误率为：

$$
\mathrm{FWER} = 1-(1-\alpha)^m
$$

### 默认参数

- 100 次实验；
- 每组 30 个样本；
- $\alpha=0.05$。

此时预期假阳性为 5 次，FWER 约为 99.4%。

### 解释与局限

- 这里使用**已知方差的双侧 z 检验**，而不是 t 检验；样本量较小时，t 检验的尾部会略厚。
- 假设各次检验独立。真实研究中的检验往往相关，FWER 会因相关结构而变化。
- 实验只模拟零假设；它展示的是假阳性，不是统计功效（power）。
- 图下方的“最小 p 值”是连续检验后的事后观察，不是预先设定的停止规则。真实研究中的“看几次，显著就停”会进一步扭曲推断。
- p 值不是“零假设为真的概率”，也不是“效应很大的概率”。

### 参考文献

- Wasserstein, R. L., & Lazar, N. A. (2016). The ASA Statement on p-Values.
- Ioannidis, J. P. A. (2005). Why Most Published Research Findings Are False.

---

## 04 回归均值

### 模型

潜在能力：

$$
\theta_i \sim N(0,1)
$$

两次测量：

$$
Y_{i1} = \theta_i + \varepsilon_{i1}, \quad
Y_{i2} = \theta_i + \varepsilon_{i2}, \quad
\varepsilon_{ij} \sim N(0,\sigma^2)
$$

两次测量的相关系数为：

$$
\rho = \frac{1}{1+\sigma^2}
$$

按第一次成绩选择前 $q$ 比例的人。对于双变量正态分布：

$$
E[Y_2 \mid Y_1=y] = \mu_2 + \rho \frac{\sigma_2}{\sigma_1}(y-\mu_1)
$$

在本模型中 $\mu_1=\mu_2=0$，$\sigma_1=\sigma_2=\sqrt{1+\sigma^2}$，所以：

$$
E[Y_2 \mid Y_1=y] = \rho y
$$

选中组的第一次均值越高，第二次期望均值就越接近总体均值。回落幅度约为 $(1-\rho)\bar{Y}_{1,\text{selected}}$。

### 默认参数

- 500 人；
- 测量噪声 $\sigma=1$；
- 选择前 10%。

此时 $\rho=0.5$，理论上第二次均值约为第一次均值的一半。图中实际值会因随机抽样略有波动。

### 解释与局限

- 模型假设能力分布和测量噪声都是正态、方差齐性、独立同分布。
- “回归”是统计现象，不等于“退步”或“干预无效”。
- 如果选择依据本身包含测量误差，极端组必然包含较多正向误差；这是回归均值的核心机制。
- 真实评估中应设置对照组，或使用多期测量和测量误差模型，而不是比较极端组的前后变化。
- 噪声为 0 时 $\rho=1$，不会出现回归；这可以作为边界检查。

### 参考文献

- Barnett, A. G., van der Pols, J. C., & Dobson, A. J. (2005). Regression to the Mean: What It Is and How to Deal with It.
- Kahneman, D. (2011). *Thinking, Fast and Slow*.

---

## 05 置信区间

### 模型

假设 $X_1,\dots,X_n \sim N(\mu,\sigma^2)$，且 $\sigma$ 已知。样本均值：

$$
\bar{X} \sim N\left(\mu,\frac{\sigma^2}{n}\right)
$$

置信水平 $1-\alpha$ 下的区间为：

$$
\bar{X} \pm z_{1-\alpha/2}\frac{\sigma}{\sqrt{n}}
$$

在重复抽样中，区间覆盖 $\mu$ 的概率恰好为 $1-\alpha$：

$$
P\left(\bar{X}-z_{1-\alpha/2}\frac{\sigma}{\sqrt{n}}
\le \mu \le
\bar{X}+z_{1-\alpha/2}\frac{\sigma}{\sqrt{n}}\right)
= 1-\alpha
$$

### 默认参数

- 100 次重复抽样；
- 每次样本量 30；
- 置信水平 95%；
- 真实均值 0，$\sigma=1$。

### 解释与局限

- 这里假设 $\sigma$ 已知，因此使用 z 区间；实际分析中 $\sigma$ 通常未知，应使用 t 区间。
- 覆盖率是**长期频率**：重复同样的抽样和构造方法，约 95% 的区间会覆盖真值。
- 对某个已经计算出的区间，不能说“参数有 95% 的概率落在里面”（在频率派框架下，参数被视为固定值）。
- 区间覆盖率和区间宽度是两件事；提高置信水平会得到更宽的区间。
- 该模拟假设正态分布和独立抽样，没有处理聚类、加权、非响应或模型选择后的不确定性。

### 参考文献

- Morey, R. D., Hoekstra, R., Rouder, J. N., Lee, M. D., & Wagenmakers, E.-J. (2016). The Fallacy of Placing Confidence in Confidence Intervals.
- Greenland, S., et al. (2016). Statistical Tests, P Values, Confidence Intervals, and Power: A Guide to Misinterpretations.

---

## 通用局限

- 这些实验是教学演示，不对应任何真实数据集或临床结论。
- 所有模型都省略了真实研究中重要的复杂性：抽样设计、缺失数据、测量误差结构、模型选择、研究者自由度等。
- 图中的“显著”“覆盖”“回落”等词，均按各节明确的模型定义使用。
- 如果要在研究或生产中使用类似方法，请咨询领域专家，并使用经过验证的统计软件与预注册分析方案。
