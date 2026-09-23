from fastapi import APIRouter, HTTPException

from app.schemas.text_schema import TextInputSchema, TextRouteResponseSchema
from app.services.smart_add.pipeline import process_health_text

router = APIRouter(prefix="/smart-add", tags=["Smart Add Text"])


@router.post("/text", response_model=TextRouteResponseSchema)
def smart_add_text(payload: TextInputSchema) -> TextRouteResponseSchema:
    """
    Accepts raw health-related text input and returns structured ML output.
    """
    try:
        result = process_health_text(
            text=payload.text,
            user_id=payload.user_id or "default_user",
        )
        return result

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Text processing failed: {exc}",
        )
