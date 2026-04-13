import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

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

    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///data/the-bot.db")

    # Encryption
    encryption_key: str = os.getenv("ENCRYPTION_KEY", "default_key_not_secure")

settings = Settings()
