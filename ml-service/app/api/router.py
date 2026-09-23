from fastapi import APIRouter
from .routes_text import router as text_router
from .routes_image import router as image_router

api_router = APIRouter()
api_router.include_router(text_router)
api_router.include_router(image_router)

def detect_modules(text: str):
    modules = []

    if "sleep" in text or "water" in text:
        modules.append("routine")

    if "medicine" in text or "pill" in text or "forgot" in text:
        modules.append("medication")

    return modules
