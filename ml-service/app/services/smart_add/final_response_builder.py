from typing import Dict, Any


def build_final_response(extracted_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert raw pipeline output into frontend/dashboard-ready response.
    """

    health_score = extracted_data.get("health_score", {})
    severity = extracted_data.get("severity_analysis", {})
    timeline = extracted_data.get("timeline_insights", {})
    response = extracted_data.get("user_friendly_response", {})
    followups = extracted_data.get("followup_questions", [])

    final_output = {
        "health_score": health_score.get("score", 0),
        "health_level": health_score.get("level", "unknown"),

        "severity": severity.get("severity_level", "low"),
        "priority_score": severity.get("priority_score", 0),
        "alerts": severity.get("priority_tags", []),

        "summary": response.get("summary", ""),
        "risk_explanation": response.get("risk_explanation", ""),

        "timeline_summary": timeline.get("timeline_summary", ""),
        "pattern_notes": timeline.get("pattern_notes", []),

        "suggestions": response.get("suggestions", []),
        "followups": followups,
    }

    return final_output
