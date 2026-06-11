from pathlib import Path


class Settings:
    PROJECT_ROOT: Path = Path(__file__).parent.parent
    DB_PATH: Path = PROJECT_ROOT / "data" / "odds.db"
    CACHE_TTL_SECONDS: int = 300  # 5 minutes
    SCRAPER_TIMEOUT: int = 30
    MAX_CONCURRENT_REQUESTS: int = 5

    # Budget presets (RMB)
    BUDGET_PRESETS: list[int] = [100, 200, 500, 1000, 2000, 5000]

    # Risk levels
    RISK_CONSERVATIVE: str = "conservative"
    RISK_MODERATE: str = "moderate"
    RISK_AGGRESSIVE: str = "aggressive"


settings = Settings()
