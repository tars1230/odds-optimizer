import os
from pathlib import Path


class Settings:
    PROJECT_ROOT: Path = Path(__file__).parent.parent

    # On serverless platforms (Vercel/Lambda) only /tmp is writable.
    _DATA_DIR: Path = (
        Path("/tmp/odds-data") if os.environ.get("VERCEL") else PROJECT_ROOT / "data"
    )
    DB_PATH: Path = _DATA_DIR / "odds.db"

    CACHE_TTL_SECONDS: int = 300  # 5 minutes
    SCRAPER_TIMEOUT: int = 30
    MAX_CONCURRENT_REQUESTS: int = 5

    # Budget presets (RMB)
    BUDGET_PRESETS: list[int] = [100, 200, 500, 1000, 2000, 5000]


settings = Settings()
