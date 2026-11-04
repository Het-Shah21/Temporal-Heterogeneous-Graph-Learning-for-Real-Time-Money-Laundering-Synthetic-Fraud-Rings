"""Backend-only contract for the existing baseline serving artifacts."""
from pathlib import Path
import pickle

FEATURE_NAMES = [
    "amount",
    "hour_of_day",
    "s_out_degree",
    "s_total_sent",
    "r_in_degree",
    "r_total_received",
    "time_delta",
]

ARTIFACTS_DIR = Path(__file__).resolve().parents[3] / "ml" / "models" / "artifacts"
BASELINE_MODEL_PATH = ARTIFACTS_DIR / "baseline_xgboost.json"
SCALER_PATH = ARTIFACTS_DIR / "scaler.pkl"


class ArtifactUnavailable(RuntimeError):
    pass


def load_scaler():
    if not SCALER_PATH.exists():
        raise ArtifactUnavailable(f"Required scaler artifact not found: {SCALER_PATH}")
    try:
        with SCALER_PATH.open("rb") as handle:
            return pickle.load(handle)
    except Exception as error:
        raise ArtifactUnavailable("Required baseline scaler could not be loaded") from error


def validate_baseline_artifacts():
    if not BASELINE_MODEL_PATH.exists():
        raise ArtifactUnavailable(
            f"Baseline XGBoost artifact not found: {BASELINE_MODEL_PATH}"
        )
    load_scaler()
