import os
import csv
import time
from app.services.visual_intelligence.pipeline import process_medicine_image

image_folder = "data/sample_images"
label_file = os.path.join(image_folder, "labels.csv")
output_file = "data/results.csv"

expected_data = {}

with open(label_file, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        expected_data[row["filename"]] = {
            "expected_medicine": row["expected_medicine"].strip().lower(),
            "expected_dosage": row["expected_dosage"].strip().lower()
        }

rows = []

for file_name in os.listdir(image_folder):
    if file_name.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
        image_path = os.path.join(image_folder, file_name)

        start = time.time()
        result = process_medicine_image(image_path)
        end = time.time()

        time_taken = round(end - start, 2)
        print(f"{file_name} -> {time_taken} sec")

        expected = expected_data.get(file_name, {})
        expected_medicine = expected.get("expected_medicine", "")
        expected_dosage = expected.get("expected_dosage", "")

        predicted_medicine = (result.get("medicine_name") or "").strip().lower()
        predicted_dosage = (result.get("dosage") or "").strip().lower()
        confidence = result.get("confidence", 0.0)
        error = result.get("error", "")
        manual_input_required = result.get("manual_input_required", False)

        status = "correct"
        if predicted_medicine != expected_medicine:
            status = "wrong_medicine"
        elif expected_dosage and predicted_dosage != expected_dosage:
            status = "wrong_or_missing_dosage"
        elif manual_input_required:
            status = "manual_input_needed"

        rows.append({
            "filename": file_name,
            "expected_medicine": expected_medicine,
            "predicted_medicine": predicted_medicine,
            "expected_dosage": expected_dosage,
            "predicted_dosage": predicted_dosage,
            "confidence": confidence,
            "error": error,
            "manual_input_required": manual_input_required,
            "status": status,
            "time_taken_sec": time_taken
        })

with open(output_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=[
            "filename",
            "expected_medicine",
            "predicted_medicine",
            "expected_dosage",
            "predicted_dosage",
            "confidence",
            "error",
            "manual_input_required",
            "status",
            "time_taken_sec"
        ]
    )
    writer.writeheader()
    writer.writerows(rows)

print(f"Results saved to {output_file}")