import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "").split(",")
    CORS_SUPPORTS_CREDENTIALS = True

    RATE_LIMIT_DEFAULT = os.getenv("RATE_LIMIT_DEFAULT", "100 per minute")

