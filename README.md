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

Project specification, a 24-item bilingual pilot (192 comparisons), validated
dataset records, an offline evaluation runner, and initial accuracy/order-bias
metrics are in place. Bilingual prompts, strict JSON parsing, and offline
recorded-response replay are also implemented. Dual-order human deferral and
risk-controlled threshold evaluation are available, together with isotonic
confidence calibration and calibration diagnostics. Real judge adapters and
human-readable reporting remain for later approved phases. A dependency-free
Ollama adapter is implemented and tested with simulated HTTP responses; it has
not yet been used for a real model run.

See:

- [Project specification](docs/project_spec.md)
- [Experiment protocol](docs/experiment_protocol.md)
- [Data schema](docs/data_schema.md)
- [Metric definitions](docs/metrics.md)
- [Judge adapter contract](docs/judge_adapter.md)
- [Local Ollama adapter](docs/local_ollama.md)

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

项目规格、包含 192 条比较记录的 24 项双语 Pilot、可验证的数据记录、
离线评估运行器，以及首批准确率和顺序偏差指标已经建立。真实 Judge
接入前所需的双语提示模板、严格 JSON 解析和离线记录重放也已实现。
双顺序人工转交和风险受控的阈值评估也已实现。真实 Judge 适配器、
单调置信度校准及其诊断指标也已实现。真实 Judge 适配器和人类可读报告
将在后续经确认的阶段中实现。项目已经实现无第三方依赖的 Ollama
适配器，并通过模拟 HTTP 响应完成测试，但尚未运行真实模型。

相关文档：

- [项目规格](docs/project_spec.md)
- [实验协议](docs/experiment_protocol.md)
- [数据格式](docs/data_schema.md)
- [指标定义](docs/metrics.md)
- [Judge 适配器规范](docs/judge_adapter.md)
- [本地 Ollama 适配器](docs/local_ollama.md)

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
```

## 许可证

MIT
