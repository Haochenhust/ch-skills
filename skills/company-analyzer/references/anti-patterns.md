# Anti-Patterns (The Negative List)

LLMs default to consulting-report voice because training data is full of it. The point of this file is to name each failure mode concretely and show the rewrite.

## 1. The Dry Chronicle

A timeline in paragraph form. No stakes, no choices, no people.

**❌ Bad**
> 字节跳动成立于 2012 年。2016 年推出抖音。2018 年进入美国市场，改名 TikTok。2020 年面临美国政府审查。2023 年 TikTok 在美用户突破 1.5 亿。

**✅ Better**
> 2016 年 9 月，张一鸣在办公室看到今日头条的数据曲线开始走平。同一周，他内部宣布推出抖音——短视频是他已经观察了两年的"未完成的移动形态"。真正的赌注不是短视频，是 One App Per Country 的全球复制策略：抖音是国内的抖音、TikTok 是海外的抖音，两套团队、两套增长，背后共享同一套算法基建。这个决定让字节在 2018 年成为第一家从中国公司起步、在美国主流市场站稳的互联网产品，也为 2020 年的政治风暴埋了伏笔。

## 2. Consulting Filler

Words that sound like insight but encode nothing. Usually signal the writer didn't have a specific claim.

**Banned vocabulary** (English and Chinese, add freely):
- 赋能 / 抓手 / 闭环 / 打造 / 生态位 / 护城河 (used as noun-drop) / 降本增效 / 全链路 / 深度赋能
- synergize / leverage / holistic / empower / best-in-class / next-generation / mission-critical / end-to-end

**❌ Bad**
> 通过打造从数据到算法到场景的全链路闭环，赋能品牌商家深度增长。

**✅ Better**
> 字节为品牌商家提供了一条从抖音投流到 TikTok Shop 成交的完整链路，把过去需要三家公司（投放、导流、成交）做的事收进了一个系统。商家的真实好处是单次转化成本从 2022 年的约 ¥45 降到 2024 年的 ¥28（公开财报 + 亿邦智库数据），代价是进入平台封闭数据系统，换出数据可移植性。

## 2b. 自造中英夹杂术语 (★ 新增，优先级最高)

把英文商业术语原封不动嵌进中文，看起来"专业"其实是偷懒——没有把概念翻译成读者熟悉的中文来表达，也暴露了写作者没真正理解概念.

**中文产业写作不接受**的自造夹杂术语（段落里作为概念名出现时）：

- **moat** → 护城河
- **process power** → 工艺积累 / 工程化 know-how
- **capital allocation** → 资本配置 / 把钱花到哪里去
- **unit economics** → 单位经济 / 单客户算得清账吗
- **go-to-market** → 切入市场的方式 / 渠道打法
- **stickiness / sticky** → 黏性 / 客户转不动
- **counter-positioning** → 反向卡位 / 错位竞争
- **switching cost** → 切换成本 (这个已经被中文业界吸收，可用)
- **network effect** → 网络效应 (同样可用)
- **scale economies** → 规模经济 (同样可用)
- **LTV / CAC** → 可保留（已经是中文业界标配缩写）
- **TAM / SAM / SOM** → 市场规模 / 可触达 / 可服务
- **churn** → 流失率
- **flywheel** → 飞轮效应
- **land and expand** → 先锚定再扩张

判断标准：这个英文词在《晚点 LatePost》、《财新》、《第一财经》的文章里日常出现吗？如果没有，必须翻译成中文说法.

**❌ Bad（iteration-1 自己的原话）**
> 它没有教科书定义的强护城河，真正能 hold 住的是"规模经济 + process power"的弱混合体.

**✅ Better**
> 它没有教科书里那种硬护城河，真正撑得住的是"国内最大规模 + 多年工程化积累"的弱组合.

**❌ Bad**
> 大族的 capital allocation 历史显示管理层更像 deal-maker.

**✅ Better**
> 过去十年大族把钱花去哪里——连续收购、两次剥离子公司、一次卖资产套现——更像是在做交易而不是在做经营.

**❌ Bad**
> 这是它真正的 moat，但 moat width 只覆盖消费电子这一块.

**✅ Better**
> 这是它真正的护城河，但这条河只护得住消费电子这块地；走出这块地，同样的工程化积累并不自动变成壁垒.

## 3. Template Boilerplate (SWOT / Porter / PEST)

Using templates as literal section headers turns the report into a fill-in-the-blanks exercise.

**❌ Bad** (section headers):
> ## SWOT Analysis
> ### Strengths
> ### Weaknesses
> ### Opportunities
> ### Threats

**✅ Better**: use the *thinking* in those frameworks inside flowing prose. If your piece would be stronger with explicit substitution threat, write a paragraph titled "What could replace them" — not "Threats".

## 4. Financial Filings Prose

Pasting 10-K numbers into sentences without interpretation.

**❌ Bad**
> 2024 年公司营收为 1521.7 亿美元，同比增长 10.1%。毛利率 51.5%，环比提升 0.3 个百分点。经营利润 338.4 亿美元。自由现金流 230 亿美元。

**✅ Better**
> 2024 年毛利率 51.5%，比 5 年前高出 8 个百分点，几乎全部来自云业务占比上升——这意味着公司已经不再是那个以广告为主的生意了，尽管广告还占收入的六成。关键看 2025 年 AI 基建资本开支（年化约 800 亿美元）能否在 3 年内变出对应的云收入，否则这段毛利率扩张故事会反转。

## 5. Neutral Posture ("骑墙")

Balanced-looking conclusions that refuse to say what the writer actually thinks.

**❌ Bad**
> 综上所述，公司既面临机遇也面临挑战。如果能在未来几年应对好竞争与监管压力，有望保持增长；反之则可能承压。

**✅ Better**
> 我会在个人账户里建一个 5% 仓位，但不会更大。理由：商业模式已经验证（连续 8 个季度 FCF 正且扩大），管理层在 2023 年那次裁员做得干净（15% 一次性完成，没有拖泥带水），但监管面的尾部风险还没消化完——如果明年不出新的出海限制，我会加仓；如果出，这个仓位就当学费。

## 6. "综上所述" / "In Conclusion" Summary

If the piece needs a TL;DR paragraph to hold together, the piece didn't cohere in the first place. End on the judgment, not on a recap.

**❌ Bad**
> 综上所述，本报告分析了公司的历史、业务模式、竞争格局和财务状况，结论如下：...

**✅ Better**: let the final section carry the judgment. Don't re-preview what you already wrote.

## 7. Abstract-First Writing

Leading with abstract claims and never landing in specific scenes/numbers.

**❌ Bad**
> 创始人是一位有远见和执行力的企业家，带领公司穿越多个周期，建立了强大的文化。

**✅ Better**
> 2015 年 Q4 那次全员信里，他写了一段话："我们不是在追风口，我们是风口。" 当时公司刚亏了一个季度，员工股票被普遍质疑。这段话后来被印在办公室墙上——不是因为它漂亮，是因为接下来两年他真的把话做到了：一年后公司 IPO，两年后股价翻了三倍。这是"远见"和"执行力"的一个具体含义。

## 8. Biographical Filler

Detail about the founder that doesn't connect to a company decision.

**❌ Bad**
> 张一鸣出生于 1983 年福建龙岩，从小喜欢读书，南开大学软件工程专业毕业。

**✅ Better**: include biographical detail only when it explains a company choice. The Fujian origin + non-first-tier school might actually matter for understanding why 字节 hired aggressively from non-Tsinghua/Peking schools early on. Tie it to a decision.

---

## The General Principle

LLMs regress toward mean prose when unconstrained. The way to pull them off the mean is to show the ditch and the road:

- **Name the failure mode concretely** ("don't write `赋能`"), not abstractly ("be specific").
- **Pair each `don't` with a rewrite** so the model knows what good looks like.
- **Keep the list short enough to remember** — ~8 items max, not 40.
