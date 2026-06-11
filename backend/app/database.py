"""SQLite database for caching odds data."""

import aiosqlite
from datetime import datetime, timedelta
from app.config import settings
from app.models import Match, BetType


async def init_db():
    """Initialize database tables."""
    settings.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    async with aiosqlite.connect(settings.DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS matches (
                id TEXT PRIMARY KEY,
                league TEXT,
                home_team TEXT,
                away_team TEXT,
                match_time TEXT,
                odds TEXT,
                bet_type TEXT,
                source TEXT,
                scraped_at TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS bets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id TEXT,
                selection TEXT,
                odds REAL,
                stake REAL,
                potential_return REAL,
                created_at TEXT,
                FOREIGN KEY (match_id) REFERENCES matches(id)
            )
        """)
        await db.commit()


async def cache_matches(matches: list[Match]):
    """Cache matches to database."""
    async with aiosqlite.connect(settings.DB_PATH) as db:
        for match in matches:
            await db.execute(
                """INSERT OR REPLACE INTO matches 
                   (id, league, home_team, away_team, match_time, odds, bet_type, source, scraped_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    match.id,
                    match.league,
                    match.home_team,
                    match.away_team,
                    match.match_time.isoformat(),
                    str(match.odds),
                    match.bet_type.value,
                    match.source,
                    match.scraped_at.isoformat(),
                ),
            )
        await db.commit()


async def get_cached_matches(max_age_seconds: int = None) -> list[Match]:
    """Get cached matches if fresh enough."""
    if max_age_seconds is None:
        max_age_seconds = settings.CACHE_TTL_SECONDS
    
    cutoff = (datetime.now() - timedelta(seconds=max_age_seconds)).isoformat()
    
    async with aiosqlite.connect(settings.DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM matches WHERE scraped_at > ?",
            (cutoff,),
        )
        rows = await cursor.fetchall()
        
        matches = []
        for row in rows:
            odds = eval(row["odds"])  # Convert string back to dict
            matches.append(Match(
                id=row["id"],
                league=row["league"],
                home_team=row["home_team"],
                away_team=row["away_team"],
                match_time=datetime.fromisoformat(row["match_time"]),
                odds=odds,
                bet_type=BetType(row["bet_type"]),
                source=row["source"],
                scraped_at=datetime.fromisoformat(row["scraped_at"]),
            ))
        
        return matches


async def save_bet(match_id: str, selection: str, odds: float, stake: float, potential_return: float):
    """Save a bet record."""
    async with aiosqlite.connect(settings.DB_PATH) as db:
        await db.execute(
            """INSERT INTO bets (match_id, selection, odds, stake, potential_return, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (match_id, selection, odds, stake, potential_return, datetime.now().isoformat()),
        )
        await db.commit()


async def get_bet_history(limit: int = 50) -> list[dict]:
    """Get recent bet history."""
    async with aiosqlite.connect(settings.DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM bets ORDER BY created_at DESC LIMIT ?",
            (limit,),
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
