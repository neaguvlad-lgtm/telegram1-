from dataclasses import dataclass
from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()


@dataclass
class Settings:
    BOT_TOKEN: str = os.getenv('BOT_TOKEN', '')
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    COOLDOWN_SECONDS: int = int(os.getenv('COOLDOWN_SECONDS', '30'))
    # Render: SQLite database persists on ephemeral disk across restarts
    # For Render free tier, database may be reset during infrastructure maintenance
    # Use project root by default (survives normal restarts)
    SQLITE_PATH: str = os.getenv('SQLITE_PATH', './data/bot.db')

    def __post_init__(self):
        # Create data directory if it doesn't exist
        db_path = Path(self.SQLITE_PATH)
        db_path.parent.mkdir(parents=True, exist_ok=True)


settings = Settings()
