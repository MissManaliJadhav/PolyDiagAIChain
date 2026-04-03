def calculate_trust(confidence, robustness="Stable"):

    # Convert percentage string to float
    if isinstance(confidence, str):
        confidence = float(confidence.replace("%", "")) / 100

    # ===============================
    # TRUST LOGIC
    # ===============================

    if robustness != "Stable":
        return "Unstable Prediction ⚠️ (Adversarial Risk)"

    # VERY LOW CONFIDENCE (Critical)
    if confidence < 0.50:
        return "Very Low Trust ❌ (Uncertain Prediction)"

    elif confidence < 0.65:
        return "Low Trust ❌"

    elif confidence < 0.80:
        return "Moderate Trust ⚠️"

    elif confidence < 0.90:
        return "High Trust 👍"

    else:
        return "Very High Trust ✅"