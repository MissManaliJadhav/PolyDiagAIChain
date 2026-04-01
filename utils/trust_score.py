def calculate_trust(confidence, robustness="Stable"):

    # If confidence is percentage string
    if isinstance(confidence, str):
        confidence = float(confidence.replace("%", "")) / 100

    # Now confidence will always be between 0 and 1

    if robustness == "Stable":

        if confidence >= 0.90:
            return "Very High Trust ✅"
        elif confidence >= 0.75:
            return "High Trust 👍"
        elif confidence >= 0.60:
            return "Moderate Trust ⚠"
        else:
            return "Low Trust ❌"

    else:
        return "Low Trust ❌"