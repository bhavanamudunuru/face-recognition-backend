"""
app/core/config.py
------------------
All environment variables and app-wide constants.
"""

import os
from dotenv import load_dotenv

load_dotenv()

FIREBASE_CERT = {
    "type": os.getenv("FIREBASE_TYPE"),
    "project_id": os.getenv("FIREBASE_PROJECT_ID"),
    "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
    "private_key": os.getenv("FIREBASE_PRIVATE_KEY", "").replace("\\n", "\n"),
    "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
    "client_id": os.getenv("FIREBASE_CLIENT_ID"),
    "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
    "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{os.getenv('FIREBASE_CLIENT_EMAIL', '')}",
}

# Face recognition settings
FACE_MATCH_THRESHOLD = 0.70
BLUR_THRESHOLD = 25.0
BRIGHTNESS_MIN = 40
BRIGHTNESS_MAX = 240
FACE_MODEL = "Facenet512"
FACE_DETECTOR = "retinaface"

# CORS
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "https://face-recognition-frontend-chi.vercel.app",
]

# Firestore collections
COLLECTION_USERS = "users"
COLLECTION_FACE_SCANS = "face_scans"
COLLECTION_DUPLICATE_FACES = "duplicate_faces"
