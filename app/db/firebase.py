"""
app/db/firebase.py
------------------
Firebase Admin SDK initialization.
Exposes db (Firestore) and bucket (Firebase Storage).
"""
import firebase_admin
from firebase_admin import credentials, firestore, storage
from app.core.config import FIREBASE_CERT
from app.core.logger import logger

db = None
bucket = None

try:
    cred = credentials.Certificate(FIREBASE_CERT)
    firebase_admin.initialize_app(cred, {
        "storageBucket": f"{FIREBASE_CERT['project_id']}.appspot.com"
    })
    db = firestore.client()
    bucket = storage.bucket()
    logger.info("Firebase connected successfully!")
except Exception as e:
    logger.error(f"Firebase initialization failed: {e}")
    raise
