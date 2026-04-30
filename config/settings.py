import os
import json
import logging
from dataclasses import dataclass
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

load_dotenv()

_CREDS_FILE = os.path.join(os.path.dirname(__file__), "../data/admin_creds.json")

@dataclass
class Settings:
    # Global
    flask_secret: str = os.getenv("FLASK_SECRET", "dev_key")
    flask_env: str = os.getenv("FLASK_ENV", "development")
    bot_timezone: str = os.getenv("BOT_TIMEZONE", "Asia/Kolkata")
    scan_interval_seconds: int = int(os.getenv("SCAN_INTERVAL_SECONDS", "5"))
    recheck_interval_seconds: int = int(os.getenv("RECHECK_INTERVAL_SECONDS", "10"))
    max_recheck_attempts: int = int(os.getenv("MAX_RECHECK_ATTEMPTS", "10"))

    # Instagram
    instagram_enabled: bool = os.getenv("INSTAGRAM_ENABLED", "true").lower() == "true"
    instagram_daily_dm_cap: int = int(os.getenv("INSTAGRAM_DAILY_DM_CAP", "50"))
    instagram_dm_delay_min: int = int(os.getenv("INSTAGRAM_DM_DELAY_MIN", "1"))
    instagram_dm_delay_max: int = int(os.getenv("INSTAGRAM_DM_DELAY_MAX", "3"))

    # Twitter
    twitter_enabled: bool = os.getenv("TWITTER_ENABLED", "false").lower() == "true"
    twitter_daily_dm_cap: int = int(os.getenv("TWITTER_DAILY_DM_CAP", "500"))
    twitter_dm_delay_min: int = int(os.getenv("TWITTER_DM_DELAY_MIN", "1"))
    twitter_dm_delay_max: int = int(os.getenv("TWITTER_DM_DELAY_MAX", "5"))

    # Telegram
    telegram_enabled: bool = os.getenv("TELEGRAM_ENABLED", "false").lower() == "true"
    telegram_daily_msg_cap: int = int(os.getenv("TELEGRAM_DAILY_MSG_CAP", "0"))

    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///data/theBot.db")

    # Encryption
    encryption_key: str = os.getenv("ENCRYPTION_KEY", "default_key_not_secure")

    # Dashboard auth (single-user)
    dashboard_username: str = os.getenv("DASHBOARD_USERNAME", "admin")
    dashboard_password_hash: str = ""
    dashboard_api_key: str = os.getenv("DASHBOARD_API_KEY", "")

    def __post_init__(self):
        if os.path.exists(_CREDS_FILE):
            try:
                with open(_CREDS_FILE) as f:
                    self.dashboard_password_hash = json.load(f)["password_hash"]
                return
            except Exception:
                pass
        raw = os.getenv("DASHBOARD_PASSWORD", "changeme")
        if raw == "changeme":
            logging.warning("DASHBOARD_PASSWORD is default 'changeme' — change it in .env before exposing on LAN")
        self.dashboard_password_hash = generate_password_hash(raw)

settings = Settings()
