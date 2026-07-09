"""
app/utils/image_utils.py
-------------------------
Utility functions for downloading images and checking image quality.
Uses OpenCV for blur detection and brightness validation.
"""
import base64
import cv2
import numpy as np
import requests
import tempfile
import os
from app.core.config import BLUR_THRESHOLD, BRIGHTNESS_MIN, BRIGHTNESS_MAX
from app.core.logger import logger

CASCADE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "models", "cascades", "haarcascade_frontalface_default.xml"
)


def download_image(image_url: str) -> str:
    """
    Downloads an image from a URL and saves it to a temp file.
    Returns the local file path.
    """
    response = requests.get(image_url, timeout=15)
    if response.status_code != 200:
        raise Exception(f"Failed to download image: HTTP {response.status_code}")
    suffix = ".jpg"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(response.content)
    tmp.close()
    return tmp.name


def decode_base64_image(base64_data: str) -> str:
    """
    Decodes a base64 data URL (e.g. 'data:image/jpeg;base64,...') and saves it to a temp file.
    Returns the local file path.
    """
    if "," in base64_data:
        base64_data = base64_data.split(",", 1)[1]
    image_bytes = base64.b64decode(base64_data)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
    tmp.write(image_bytes)
    tmp.close()
    return tmp.name


def check_image_quality(image_path: str) -> dict:
    """
    Runs quality checks on the image:
    - Blur detection using Laplacian variance
    - Brightness check using mean pixel value
    - Face count check using OpenCV Haar Cascade
    Returns a dict with 'passed' (bool) and 'reason' (str if failed).
    """
    img = cv2.imread(image_path)
    if img is None:
        return {"passed": False, "reason": "Could not read image file."}

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Blur check