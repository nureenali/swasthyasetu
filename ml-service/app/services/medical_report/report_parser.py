import re
from app.services.medical_report.report_ranges import get_status


TEST_ALIASES = {
    "hemoglobin": [
        "hemoglobin",
        "haemoglobin",
        "hemoglobln",
        "hb",
        "hgb"
    ],

    "rbc": [
        "total rbc count",
        "rbc count",
        "rbc",
        "red blood cell count"
    ],

    "wbc": [
        "total wbc count",
        "wbc count",
        "wbc",
        "white blood cells",
        "total leukocyte count",
        "tlc"
    ],

    "platelets": [
        "platelet count",
        "platelets",
        "platelet",
        "plt",
        "plalelet covnt",
        "plalelet count",
        "platelet covnt"
    ],

    "glucose": [
        "glucose",
        "blood sugar",
        "fasting glucose"
    ],

    "hba1c": [
        "hba1c",
        "hb a1c"
    ],

    "cholesterol": [
        "cholesterol",
        "total cholesterol"
    ],

    "hdl": [
        "hdl"
    ],

    "ldl": [
        "ldl"
    ],

    "triglycerides": [
        "triglycerides",
        "tg"
    ],

    "creatinine": [
        "creatinine"
    ],

    "urea": [
        "urea"
    ],

    "bilirubin": [
        "bilirubin"
    ],

    "sgpt": [
        "sgpt",
        "alt"
    ],

    "sgot": [
        "sgot",
        "ast"
    ]
}


def clean_text(text):
    text = text.lower()
    text = text.replace("\n", " ")

    # common OCR spelling fixes
    text = text.replace("hemoglobln", "hemoglobin")
    text = text.replace("plalelet", "platelet")
    text = text.replace("covnt", "count")
    text = text.replace("nommal", "normal")
    text = text.replace("hormal", "normal")
    text = text.replace("nlonmal", "normal")
    text = text.replace("ommai", "normal")

    # decimal comma fix: 4,50 -> 4.50
    text = re.sub(r"(\d),(\d)", r"\1.\2", text)

    # reduce multiple spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def clean_number(value_text):
    value_text = value_text.strip()

    # OCR sometimes reads 13.00 as 13-Vu or 13-vu
    value_text = value_text.replace("o", "0")
    value_text = value_text.replace("O", "0")

    # keep only starting number part
    match = re.search(r"\d+\.?\d*", value_text)

    if match:
        return float(match.group())

    return None


def extract_value_near_test(text, aliases):
    for alias in aliases:
        alias = alias.lower()

        # Finds number within 40 characters after test name
        pattern = re.escape(alias) + r"[\s\(\)a-zA-Z]*[:\-]?\s*([0-9]+(?:\.[0-9]+)?(?:-[a-zA-Z]+)?)"

        match = re.search(pattern, text)

        if match:
            value = clean_number(match.group(1))

            if value is not None:
                return value, ""

    return None, None


def parse_report_text(text, gender="unknown"):
    text = clean_text(text)

    extracted_tests = []
    found_tests = set()

    for test_name, aliases in TEST_ALIASES.items():
        value, unit = extract_value_near_test(text, aliases)

        if value is not None and test_name not in found_tests:
            status_data = get_status(test_name, value, gender)

            extracted_tests.append({
                "test_name": test_name,
                "value": value,
                "unit": unit,
                "gender": gender,
                "status": status_data["status"],
                "normal_range": status_data["normal_range"],
                "message": status_data["message"]
            })

            found_tests.add(test_name)

    return extracted_tests