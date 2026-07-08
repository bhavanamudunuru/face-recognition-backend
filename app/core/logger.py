"""
app/core/logger.py
------------------
Centralized logging setup for the entire application.
"""
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("face-recognition")
