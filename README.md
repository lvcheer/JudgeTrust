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

## What is RAG? A potential use case

Retrieval-Augmented Generation (RAG) first retrieves relevant information from
a trusted knowledge base and then asks an LLM to answer using that information.

JudgeTrust does **not** currently implement a complete RAG system. The present
pilot starts after the retrieval and generation stages: its reference passages,
clean answers, and controlled variants were authored as experimental data. It
does not use an embedding model, vector database, retriever, or generator LLM.
The only real LLM evaluated in the completed pilot is `qwen2.5:14b`, acting as
the **judge** through local Ollama. Fake and recorded judges are infrastructure
tests rather than answer-generation models.

The distinction between a potential deployment and the current pilot is:

```text
Potential RAG deployment:
Knowledge base → Retriever → Generator LLM → Candidate answers
              → Judge LLM → JudgeTrust audit

Current controlled pilot:
Authored reference passage + controlled candidate answers
              → Qwen2.5 14B Judge → JudgeTrust audit
```

The controlled design isolates judge behaviour. If a complete RAG pipeline
were used, an observed error could also come from document chunking, retrieval,
or answer generation, making order, verbosity, style, and citation effects
harder to attribute to the judge itself.

As a conceptual application example, a university RAG assistant might retrieve
the following policy when a student asks when the library closes on Saturday:

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

In a future deployment, JudgeTrust would audit the automated evaluator used to
assess these RAG outputs. In the current repository, the same evaluation stage
is reproduced with controlled, RAG-like grounded question-answering examples.

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

## 什么是 RAG？一个潜在应用场景

RAG 是 Retrieval-Augmented Generation 的缩写，中文通常译为“检索增强
生成”。它先从可信知识库中检索与问题相关的材料，再让大模型依据这些
材料生成回答。

JudgeTrust **目前并没有实现完整的 RAG 系统**。当前 Pilot 从检索和生成
之后的阶段开始：参考材料、干净回答和受控变体均作为实验数据人工编写。
项目没有使用 embedding 模型、向量数据库、retriever 或 Generator LLM。
已完成 Pilot 中唯一真实运行的 LLM 是通过本地 Ollama 调用的
`qwen2.5:14b`，它只承担 **Judge** 角色。Fake Judge 和 Recorded Judge
用于测试基础设施，不是回答生成模型。

潜在部署与当前实验之间的区别是：

```text
潜在的完整 RAG 部署：
知识库 → Retriever → Generator LLM → 候选回答
      → Judge LLM → JudgeTrust 审计

当前受控 Pilot：
人工编写的参考材料 + 受控候选回答
      → Qwen2.5 14B Judge → JudgeTrust 审计
```

这种受控设计有助于隔离 Judge 自身的行为。如果直接使用完整 RAG 流程，
观察到的错误还可能来自文档切分、检索或回答生成，因而难以判断顺序、
冗长度、风格和引用效应是否真正来自 Judge。

作为概念性应用案例，当学生询问图书馆周六几点闭馆时，大学 RAG 咨询
助手可能检索到下面的规定：

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

在未来的真实部署中，JudgeTrust 可以审计用于评价这些 RAG 输出的自动
评委。当前仓库则通过受控、类似 RAG 的带参考材料问答案例复现这一评审
阶段。

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
