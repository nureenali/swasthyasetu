import csv
import os
import time

from app.services.visual_intelligence.ocr_engine import run_ocr
from app.services.medical_report.report_parser import parse_report_text
from app.services.medical_report.report_type import detect_report_type


def extract_text_from_ocr_result(ocr_result):
    detected_text = ""

    if isinstance(ocr_result, dict):
        if "texts" in ocr_result and isinstance(ocr_result["texts"], list):
            detected_text = " ".join(ocr_result["texts"])

        elif "text" in ocr_result:
            detected_text = ocr_result.get("text", "")

        elif "detected_text" in ocr_result:
            detected_text = ocr_result.get("detected_text", "")

        elif "raw_text" in ocr_result:
            detected_text = ocr_result.get("raw_text", "")

    elif isinstance(ocr_result, list):
        detected_text = " ".join(ocr_result)

    else:
        detected_text = str(ocr_result)

    return detected_text


def save_report_result(image_path, processing_time, report_type, gender, tests, alerts):
    file_path = "data/report_results.csv"

    os.makedirs("data", exist_ok=True)

    file_exists = os.path.exists(file_path)

    with open(file_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow([
                "processing_time_seconds",
                "filename",
                "report_type",
                "gender",
                "test_name",
                "value",
                "unit",
                "status",
                "normal_range",
                "message",
                "alerts"
            ])

        filename = os.path.basename(image_path)

        if not tests:
            writer.writerow([
                processing_time,
                filename,
                report_type,
                gender,
                "",
                "",
                "",
                "",
                "",
                "No tests extracted",
                "; ".join(alerts)
            ])

        for test in tests:
            writer.writerow([
                processing_time,
                filename,
                report_type,
                gender,
                test.get("test_name", ""),
                test.get("value", ""),
                test.get("unit", ""),
                test.get("status", ""),
                test.get("normal_range", ""),
                test.get("message", ""),
                "; ".join(alerts)
            ])


def process_medical_report(image_path, gender="male"):
    start_time = time.time()

    try:
        ocr_result = run_ocr(image_path)

        detected_text = extract_text_from_ocr_result(ocr_result)

        if not detected_text.strip():
            processing_time = round(time.time() - start_time, 2)

            return {
                "type": "medical_report",
                "error": True,
                "message": "No text detected from report.",
                "manual_input_required": True,
                "processing_time_seconds": processing_time,
                "detected_text": "",
                "tests": []
            }

        report_type = detect_report_type(detected_text)

        tests = parse_report_text(detected_text, gender)

        alerts = []

        for test in tests:
            if test["status"] in ["Low", "High", "Borderline Low", "Borderline High"]:
                alerts.append(f"{test['test_name']} is {test['status']}")

        processing_time = round(time.time() - start_time, 2)

        save_report_result(image_path, processing_time, report_type, gender, tests, alerts)

        return {
            "type": "medical_report",
            "report_type": report_type,
            "gender": gender,
            "error": False,
            "manual_input_required": len(tests) == 0,
            "processing_time_seconds": processing_time,
            "detected_text": detected_text,
            "tests": tests,
            "alerts": alerts,
            "message": "Medical report processed successfully."
        }

    except Exception as e:
        processing_time = round(time.time() - start_time, 2)

        return {
            "type": "medical_report",
            "error": True,
            "message": str(e),
            "manual_input_required": True,
            "processing_time_seconds": processing_time,
            "detected_text": "",
            "tests": []
        }