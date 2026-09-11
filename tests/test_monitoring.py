import pandas as pd



from monitoring import (
    calculate_performance,
    calculate_psi,
    calculate_categorical_drift,
    evaluate_performance
)


def test_calculate_performance():
    y_true = [0, 1, 1, 0, 1]
    y_pred = [0, 1, 0, 0, 1]

    metrics = calculate_performance(
        y_true,
        y_pred
    )

    assert "precision" in metrics
    assert "recall" in metrics
    assert "f1" in metrics

    assert 0 <= metrics["precision"] <= 1
    assert 0 <= metrics["recall"] <= 1
    assert 0 <= metrics["f1"] <= 1


def test_calculate_psi_no_drift():
    reference = [10, 20, 30, 40, 50]
    current = [10, 20, 30, 40, 50]

    psi = calculate_psi(
        reference,
        current
    )

    assert psi == 0.0


def test_categorical_drift_no_drift():
    reference = [
        "Month-to-month",
        "One year",
        "Two year",
        "Month-to-month"
    ]

    current = [
        "Month-to-month",
        "One year",
        "Two year",
        "Month-to-month"
    ]

    drift = calculate_categorical_drift(
        pd.Series(reference),
        pd.Series(current)
    )

    assert drift == 0.0


def test_evaluate_performance():
    good_metrics = {
        "precision": 0.70,
        "recall": 0.75,
        "f1": 0.62
    }

    bad_metrics = {
        "precision": 0.40,
        "recall": 0.50,
        "f1": 0.49
    }

    assert evaluate_performance(
        good_metrics,
        minimum_f1=0.55
    ) == "acceptable"

    assert evaluate_performance(
        bad_metrics,
        minimum_f1=0.55
    ) == "investigate"