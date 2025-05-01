import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = os.getenv("SMTP_PORT", 587)
    SMTP_SENDER = os.getenv("SMTP_SENDER", "your-email@gmail.com")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "your-app-password")