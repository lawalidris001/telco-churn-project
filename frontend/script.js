// const form = document.getElementById("churnForm");
// const result = document.getElementById("result");

// form.addEventListener("submit", async function (event) {
//     event.preventDefault();

//     const customerData = {
//         gender: document.getElementById("gender").value,
//         SeniorCitizen: Number(document.getElementById("SeniorCitizen").value),
//         Partner: document.getElementById("Partner").value,
//         Dependents: document.getElementById("Dependents").value,
//         tenure: Number(document.getElementById("tenure").value),
//         PhoneService: document.getElementById("PhoneService").value,
//         MultipleLines: document.getElementById("MultipleLines").value,
//         InternetService: document.getElementById("InternetService").value,
//         OnlineSecurity: document.getElementById("OnlineSecurity").value,
//         OnlineBackup: document.getElementById("OnlineBackup").value,
//         DeviceProtection: document.getElementById("DeviceProtection").value,
//         TechSupport: document.getElementById("TechSupport").value,
//         StreamingTV: document.getElementById("StreamingTV").value,
//         StreamingMovies: document.getElementById("StreamingMovies").value,
//         Contract: document.getElementById("Contract").value,
//         PaperlessBilling: document.getElementById("PaperlessBilling").value,
//         PaymentMethod: document.getElementById("PaymentMethod").value,
//         MonthlyCharges: Number(document.getElementById("MonthlyCharges").value),
//         TotalCharges: Number(document.getElementById("TotalCharges").value)
//     };

//     try {
//         const response = await fetch("/frontend-predict", {
//             method: "POST",
//             headers: {
//                 "Content-Type": "application/json"
//             },
//             body: JSON.stringify(customerData)
//         });

//         const data = await response.json();

//         if (!response.ok) {
//             throw new Error(data.detail || "Prediction failed");
//         }

//         result.innerHTML = `
//             <h2>${data.prediction_label}</h2>
//             <p>Churn probability: ${(data.churn_probability * 100).toFixed(2)}%</p>
//             <p>Decision threshold: ${(data.threshold * 100).toFixed(0)}%</p>
//         `;

//     } catch (error) {
//         result.innerHTML = `
//             <p>Error: ${error.message}</p>
//         `;
//     }
// });






const form = document.getElementById("churnForm");
const result = document.getElementById("result");
const predictButton = document.getElementById("predictButton");
const buttonText = predictButton.querySelector(".button-text");


form.addEventListener("submit", async function (event) {

    event.preventDefault();


    // -----------------------------
    // Collect customer information
    // -----------------------------

    const customerData = {

        gender:
            document.getElementById("gender").value,

        SeniorCitizen:
            Number(
                document.getElementById("SeniorCitizen").value
            ),

        Partner:
            document.getElementById("Partner").value,

        Dependents:
            document.getElementById("Dependents").value,

        tenure:
            Number(
                document.getElementById("tenure").value
            ),

        PhoneService:
            document.getElementById("PhoneService").value,

        MultipleLines:
            document.getElementById("MultipleLines").value,

        InternetService:
            document.getElementById("InternetService").value,

        OnlineSecurity:
            document.getElementById("OnlineSecurity").value,

        OnlineBackup:
            document.getElementById("OnlineBackup").value,

        DeviceProtection:
            document.getElementById("DeviceProtection").value,

        TechSupport:
            document.getElementById("TechSupport").value,

        StreamingTV:
            document.getElementById("StreamingTV").value,

        StreamingMovies:
            document.getElementById("StreamingMovies").value,

        Contract:
            document.getElementById("Contract").value,

        PaperlessBilling:
            document.getElementById("PaperlessBilling").value,

        PaymentMethod:
            document.getElementById("PaymentMethod").value,

        MonthlyCharges:
            Number(
                document.getElementById("MonthlyCharges").value
            ),

        TotalCharges:
            Number(
                document.getElementById("TotalCharges").value
            )
    };


    // -----------------------------
    // Loading state
    // -----------------------------

    predictButton.disabled = true;

    buttonText.textContent = "Analyzing...";

    result.className = "result hidden";



    try {

        // -----------------------------
        // Send data to FastAPI
        // -----------------------------

        const response = await fetch(
            "/frontend-predict",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify(customerData)
            }
        );


        const data = await response.json();


        if (!response.ok) {
            throw new Error(
                data.detail || "Prediction failed"
            );
        }


        // -----------------------------
        // Convert probability
        // -----------------------------

        const probability =
            Number(data.churn_probability) * 100;

        const threshold =
            Number(data.threshold) * 100;


        const isChurn =
            data.prediction === 1;


        // -----------------------------
        // Display result
        // -----------------------------

        result.className =
            `result ${isChurn ? "churn" : "stay"}`;


        result.innerHTML = `

            <div class="result-header">

                <div>

                    <h2 class="result-label">
                        ${data.prediction_label}
                    </h2>

                    <p class="result-description">
                        Based on the customer's current profile
                        and the model's prediction.
                    </p>

                </div>

                <div class="probability">
                    ${probability.toFixed(1)}%
                </div>

            </div>


            <div class="progress-track">

                <div
                    class="progress-bar"
                    style="width: ${probability}%"
                ></div>

            </div>


            <div class="result-meta">

                <span>
                    Churn probability
                </span>

                <span>
                    Decision threshold: ${threshold.toFixed(0)}%
                </span>

            </div>

        `;


        // Scroll result into view
        result.scrollIntoView({
            behavior: "smooth",
            block: "nearest"
        });


    } catch (error) {

        // -----------------------------
        // Error state
        // -----------------------------

        result.className =
            "result error-result";


        result.innerHTML = `

            <p>
                <strong>Prediction error:</strong>
                ${error.message}
            </p>

        `;


    } finally {

        // -----------------------------
        // Restore button
        // -----------------------------

        predictButton.disabled = false;

        buttonText.textContent =
            "Predict Churn";
    }

});