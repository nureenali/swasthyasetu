def detect_report_type(text):
    text = text.lower()

    if any(word in text for word in ["hemoglobin", "haemoglobin", "hb", "wbc", "platelet", "rbc"]):
        return "CBC"

    if any(word in text for word in ["glucose", "fasting", "hba1c", "blood sugar"]):
        return "Blood Sugar"

    if any(word in text for word in ["cholesterol", "hdl", "ldl", "triglycerides"]):
        return "Lipid Profile"

    if any(word in text for word in ["bilirubin", "sgpt", "sgot", "alt", "ast"]):
        return "Liver Function Test"

    if any(word in text for word in ["creatinine", "urea", "uric acid"]):
        return "Kidney Function Test"

    return "Unknown"