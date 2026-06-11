"""Abstract base scraper interface."""

from abc import ABC, abstractmethod
from app.models import Match


class BaseScraper(ABC):
    """Base class for odds scrapers."""
    
    @abstractmethod
    async def fetch_matches(self) -> list[Match]:
        """Fetch today's matches with odds."""
        pass
    
    @abstractmethod
    async def fetch_match_detail(self, match_id: str) -> Match | None:
        """Fetch detailed odds for a specific match."""
        pass