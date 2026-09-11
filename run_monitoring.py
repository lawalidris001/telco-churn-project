import joblib
import pandas as pd

from sklearn.model_selection import train_test_split

from monitoring import (
    calculate_performance,
    calculate_psi,
    calculate_categorical_drift,
    create_monitoring_report
)


DATA_PATH = "data/WA_Fn-UseC_-Telco-Customer-Churn.csv"
MODEL_PATH = "model/telco_churn_model.pkl"


def load_data():
    df = pd.read_csv(DATA_PATH)

    df["TotalCharges"] = pd.to_numeric(
        df["TotalCharges"],
        errors="coerce"
    )

    df["TotalCharges"] = df["TotalCharges"].fillna(0)

    X = df.drop(columns=["Churn", "customerID"])
    y = df["Churn"].map({"No": 0, "Yes": 1})

    return X, y


def main():

    print("Loading model...")

    bundle = joblib.load(MODEL_PATH)

    model = bundle["model"]
    threshold = bundle["threshold"]

    print(f"Model threshold: {threshold}")

    print("Loading data...")

    X, y = load_data()

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    print("Generating predictions...")

    probabilities = model.predict_proba(X_test)[:, 1]

    predictions = (
        probabilities >= threshold
    ).astype(int)

    print("Calculating performance...")

    performance_metrics = calculate_performance(
        y_test,
        predictions
    )

    # -----------------------------------------
    # Numerical drift
    # -----------------------------------------

    numerical_features = [
        "SeniorCitizen",
        "tenure",
        "MonthlyCharges",
        "TotalCharges"
    ]

    drift_metrics = {}

    for feature in numerical_features:

        psi = calculate_psi(
            X_train[feature],
            X_test[feature]
        )

        drift_metrics[feature] = psi

    # -----------------------------------------
    # Categorical drift
    # -----------------------------------------

    categorical_features = [
        "gender",
        "Partner",
        "Dependents",
        "PhoneService",
        "MultipleLines",
        "InternetService",
        "OnlineSecurity",
        "OnlineBackup",
        "DeviceProtection",
        "TechSupport",
        "StreamingTV",
        "StreamingMovies",
        "Contract",
        "PaperlessBilling",
        "PaymentMethod"
    ]

    for feature in categorical_features:

        drift_score = calculate_categorical_drift(
            X_train[feature],
            X_test[feature]
        )

        drift_metrics[feature] = drift_score

    # -----------------------------------------
    # Create monitoring report
    # -----------------------------------------

    report = create_monitoring_report(
        performance_metrics,
        drift_metrics
    )

    print("\n==============================")
    print("       MONITORING REPORT")
    print("==============================")

    print("\nPerformance:")

    print(
        f"Precision: "
        f"{report['performance']['precision']:.4f}"
    )

    print(
        f"Recall:    "
        f"{report['performance']['recall']:.4f}"
    )

    print(
        f"F1:        "
        f"{report['performance']['f1']:.4f}"
    )

    print(
        f"Status:    "
        f"{report['performance_status']}"
    )

    print("\nDrift:")

    for feature, result in report["drift"].items():

        if isinstance(result, dict):

            print(
                f"{feature}: "
                f"{result['psi']:.4f} "
                f"({result['status']})"
            )

        else:

            print(
                f"{feature}: "
                f"{result:.4f}"
            )


if __name__ == "__main__":
    main()