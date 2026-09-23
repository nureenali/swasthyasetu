from typing import Any, Dict, List

from app.schemas.common_schema import HealthCategory, ProcessingStatus, RiskLevel
from app.schemas.text_schema import (
    ExtractedFieldSchema,
    TextExtractionResultSchema,
    TextRouteResponseSchema,
)
from app.services.smart_add.cleaner import clean_text
from app.services.smart_add.extractor import extract_fields
from app.services.smart_add.router import route_text
from app.services.smart_add.scorer import score_extraction
from app.services.smart_add.context_memory import save_user_record, load_user_history
from app.services.smart_add.trend_analyzer import analyze_trend
from app.services.smart_add.synonym_mapper import normalize_extracted_data
from app.services.smart_add.hinglish_mapper import normalize_hinglish_text
from app.services.smart_add.feature_builder import build_health_features
from app.services.smart_add.risk_engine import get_enhanced_risk_level
from app.services.smart_add.response_builder import build_user_friendly_response
from app.services.smart_add.future_risk_predictor import predict_future_risks
from app.services.smart_add.health_score_engine import calculate_health_score
from app.services.smart_add.followup_engine import generate_followup_questions
from app.services.smart_add.severity_engine import calculate_severity_and_priority
from app.services.smart_add.timeline_insight_engine import build_timeline_insights
from app.services.smart_add.final_response_builder import build_final_response


def _dict_to_extracted_fields(extracted_data: Dict[str, Any]) -> List[ExtractedFieldSchema]:
    fields = []

    for key, value in extracted_data.items():
        if value is None:
            continue
        if isinstance(value, str) and not value.strip():
            continue
        if isinstance(value, (dict, list)):
            continue

        fields.append(ExtractedFieldSchema(key=key, value=value))

    return fields


def _build_failed_response(original_text: str, cleaned_text: str, message: str) -> TextRouteResponseSchema:
    result = TextExtractionResultSchema(
        category=HealthCategory.UNKNOWN,
        status=ProcessingStatus.FAILED,
        original_text=original_text,
        cleaned_text=cleaned_text,
        extracted_data={},
        extracted_fields=[],
        confidence=0.0,
        score=0.0,
        risk_level=RiskLevel.LOW,
        message=message,
    )
    return TextRouteResponseSchema(success=False, data=result)


def _build_history_record(
    original_text: str,
    cleaned_text: str,
    category: HealthCategory,
    extracted_data: Dict[str, Any],
    confidence: float,
    score: float,
    risk_level: RiskLevel,
) -> Dict[str, Any]:
    """
    Convert current pipeline result into a structured history record.
    This record is what gets saved into context memory.
    """

    normalized_value = None

    preferred_keys = [
        "condition",
        "symptom",
        "medicine_name",
        "habit",
        "activity",
        "issue",
        "value",
        "disease",
    ]

    for key in preferred_keys:
        value = extracted_data.get(key)
        if isinstance(value, str) and value.strip():
            normalized_value = value.strip().lower()
            break

    if normalized_value is None:
        if category == HealthCategory.SYMPTOM:
            normalized_value = "symptom_logged"
        elif category == HealthCategory.MEDICATION:
            normalized_value = "medication_logged"
        elif category == HealthCategory.ROUTINE:
            normalized_value = "routine_logged"
        elif category == HealthCategory.FAMILY_HISTORY:
            normalized_value = "family_history_logged"
        else:
            normalized_value = "health_event_logged"

    record = {
        "original_text": original_text,
        "cleaned_text": cleaned_text,
        "category": category.value if hasattr(category, "value") else str(category),
        "value": normalized_value,
        "extracted_data": extracted_data,
        "confidence": confidence,
        "score": score,
        "risk_level": risk_level.value if hasattr(risk_level, "value") else str(risk_level),
        "source": "text",
    }

    return record


def process_health_text(text: str, user_id: str = "default_user") -> TextRouteResponseSchema:
    """
    Main end-to-end pipeline for text health input.

    Includes:
    - cleaning
    - Hinglish normalization
    - routing
    - extraction
    - synonym normalization
    - scoring
    - context memory
    - trend analysis
    - feature building
    - enhanced risk reasoning
    - future risk prediction
    - health score
    - severity analysis
    - follow-up questions
    - timeline insights
    """

    original_text = text if text is not None else ""

    if text is None:
        return _build_failed_response(
            original_text="",
            cleaned_text="",
            message="Input text is missing",
        )

    cleaned_text = clean_text(text)

    if not cleaned_text:
        return _build_failed_response(
            original_text=original_text,
            cleaned_text="",
            message="Input text is empty after cleaning",
        )

    cleaned_text = normalize_hinglish_text(cleaned_text)

    try:
        # Step 1: Route
        category = route_text(cleaned_text)

        # Step 2: Extract
        extracted_data = extract_fields(cleaned_text, category)
        if extracted_data is None:
            extracted_data = {}

        # Step 3: Normalize extracted data
        extracted_data = normalize_extracted_data(extracted_data)

        # Step 4: Score extraction quality
        score, confidence, status, message = score_extraction(category, extracted_data)

        # Step 5: Save temporary history record with placeholder risk
        temp_history_record = _build_history_record(
            original_text=original_text,
            cleaned_text=cleaned_text,
            category=category,
            extracted_data=extracted_data,
            confidence=confidence,
            score=score,
            risk_level=RiskLevel.LOW,
        )

        history_saved = save_user_record(user_id, temp_history_record)

        # Step 6: Load updated history
        user_history = load_user_history(user_id)

        # Step 7: Timeline + trend + features
        trend_analysis = analyze_trend(user_history)
        health_features = build_health_features(user_history)
        timeline_insights = build_timeline_insights(user_history)

        # Step 8: Current enhanced risk
        risk_level = get_enhanced_risk_level(
            category=category,
            extracted_data=extracted_data,
            health_features=health_features,
            trend_analysis=trend_analysis,
        )

        # Step 9: Future risk prediction
        future_risk_predictions = predict_future_risks(
            health_features=health_features,
            trend_analysis=trend_analysis,
        )

        # Step 10: Health score
        current_risk_str = risk_level.value if hasattr(risk_level, "value") else str(risk_level)
        category_str = category.value if hasattr(category, "value") else str(category)

        health_score = calculate_health_score(
            health_features=health_features,
            current_risk_level=current_risk_str,
            future_risk_predictions=future_risk_predictions,
            trend_analysis=trend_analysis,
        )

        # Step 11: Severity analysis
        severity_analysis = calculate_severity_and_priority(
            health_features=health_features,
            current_risk_level=current_risk_str,
            future_risk_predictions=future_risk_predictions,
            health_score=health_score,
            trend_analysis=trend_analysis,
        )

        # Step 12: Follow-up questions
        followup_questions = generate_followup_questions(
            category=category_str,
            extracted_data=extracted_data,
            risk_level=current_risk_str,
        )

        # Step 13: User-friendly response
        user_friendly_response = build_user_friendly_response(
            category=category_str,
            extracted_data=extracted_data,
            risk_level=current_risk_str,
            trend_analysis=trend_analysis,
            health_features=health_features,
        )

        # Step 14: Build enriched extracted data
        enriched_extracted_data = dict(extracted_data)
        enriched_extracted_data["history_saved"] = history_saved
        enriched_extracted_data["trend_analysis"] = trend_analysis
        enriched_extracted_data["health_features"] = health_features
        enriched_extracted_data["future_risk_predictions"] = future_risk_predictions
        enriched_extracted_data["health_score"] = health_score
        enriched_extracted_data["severity_analysis"] = severity_analysis
        enriched_extracted_data["timeline_insights"] = timeline_insights
        enriched_extracted_data["user_friendly_response"] = user_friendly_response
        enriched_extracted_data["followup_questions"] = followup_questions

        final_dashboard_output = build_final_response(enriched_extracted_data)

        enriched_extracted_data["final_output"] = final_dashboard_output

        # Step 15: Extract simple display fields
        extracted_fields = _dict_to_extracted_fields(enriched_extracted_data)

        # Step 16: Final response
        result = TextExtractionResultSchema(
            category=category,
            status=status,
            original_text=original_text,
            cleaned_text=cleaned_text,
            extracted_data=enriched_extracted_data,
            extracted_fields=extracted_fields,
            confidence=confidence,
            score=score,
            risk_level=risk_level,
            message=message,
        )

        return TextRouteResponseSchema(success=True, data=result)

    except Exception as exc:
        return _build_failed_response(
            original_text=original_text,
            cleaned_text=cleaned_text,
            message=f"Pipeline processing failed: {str(exc)}",
        )
