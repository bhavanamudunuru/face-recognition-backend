"""
app/models/face_models.py
--------------------------
Pydantic request/response models for face registration and verification APIs.
"""
from pydantic import BaseModel
from typing import Optional


class RegisterFaceRequest(BaseModel):
    user_id: str
    image_url: str


class VerifyFaceRequest(BaseModel):
    user_id: str
    image_url: str


class FaceResult(BaseModel):
    status: str           # "verified" | "not_verified" | "liveness_failed" | "duplicate" | "poor_quality"
    message: str
    confidence: Optional[float] = None
    duplicate_user_id: Optional[str] = None
