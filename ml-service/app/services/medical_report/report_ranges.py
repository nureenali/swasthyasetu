NORMAL_RANGES = {
    "hemoglobin": {
        "male": {
            "min": 13.2,
            "max": 16.6,
            "unit": "g/dL",
            "margin": 0.4
        },
        "female": {
            "min": 11.6,
            "max": 15.0,
            "unit": "g/dL",
            "margin": 0.4
        },
        "unknown": {
            "min": 12.0,
            "max": 16.0,
            "unit": "g/dL",
            "margin": 0.4
        }
    },

    "wbc": {
        "common": {
            "min": 4000,
            "max": 11000,
            "unit": "cells/cumm",
            "margin": 500
        }
    },

    "rbc": {
        "male": {
            "min": 4.5,
            "max": 5.9,
            "unit": "million/cumm",
            "margin": 0.2
        },
        "female": {
            "min": 4.1,
            "max": 5.1,
            "unit": "million/cumm",
            "margin": 0.2
        },
        "unknown": {
            "min": 4.2,
            "max": 5.5,
            "unit": "million/cumm",
            "margin": 0.2
        }
    },

    "platelets": {
        "common": {
            "min": 150000,
            "max": 410000,
            "unit": "cells/cumm",
            "margin": 20000
        }
    },

    "glucose": {
        "common": {
            "min": 70,
            "max": 100,
            "unit": "mg/dL",
            "margin": 10
        }
    },

    "hba1c": {
        "common": {
            "min": 4.0,
            "max": 5.6,
            "unit": "%",
            "margin": 0.3
        }
    },

    "cholesterol": {
        "common": {
            "min": 0,
            "max": 200,
            "unit": "mg/dL",
            "margin": 20
        }
    },

    "hdl": {
        "common": {
            "min": 40,
            "max": 100,
            "unit": "mg/dL",
            "margin": 5
        }
    },

    "ldl": {
        "common": {
            "min": 0,
            "max": 100,
            "unit": "mg/dL",
            "margin": 10
        }
    },

    "triglycerides": {
        "common": {
            "min": 0,
            "max": 150,
            "unit": "mg/dL",
            "margin": 20
        }
    },

    "creatinine": {
        "male": {
            "min": 0.7,
            "max": 1.3,
            "unit": "mg/dL",
            "margin": 0.1
        },
        "female": {
            "min": 0.6,
            "max": 1.1,
            "unit": "mg/dL",
            "margin": 0.1
        },
        "unknown": {
            "min": 0.6,
            "max": 1.3,
            "unit": "mg/dL",
            "margin": 0.1
        }
    },

    "urea": {
        "common": {
            "min": 15,
            "max": 40,
            "unit": "mg/dL",
            "margin": 5
        }
    },

    "bilirubin": {
        "common": {
            "min": 0.1,
            "max": 1.2,
            "unit": "mg/dL",
            "margin": 0.2
        }
    },

    "sgpt": {
        "common": {
            "min": 7,
            "max": 56,
            "unit": "U/L",
            "margin": 5
        }
    },

    "sgot": {
        "common": {
            "min": 5,
            "max": 40,
            "unit": "U/L",
            "margin": 5
        }
    }
}


def get_range_data(test_name, gender="unknown"):
    test_name = test_name.lower()
    gender = gender.lower()

    if test_name not in NORMAL_RANGES:
        return None

    range_info = NORMAL_RANGES[test_name]

    if gender in range_info:
        return range_info[gender]

    if "common" in range_info:
        return range_info["common"]

    if "unknown" in range_info:
        return range_info["unknown"]

    return None


def get_status(test_name, value, gender="unknown"):
    range_data = get_range_data(test_name, gender)

    if range_data is None:
        return {
            "status": "Unknown",
            "normal_range": "Not available",
            "message": "Normal range is not available for this test."
        }

    min_value = range_data["min"]
    max_value = range_data["max"]
    margin = range_data["margin"]
    unit = range_data["unit"]

    normal_range = f"{min_value}-{max_value} {unit}"

    if value < min_value - margin:
        return {
            "status": "Low",
            "normal_range": normal_range,
            "message": f"{test_name} is lower than the normal range."
        }

    elif min_value - margin <= value < min_value:
        return {
            "status": "Borderline Low",
            "normal_range": normal_range,
            "message": f"{test_name} is slightly below normal range but close to acceptable range."
        }

    elif min_value <= value <= max_value:
        return {
            "status": "Normal",
            "normal_range": normal_range,
            "message": f"{test_name} is within the normal range."
        }

    elif max_value < value <= max_value + margin:
        return {
            "status": "Borderline High",
            "normal_range": normal_range,
            "message": f"{test_name} is slightly above normal range but close to acceptable range."
        }

    else:
        return {
            "status": "High",
            "normal_range": normal_range,
            "message": f"{test_name} is higher than the normal range."
        }