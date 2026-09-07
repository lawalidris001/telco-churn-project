const form = document.getElementById("churnForm");
const result = document.getElementById("result");

form.addEventListener("submit", async function (event) {
    event.preventDefault();

    const customerData = {
        gender: document.getElementById("gender").value,
        SeniorCitizen: Number(document.getElementById("SeniorCitizen").value),
        Partner: document.getElementById("Partner").value,
        Dependents: document.getElementById("Dependents").value,
        tenure: Number(document.getElementById("tenure").value),
        PhoneService: document.getElementById("PhoneService").value,
        MultipleLines: document.getElementById("MultipleLines").value,
        InternetService: document.getElementById("InternetService").value,
        OnlineSecurity: document.getElementById("OnlineSecurity").value,
        OnlineBackup: document.getElementById("OnlineBackup").value,
        DeviceProtection: document.getElementById("DeviceProtection").value,
        TechSupport: document.getElementById("TechSupport").value,
        StreamingTV: document.getElementById("StreamingTV").value,
        StreamingMovies: document.getElementById("StreamingMovies").value,
        Contract: document.getElementById("Contract").value,
        PaperlessBilling: document.getElementById("PaperlessBilling").value,
        PaymentMethod: document.getElementById("PaymentMethod").value,
        MonthlyCharges: Number(document.getElementById("MonthlyCharges").value),
        TotalCharges: Number(document.getElementById("TotalCharges").value)
    };

    try {
        const response = await fetch("/predict", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(customerData)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Prediction failed");
        }

        result.innerHTML = `
            <h2>${data.prediction_label}</h2>
            <p>Churn probability: ${(data.churn_probability * 100).toFixed(2)}%</p>
            <p>Decision threshold: ${(data.threshold * 100).toFixed(0)}%</p>
        `;

    } catch (error) {
        result.innerHTML = `
            <p>Error: ${error.message}</p>
        `;
    }
});