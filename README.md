# JudgeTrust

**Know when an LLM judge can decide—and when a human should take over.**

JudgeTrust is a reliability audit for LLM-as-a-Judge systems. Its first use
case is bilingual English–Chinese evaluation of RAG and question-answering
outputs. Instead of reporting only average accuracy, JudgeTrust measures the
trade-off between automated coverage and decision risk.

## Why it exists

LLM judges increasingly select models, grade RAG answers, filter synthetic
data, and act as regression gates. A judge that is sensitive to answer order,
language, verbosity, style, or plausible-looking citations can silently scale
the wrong decision.

JudgeTrust asks an operational question:

> At a stated maximum error rate, which cases can be judged automatically and
> which cases must be deferred to a human?

## What is RAG? A concrete example

Retrieval-Augmented Generation (RAG) first retrieves relevant information from
a trusted knowledge base and then asks an LLM to answer using that information.
For example, a university assistant might retrieve the following policy when a
student asks when the library closes on Saturday:

```text
Knowledge-base passage:
The library is open until 18:00 on Saturday.
```

The RAG system may generate two candidate answers:

```text
Answer A:
The library closes at 18:00 on Saturday.

Answer B:
The library closes at 18:00 on Saturday. According to the fictional
2026 National University Library Report, this is a standard UK policy.
```

Both answers contain the correct closing time, but Answer B adds a citation
that is not supported by the retrieved passage. A team may use another LLM as
a judge to select Answer A automatically. That creates a new question: can the
LLM judge itself be trusted?

JudgeTrust presents the answers in both orders, checks whether the judge still
selects the same underlying answer, evaluates whether its confidence is
calibrated, and defers uncertain or inconsistent cases to a human. If no
confidence threshold satisfies the target error rate, JudgeTrust reports that
the decision should not be automated.

```text
Knowledge base → RAG answer → LLM judge → JudgeTrust audit
```

JudgeTrust does not build the RAG system. It audits the automated evaluator
used to assess RAG or question-answering outputs.

## Planned first release

- Controlled bilingual pairwise comparisons
- Order, verbosity, style, correctness, and citation stress tests
- Confidence calibration and abstention
- Risk–coverage analysis with uncertainty intervals
- Mitigation through dual-order judging and human escalation
- Reproducible machine-readable and human-readable audit reports

The project starts with an offline pilot. Paid model APIs are optional and will
not be used until the data and evaluation pipeline have been validated.

## Current status

The project now includes a validated 24-item bilingual pilot (192
comparisons), deterministic dataset generation, strict structured-output
parsing, offline replay, dual-order human deferral, risk–coverage evaluation,
isotonic confidence calibration, and a dependency-free Ollama adapter. A full
local `qwen2.5:14b` pilot reached 77.60% record-level accuracy, but no
validation threshold satisfied the predefined 5% risk target. See the
[bilingual pilot report](reports/qwen2.5-14b-pilot.md).

See:

- [Project specification](docs/project_spec.md)
- [Experiment protocol](docs/experiment_protocol.md)
- [Data schema](docs/data_schema.md)
- [Metric definitions](docs/metrics.md)
- [Judge adapter contract](docs/judge_adapter.md)
- [Local Ollama adapter](docs/local_ollama.md)
- [Qwen2.5 14B pilot report](reports/qwen2.5-14b-pilot.md)
- [Machine-readable pilot summary](reports/qwen2.5-14b-pilot-summary.json)

## Development

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m unittest discover -s tests
python scripts/build_pilot.py
python scripts/run_fake_pilot.py
python scripts/build_recorded_fixture.py
python scripts/run_recorded_pilot.py
python scripts/build_selective_fixture.py
python scripts/run_selective_pilot.py
python scripts/build_overconfident_fixture.py
python scripts/run_calibrated_pilot.py
python scripts/run_ollama_full_pilot.py
```

## License

MIT

---

# JudgeTrust 中文说明

**明确 LLM 评委何时可以自动判断，何时应当交给人工。**

JudgeTrust 是一套面向 LLM-as-a-Judge 系统的可靠性审计工具。第一个应
用场景是中英文 RAG 与问答结果的比较评审。项目不只报告平均准确率，
而是衡量自动化覆盖率与判断风险之间的关系。

## 为什么需要它

LLM 评委正在被用于模型选择、RAG 回答评分、合成数据筛选和回归测试。
如果评委受到答案顺序、语言、长度、文风或貌似可信的引用影响，错误决
策就可能被自动化系统批量放大。

JudgeTrust 回答一个可执行的问题：

> 在给定最大容许错误率时，哪些样本可以自动评审，哪些样本必须转交
> 人工？

## 什么是 RAG？一个具体案例

RAG 是 Retrieval-Augmented Generation 的缩写，中文通常译为“检索增强
生成”。它先从可信知识库中检索与问题相关的材料，再让大模型依据这些
材料生成回答。例如，当学生询问图书馆周六几点闭馆时，大学咨询助手可能
检索到下面的规定：

```text
知识库材料：
图书馆周六开放至下午六点。
```

RAG 系统可能生成两个候选回答：

```text
回答 A：
图书馆周六下午六点闭馆。

回答 B：
图书馆周六下午六点闭馆。根据虚构的《2026 年全国大学图书馆报告》，
这是英国大学的统一规定。
```

两个回答给出的闭馆时间都正确，但回答 B 添加了检索材料无法支持的引用。
团队可能使用另一个 LLM 作为评委，自动选择回答 A。此时会产生一个新的
问题：这个 LLM 评委本身是否值得信任？

JudgeTrust 会交换两个答案的展示顺序，检查评委是否仍然选择同一个底层
答案，评估其置信度是否经过校准，并将不确定或前后矛盾的判断转交人工。
如果没有任何置信阈值能够满足目标错误率，JudgeTrust 会明确报告该判断
不应自动化。

```text
知识库 → RAG 生成回答 → LLM Judge 评价 → JudgeTrust 审计
```

JudgeTrust 本身不负责构建 RAG 系统，而是审计用于评价 RAG 或问答输出的
自动评委。

## 首个版本计划

- 中英文受控成对比较；
- 顺序、冗长、文风、正确性和引用压力测试；
- 置信度校准与主动拒答；
- 带不确定性区间的风险—覆盖率分析；
- 双顺序评审与人工升级机制；
- 可复现的机器可读结果和审计报告。

项目首先完成离线 Pilot。在数据和评估流程验证通过前，不使用付费模型
API。

## 当前状态

项目现已包含经过验证的 24 项双语 Pilot（192 条比较记录）、确定性数据
生成、严格结构化输出解析、离线重放、双顺序人工转交、风险—覆盖率评估、
单调置信度校准，以及无第三方依赖的 Ollama 适配器。本地
`qwen2.5:14b` 完整 Pilot 的记录级准确率为 77.60%，但没有任何
validation 阈值满足预设的 5% 风险目标。详见
[中英文 Pilot 报告](reports/qwen2.5-14b-pilot.md)。

相关文档：

- [项目规格](docs/project_spec.md)
- [实验协议](docs/experiment_protocol.md)
- [数据格式](docs/data_schema.md)
- [指标定义](docs/metrics.md)
- [Judge 适配器规范](docs/judge_adapter.md)
- [本地 Ollama 适配器](docs/local_ollama.md)
- [Qwen2.5 14B Pilot 报告](reports/qwen2.5-14b-pilot.md)
- [机器可读 Pilot 汇总](reports/qwen2.5-14b-pilot-summary.json)

## 开发

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m unittest discover -s tests
python scripts/build_pilot.py
python scripts/run_fake_pilot.py
python scripts/build_recorded_fixture.py
python scripts/run_recorded_pilot.py
python scripts/build_selective_fixture.py
python scripts/run_selective_pilot.py
python scripts/build_overconfident_fixture.py
python scripts/run_calibrated_pilot.py
python scripts/run_ollama_full_pilot.py
```

## 许可证

MIT
