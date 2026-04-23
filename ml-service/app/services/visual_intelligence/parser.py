import re

KNOWN_MEDICINES = [
    "amlodipine",
    "asthalin",
    "enalapril",
    "ibuprofen",
    "loperamide",
    "metformin",
    "pantoprazole",
    "paracetamol",
    "rosuvastatin",
    "sumatriptan",
    "sodiumvalproate",
    "levodopa",
    "donepezil",
    "interferonbeta",
    "ceftriaxone",
    "fluoxetine",
    "alprazolam",
    "aspirin",
    "aspirinlowdose",
    "amiodarone",
    "furosemide",
    "nitroglycerin",
    "clopidogrel",
    "metoprolol",
    "vancomycin",
    "azithromycin",
    "budesonide",
    "rifampicin",
    "dextromethorphan",
    "cisplatin",
    "heparin",
    "furosemideinjection",
    "furosemidetab",
    "pirfenidone",
    "loratadine",
    "hydrocortisone",
    "clotrimazole",
    "tacrolimus",
    "amoxycillin",
    "aciclovir",
    "calpol"
]

BAD_WORDS = {
    "tablet", "tablets", "capsule", "capsules", "syrup", "strip",
    "mrp", "batch", "mfg", "exp", "use", "before", "after",
    "clc"
}

def clean_text(texts):
    return " ".join(texts).strip()

def extract_dosage(text):
    match = re.search(r'\b\d+(\.\d+)?\s?(mg|ml|g|mcg)\b', text.lower())
    return match.group() if match else None

def extract_medicine_name(text):
    text_lower = text.lower()

    for med in KNOWN_MEDICINES:
        if med in text_lower:
            return med

    words = text_lower.split()
    for med in KNOWN_MEDICINES:
        for word in words:
            if med.startswith(word) and len(word) >= 4:
                return med

    for word in words:
        w = re.sub(r'[^a-zA-Z0-9]', '', word)
        if len(w) > 3 and w not in BAD_WORDS and not w.isdigit():
            return w

    return None

def parse_medicine_fields(ocr_output):
    text = clean_text(ocr_output["texts"])

    return {
        "medicine_name": extract_medicine_name(text),
        "dosage": extract_dosage(text),
        "detected_text": text,
        "confidence": ocr_output["confidence"]
    }