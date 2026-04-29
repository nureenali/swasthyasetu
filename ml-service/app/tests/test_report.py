from app.services.medical_report.report_pipeline import process_medical_report

image_path = "data/medical_report/samplecbc.jpeg"

result = process_medical_report(image_path, gender="male")

print(result)