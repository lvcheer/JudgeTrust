# Qwen2.5 14B Bilingual Judge Reliability Pilot

## Summary

JudgeTrust evaluated `qwen2.5:14b` as a local LLM judge on 192 controlled
English–Chinese pairwise comparisons. The model achieved 77.60% record-level
accuracy and was perfect on explicit correctness degradations, but performance
fell to 50.00% on verbosity-only comparisons and 75.00% on unsupported
citations. English accuracy exceeded Chinese accuracy by 11.46 percentage
points. Dual-order adjudication deferred 25 of 96 underlying pairs to a human,
yet the 71 remaining automated decisions still contained eight errors.

The formal selective audit did not identify a threshold meeting the target
error rate of 5%. On the validation split, the only available calibrated
threshold automated 17 of 24 pairs, made three errors, and produced an observed
risk of 17.65% with a one-sided 95% Wilson upper bound of 36.90%. The correct
operational conclusion is therefore `insufficient_evidence`: this judge should
not be used for unsupervised automated decisions under the stated risk target.

## Experimental setup

The pilot comprised 24 base items, evenly divided between English and Chinese
and among factual question answering, summarisation, and instruction following.
Each base item produced correctness, verbosity-only, style-only, and
unsupported-citation variants. Every comparison was evaluated in both original
and swapped A/B orders, yielding 192 model calls and 96 underlying pairs.

The experiment used the local Ollama model `qwen2.5:14b` in Q4_K_M
quantisation. Generation was non-streaming with temperature zero and seed zero.
The v2 run used a JSON Schema that constrained winner labels, reason codes,
scores, confidence, and required fields. JudgeTrust independently applied its
strict parser after generation. The dataset was processed in a fixed random
order with seed `20260923`. The complete run took 1,396 seconds, approximately
23 minutes and 16 seconds, and produced no connection or schema failures.

An earlier v1 attempt requested generic JSON but not a full schema. It stopped
after 76 records when the model returned `instruction_following` instead of the
allowed reason code `instruction`. Those partial outputs were retained locally
but were not mixed with the v2 experiment. The complete v2 run restarted from
the beginning under one consistent configuration.

## Record-level results

Table 1 reports descriptive accuracy across all 192 records. These values
describe observed behaviour but do not constitute a risk guarantee.

| Group | Records | Accuracy |
| --- | ---: | ---: |
| Overall | 192 | 77.60% |
| English | 96 | 83.33% |
| Chinese | 96 | 71.88% |
| Factual QA | 64 | 76.56% |
| Instruction following | 64 | 81.25% |
| Summarisation | 64 | 75.00% |

The perturbation analysis revealed a sharp separation between explicit errors
and preference-sensitive comparisons.

| Perturbation | Records | Accuracy |
| --- | ---: | ---: |
| Correctness degradation | 48 | 100.00% |
| Style only | 48 | 85.42% |
| Unsupported citation | 48 | 75.00% |
| Verbosity only | 48 | 50.00% |

The perfect result on correctness degradation shows that the model readily
identified direct contradictions in this pilot. The verbosity result is more
concerning: because the clean and longer answers were designed to be
substantively equivalent, chance-level accuracy indicates a systematic
tendency to prefer one answer rather than return `tie`. Unsupported citations
also remained difficult, despite the prompt explicitly requiring the judge to
check whether citations were supported.

## Dual-order adjudication

The model gave the same underlying decision in both A/B orders for 71 of 96
pairs. JudgeTrust deferred the other 25 pairs to a human. This mitigation
reduced exposure to order-sensitive decisions but did not make the retained
set safe: eight of the 71 automated decisions were wrong, corresponding to an
observed selective risk of 11.27%.

| Pair group | Coverage | Errors among automated pairs | Observed risk |
| --- | ---: | ---: | ---: |
| Overall | 73.96% | 8 | 11.27% |
| English | 79.17% | 3 | 7.89% |
| Chinese | 68.75% | 5 | 15.15% |
| Correctness degradation | 100.00% | 0 | 0.00% |
| Style only | 83.33% | 1 | 5.00% |
| Unsupported citation | 70.83% | 2 | 11.76% |
| Verbosity only | 41.67% | 5 | 50.00% |

These findings show why order consistency should be treated as a necessary
diagnostic rather than evidence of correctness. In particular, ten
verbosity-only pairs passed the consistency check, but five of those decisions
were still wrong.

## Calibration and selective-risk decision

Calibration, validation, and test base items were separated before evaluation.
Only 17 of the 24 calibration pairs remained eligible after dual-order
adjudication, and all 17 happened to be correct. Isotonic calibration therefore
mapped their confidence to 1.0, reducing calibration-set Brier score and ECE to
zero. This apparent improvement did not generalise: at the resulting validation
threshold of 1.0, 17 of 24 validation pairs were automated and three were
wrong.

| Validation quantity | Result |
| --- | ---: |
| Automated pairs | 17 / 24 |
| Coverage | 70.83% |
| Errors | 3 |
| Observed selective risk | 17.65% |
| One-sided 95% Wilson upper bound | 36.90% |

No validation threshold met the predefined 5% target. JudgeTrust therefore did
not select a threshold and did not issue a formal test-set risk estimate. The
audit status was `insufficient_evidence`, which in this case reflects both
limited sample size and a validation error rate already well above the target.

## Practical interpretation

Qwen2.5 14B was dependable for simple, explicit factual degradations in this
pilot, but reliability did not transfer to all judge tasks. The model was
particularly vulnerable when two answers conveyed the same content with
different length, and it inconsistently penalised unsupported citations. Its
performance was also lower in Chinese than in English. A production system
could use dual-order disagreement as one trigger for human review, but it
should not treat agreement or model confidence as sufficient grounds for
automatic acceptance.

The operational recommendation is to keep human review enabled for this model
and task distribution. If automation is required, it should initially be
restricted to a separately validated narrow slice, such as explicit
correctness degradations, and reassessed on a substantially larger held-out
dataset before deployment.

## Limitations

This is a software and experimental pilot rather than a definitive model
benchmark. The 24 base items were authored for controlled testing and have not
yet undergone independent double annotation. The study evaluated one model,
one quantisation, one prompt, and one local inference configuration. The
calibration and validation splits were small, and isotonic calibration was
unstable because every eligible calibration decision happened to be correct.
The reported Wilson bounds treat pair decisions as Bernoulli observations and
do not yet account for clustering of four perturbations within each base item;
a full study should use base-item cluster bootstrap intervals. Finally,
style-only and verbosity-only gold ties depend on the study's controlled-design
assumption that the altered answers are substantively equivalent.

## Reproducibility and data policy

The dataset, generation scripts, strict result schema, evaluation metrics, and
full-run script are version controlled. Raw local model predictions remain in
the ignored `results/` directory and are not published by default. The public
repository includes only this aggregate report and a machine-readable summary,
preventing accidental publication of local execution artifacts while retaining
the main findings.

---

# Qwen2.5 14B 双语 Judge 可靠性 Pilot

## 摘要

JudgeTrust 使用 192 条受控中英文成对比较，对本地运行的
`qwen2.5:14b` 进行了 LLM Judge 可靠性评估。模型的记录级总体准确率为
77.60%，对明确正确性下降的识别率达到 100%，但在仅增加冗长度的比较中
准确率只有 50.00%，在无依据引用比较中为 75.00%。英文准确率比中文高
11.46 个百分点。双顺序裁决将 96 个底层 pair 中的 25 个转交人工，但其余
71 个自动判断中仍有 8 个错误。

正式选择性风险审计没有找到满足 5% 目标错误率的阈值。在 validation
分区中，唯一可用的校准阈值自动处理了 24 个 pair 中的 17 个，其中出现
3 个错误；观察风险为 17.65%，单侧 95% Wilson 上界为 36.90%。因此，
正确的操作结论是 `insufficient_evidence`：在当前风险目标下，不应让该
Judge 无人工监督地自动决策。

## 实验设置

Pilot 包含 24 个基础样本，中英文各占一半，并均衡覆盖事实问答、摘要和
指令遵循。每个基础样本构造正确性下降、仅增加冗长度、仅改变风格和加入
无依据引用四类变体。每个比较同时采用原始和交换后的 A/B 顺序，因此共
产生 192 次模型调用和 96 个底层 pair。

实验通过 Ollama 本地运行 Q4_K_M 量化的 `qwen2.5:14b`。生成设置为
非流式、temperature 为 0、seed 为 0。完整 v2 运行使用 JSON Schema
约束 winner、reason code、分数、置信度和必填字段，生成后仍由
JudgeTrust 的严格解析器独立验证。数据按照固定随机种子 `20260923`
排序。完整运行耗时 1,396 秒，约 23 分 16 秒，没有出现连接或 schema
错误。

此前的 v1 尝试只要求普通 JSON，没有使用完整 schema。运行到 76 条时，
模型返回了不在允许枚举中的 `instruction_following`，而不是
`instruction`，因此系统按规则停止。这些局部结果只保留在本地，没有与
v2 数据混合；完整 v2 实验在统一配置下从头重新运行。

## 记录级结果

下表给出全部 192 条记录上的描述性准确率。这些数字用于理解模型行为，
不构成风险保证。

| 分组 | 记录数 | 准确率 |
| --- | ---: | ---: |
| 总体 | 192 | 77.60% |
| 英文 | 96 | 83.33% |
| 中文 | 96 | 71.88% |
| 事实问答 | 64 | 76.56% |
| 指令遵循 | 64 | 81.25% |
| 摘要 | 64 | 75.00% |

四类扰动之间存在明显差异。

| 扰动类型 | 记录数 | 准确率 |
| --- | ---: | ---: |
| 正确性下降 | 48 | 100.00% |
| 仅改变风格 | 48 | 85.42% |
| 无依据引用 | 48 | 75.00% |
| 仅增加冗长度 | 48 | 50.00% |

正确性下降上的满分表明，模型能够识别 Pilot 中的直接事实矛盾。相比之
下，verbosity-only 准确率更值得警惕：干净回答和较长回答被设计为实质
内容相同，接近随机水平的准确率说明模型经常偏好其中一个答案，而不是
给出 `tie`。尽管 Prompt 明确要求检查引用是否有依据，模型对无依据引用
的惩罚也不稳定。

## 双顺序裁决

在 96 个 pair 中，模型有 71 个在原始与交换顺序下选择了相同的底层
答案，JudgeTrust 将另外 25 个转交人工。这一措施减少了顺序敏感判断，
但没有使保留结果达到安全水平：71 个自动判断中仍有 8 个错误，观察
selective risk 为 11.27%。

| Pair 分组 | 覆盖率 | 自动判断中的错误 | 观察风险 |
| --- | ---: | ---: | ---: |
| 总体 | 73.96% | 8 | 11.27% |
| 英文 | 79.17% | 3 | 7.89% |
| 中文 | 68.75% | 5 | 15.15% |
| 正确性下降 | 100.00% | 0 | 0.00% |
| 仅改变风格 | 83.33% | 1 | 5.00% |
| 无依据引用 | 70.83% | 2 | 11.76% |
| 仅增加冗长度 | 41.67% | 5 | 50.00% |

这些结果说明，顺序一致性应该被视为必要的诊断条件，而不是判断正确的
证据。尤其是在 10 个通过一致性检查的 verbosity-only pair 中，仍有
5 个判断错误。

## 校准与选择性风险结论

实验在评估前按照基础样本划分 calibration、validation 和 test。
双顺序裁决后，24 个 calibration pair 中只有 17 个仍可自动判断，而且
这 17 个恰好全部正确。因此 isotonic calibration 将其置信度映射为
1.0，使 calibration 分区上的 Brier score 和 ECE 都降至零。然而，
这种表面改善没有推广到 validation：在校准后阈值 1.0 下，系统自动
处理了 24 个 validation pair 中的 17 个，其中 3 个错误。

| Validation 指标 | 结果 |
| --- | ---: |
| 自动判断 | 17 / 24 |
| 覆盖率 | 70.83% |
| 错误数 | 3 |
| 观察 selective risk | 17.65% |
| 单侧 95% Wilson 上界 | 36.90% |

没有任何 validation 阈值满足预设的 5% 目标。因此 JudgeTrust 没有选择
阈值，也没有给出正式的 test 风险估计。审计状态为
`insufficient_evidence`。在本实验中，这不仅反映了样本量较小，也反映
了 validation 观察错误率本身已经明显高于目标。

## 实际解释

在本 Pilot 中，Qwen2.5 14B 对简单、明确的事实错误较为可靠，但这种
表现没有推广到所有 Judge 任务。当两个回答内容相同但长度不同时，模型
尤其容易产生偏好；它对无依据引用的处理也不一致。中文表现低于英文。
生产系统可以将双顺序冲突作为转人工的触发条件之一，但不能把顺序一致
或模型自身置信度当作自动接受的充分依据。

实际建议是：在当前模型和任务分布下继续保留人工复核。如果确实需要
自动化，应先把范围限制在经过单独验证的狭窄场景，例如明确的正确性
下降，并在更大的独立留出数据集上重新评估后再考虑部署。

## 局限

本研究是软件与实验 Pilot，而不是最终模型基准。24 个基础样本为受控
实验人工编写，尚未进行独立双人标注。实验只覆盖一个模型、一个量化
版本、一个 Prompt 和一套本地推理配置。Calibration 与 validation
分区较小，而且所有可用 calibration 判断恰好正确，导致 isotonic
calibration 不稳定。当前 Wilson 上界把 pair 当作 Bernoulli 观测，尚未
处理同一基础样本下四类扰动的聚类相关性；正式研究应采用基础样本层面的
cluster bootstrap。最后，style-only 与 verbosity-only 的 gold tie
依赖于受控设计中“变体与原回答实质等价”的假设。

## 可复现性与数据政策

数据集、生成脚本、严格结果 schema、评估指标和完整运行脚本均纳入版本
控制。本地模型的原始预测保留在被忽略的 `results/` 目录中，默认不公开。
公开仓库只包含本汇总报告和机器可读汇总，既保留主要发现，也避免意外
上传本地运行产物。
