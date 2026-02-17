import os
from dotenv import load_dotenv

load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER")
EMERGENCY_NUMBER = os.getenv("EMERGENCY_NUMBER")

TWILIO_ENABLED = os.getenv("TWILIO_ENABLED", "False") == "True"
AUTO_CALL = os.getenv("AUTO_CALL", "False") == "True"


CONFIDENCE_THRESHOLD = int(os.getenv("CONFIDENCE_THRESHOLD", 95))
MIN_DETECTION_FRAMES = int(os.getenv("MIN_DETECTION_FRAMES", 5))
WARMUP_FRAMES = int(os.getenv("WARMUP_FRAMES", 300))


MODEL_JSON = os.getenv("MODEL_JSON")
MODEL_WEIGHTS = os.getenv("MODEL_WEIGHTS")


VIDEO_SOURCE = os.getenv("VIDEO_SOURCE")

WEB_HOST = os.getenv("WEB_HOST", "0.0.0.0")
WEB_PORT = int(os.getenv("WEB_PORT", 5000))
WEB_DEBUG = os.getenv("WEB_DEBUG", "False") == "True"

PHOTO_DIRECTORY = os.getenv("PHOTO_DIRECTORY")
