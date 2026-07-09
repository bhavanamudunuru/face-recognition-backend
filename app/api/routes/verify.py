"""
app/api/routes/verify.py
-------------------------
POST /api/verify
Verifies a scanned face against the registered face of a user.
Runs quality, detection, liveness, then verification checks.
"""
import os
from fastapi import APIRouter, HTTPException
from app.models.face_models import VerifyFaceRequest, FaceResult
from app.utils.image_utils import decode_base64_image, check_image_quality
from app.services.face_detection import detect_face
from app.services.liveness_detection import check_liveness
from app.services.face_verification import verify_face
from app.services.firestore_service import get_user, save_scan_result
from app.core.logger import logger

router = APIRouter(prefix="/api", tags=["Verification"])


@router.post("/verify", response_model=FaceResult)
async def verify_user_face(body: VerifyFaceRequest):
    """
    Verifies a user's face against their registered face.
    Steps: decode -> quality -> detection -> liveness -> verification -> save result
    """
    scanned_path = None
    registered_path = None
    try:
        logger.info(f"Verification started for user: {body.user_id}")

        # Step 1 — Check user exists
        user = get_user(body.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not registered. Please register first.")

        # Step 2 — Decode scanned image
        scanned_path = decode_base64_image(body.image_base64)

        # Step 3 — Image quality check
        quality = check_image_quality(scanned_path)
        if not quality["passed"]:
            save_scan_result(body.user_id, "poor_quality", message=quality["reason"])
            return FaceResult(status="poor_quality", message=quality["reason"])

        # Step 4 — Face detection
        detection = detect_face(scanned_path)
        if not detection["detected"]:
            save_scan_result(body.user_id, "poor_quality", message=detection["reason"])
            return FaceResult(status="poor_quality", message=detection["reason"])

        # Step 5 — Liveness check
        liveness = check_liveness(scanned_path)
        if not liveness["is_live"]:
            save_scan_result(body.user_id, "liveness_failed", message=liveness["reason"])
            return FaceResult(status="liveness_failed", message=liveness["reason"])

        # Step 6 — Decode registered face and verify
        registered_path = decode_base64_image(user["face_image_base64"])
        verification = verify_face(registered_path, scanned_path)

        if verification["verified"]:
            confidence = verification["confidence"]
            save_scan_result(body.user_id, "verified", confidence=confidence, message="Face matched successfully.")
            return FaceResult(status="verified", message="Face verified successfully.", confidence=confidence)
        else:
            save_scan_result(body.user_id, "not_verified", confidence=verification["confidence"], message="Face does not match registered face.")
            return FaceResult(status="not_verified", message="Face does not match. Verification failed.", confidence=verification["confidence"])

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Verification error for {body.user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")
    finally:
        for path in [scanned_path, registered_path]:
            if path and os.path.exists(path):
                os.remove(path)