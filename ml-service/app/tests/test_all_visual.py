import os

from app.services.visual_intelligence.pipeline import process_medicine_image
from app.services.medical_report.report_pipeline import process_medical_report


medicine_folder = "data/sample_images"
report_folder = "data/medical_report"

allowed_extensions = [".jpg", ".jpeg", ".png"]


def process_medicine_folder():
    print("\n========== MEDICINE IMAGE EXTRACTION ==========")

    if not os.path.exists(medicine_folder):
        print("Medicine folder not found:", medicine_folder)
        return

    for file_name in os.listdir(medicine_folder):
        file_path = os.path.join(medicine_folder, file_name)

        if not os.path.isfile(file_path):
            continue

        ext = os.path.splitext(file_name)[1].lower()

        if ext not in allowed_extensions:
            continue

        print("\nProcessing medicine:", file_name)

        result = process_medicine_image(file_path)

        print("Medicine Name:", result.get("medicine_name"))
        print("Dosage:", result.get("dosage"))
        print("Confidence:", result.get("confidence"))
        print("Manual Input Required:", result.get("manual_input_required"))


def process_report_folder():
    print("\n========== MEDICAL REPORT EXTRACTION ==========")

    if not os.path.exists(report_folder):
        print("Report folder not found:", report_folder)
        return

    for file_name in os.listdir(report_folder):
        file_path = os.path.join(report_folder, file_name)

        if not os.path.isfile(file_path):
            continue

        ext = os.path.splitext(file_name)[1].lower()

        if ext not in allowed_extensions:
            continue

        print("\nProcessing report:", file_name)

        result = process_medical_report(file_path, gender="male")

        print("Report Type:", result.get("report_type"))
        print("Processing Time:", result.get("processing_time_seconds"))
        print("Tests Found:", len(result.get("tests", [])))
        print("Alerts:", result.get("alerts", []))


if __name__ == "__main__":
    process_medicine_folder()
    process_report_folder()

    print("\n========== ALL VISUAL INTELLIGENCE TASKS COMPLETED ==========")