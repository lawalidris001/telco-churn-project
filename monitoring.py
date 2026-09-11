import pandas as pd
import numpy as np

from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score
)


def calculate_performance(y_true, y_pred):
    """Calculate classification performance metrics."""

    return {
        "precision": precision_score(y_true, y_pred),
        "recall": recall_score(y_true, y_pred),
        "f1": f1_score(y_true, y_pred)
    }


def calculate_psi(reference, current, bins=10):
    """Calculate Population Stability Index for a numerical feature."""

    reference = np.asarray(reference)
    current = np.asarray(current)

    boundaries = np.percentile(
        reference,
        np.linspace(0, 100, bins + 1)
    )

    boundaries = np.unique(boundaries)

    reference_counts, _ = np.histogram(
        reference,
        bins=boundaries
    )

    current_counts, _ = np.histogram(
        current,
        bins=boundaries
    )

    reference_pct = reference_counts / len(reference)
    current_pct = current_counts / len(current)

    reference_pct = np.clip(reference_pct, 0.0001, None)
    current_pct = np.clip(current_pct, 0.0001, None)

    psi = np.sum(
        (current_pct - reference_pct)
        * np.log(current_pct / reference_pct)
    )

    return float(psi)


def calculate_categorical_drift(reference, current):
    """Compare category proportions between reference and current data."""

    reference_pct = reference.value_counts(
        normalize=True
    )

    current_pct = current.value_counts(
        normalize=True
    )

    categories = reference_pct.index.union(
        current_pct.index
    )

    reference_pct = reference_pct.reindex(
        categories,
        fill_value=0
    )

    current_pct = current_pct.reindex(
        categories,
        fill_value=0
    )

    drift = (
        current_pct - reference_pct
    ).abs()

    return float(drift.sum())


def evaluate_performance(metrics, minimum_f1=0.55):
    """Determine whether model performance needs investigation."""

    if metrics["f1"] < minimum_f1:
        return "investigate"

    return "acceptable"


def evaluate_psi(psi, threshold=0.25):
    """Evaluate numerical data drift."""

    if psi > threshold:
        return "drift_detected"

    return "acceptable"


def create_monitoring_report(
    performance_metrics,
    drift_metrics,
    minimum_f1=0.55,
    psi_threshold=0.25
):
    """Create a complete monitoring report."""

    performance_status = evaluate_performance(
        performance_metrics,
        minimum_f1
    )

    report = {
        "performance": performance_metrics,
        "performance_status": performance_status,
        "drift": drift_metrics
    }

    for feature, psi in drift_metrics.items():
        report["drift"][feature] = {
            "psi": psi,
            "status": evaluate_psi(
                psi,
                psi_threshold
            )
        }

    return report