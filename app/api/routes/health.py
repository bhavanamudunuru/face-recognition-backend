"""
app/api/routes/health.py
-------------------------
GET /  — health check endpoint
"""
from fastapi import APIRouter

router = APIRouter(tags=["Health"])

@router.get("/")
def health_check():
    return {"status": "ok", "service": "Face Recognition API"}
