"""JudgeTrust public interfaces."""

from .calibration import IsotonicCalibrator, calibration_metrics
from .data import DatasetItem, load_jsonl, validate_paired_dataset
from .fake import FixedWinnerJudge
from .interfaces import Judge, JudgeRequest, JudgeResult
from .metrics import compute_metrics
from .ollama import OllamaConnectionError, OllamaJudge, OllamaResponseError
from .prompting import build_judge_prompt, parse_judge_response
from .recorded import RecordedJudge
from .runner import EvaluationRecord, run_judge, write_run
from .selective import (
    PairDecision,
    audit_calibrated_judge,
    audit_selective_judge,
    build_pair_decisions,
    risk_coverage_curve,
    wilson_upper_bound,
)

__all__ = [
    "DatasetItem",
    "FixedWinnerJudge",
    "IsotonicCalibrator",
    "Judge",
    "JudgeRequest",
    "JudgeResult",
    "OllamaConnectionError",
    "OllamaJudge",
    "OllamaResponseError",
    "RecordedJudge",
    "PairDecision",
    "audit_calibrated_judge",
    "audit_selective_judge",
    "build_judge_prompt",
    "build_pair_decisions",
    "calibration_metrics",
    "EvaluationRecord",
    "compute_metrics",
    "load_jsonl",
    "parse_judge_response",
    "run_judge",
    "risk_coverage_curve",
    "validate_paired_dataset",
    "wilson_upper_bound",
    "write_run",
]
__version__ = "0.1.0"
