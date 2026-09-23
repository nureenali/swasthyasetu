from fastapi import FastAPI
from app.api.router import api_router

app = FastAPI(
    title="SwasthyaSetu ML Service",
    description="ML service for smart health text understanding and structured extraction",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "message": "SwasthyaSetu ML Service is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }


app.include_router(api_router)
