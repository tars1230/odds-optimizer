# 竞彩赔率优化器 (Odds Optimizer) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a web application that scrapes real-time sports betting odds, calculates optimal risk-reward ratios using Kelly Criterion, and generates budget-based betting plans.

**Architecture:** Python FastAPI backend with Playwright-based odds scraper, SQLite for caching, React + Tailwind frontend. Core engine uses Kelly Criterion for optimal bet sizing and expected value calculations to rank matches by risk-reward.

**Tech Stack:** Python 3.11+, FastAPI, Playwright (web scraping), SQLite, React 18, Tailwind CSS, Vite

---

## File Structure

```
odds-optimizer/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app entry
│   │   ├── config.py            # Settings & constants
│   │   ├── models.py            # Pydantic models
│   │   ├── database.py          # SQLite setup
│   │   ├── scrapers/
│   │   │   ├── __init__.py
│   │   │   ├── base.py          # Abstract scraper interface
│   │   │   ├── aoke.py          # 澳客网 scraper
│   │   │   └── parser.py        # HTML parser for odds data
│   │   ├── engine/
│   │   │   ├── __init__.py
│   │   │   ├── kelly.py         # Kelly Criterion calculator
│   │   │   ├── optimizer.py     # Budget optimization algorithm
│   │   │   └── ev.py            # Expected value calculations
│   │   └── api/
│   │       ├── __init__.py
│   │       ├── matches.py       # GET /api/matches
│   │       ├── optimize.py      # POST /api/optimize
│   │       └── history.py       # GET /api/history
│   ├── tests/
│   │   ├── test_kelly.py
│   │   ├── test_optimizer.py
│   │   └── test_scraper.py
│   ├── requirements.txt
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── MatchList.tsx     # Today's matches display
│   │   │   ├── BudgetInput.tsx   # Budget selector
│   │   │   ├── PlanCard.tsx      # Betting plan card
│   │   │   ├── OddsBadge.tsx     # Odds display badge
│   │   │   └── RiskMeter.tsx     # Risk level indicator
│   │   ├── hooks/
│   │   │   ├── useMatches.ts     # Fetch matches hook
│   │   │   └── useOptimize.ts    # Optimize budget hook
│   │   ├── lib/
│   │   │   └── api.ts            # API client
│   │   └── main.tsx
│   ├── package.json
│   ├── tailwind.config.js
│   ├── vite.config.ts
│   └── index.html
├── docker-compose.yml
└── README.md
```

---

## Task 1: Project Setup & Backend Scaffold

**Files:**
- Create: `backend/pyproject.toml`, `backend/requirements.txt`, `backend/app/__init__.py`, `backend/app/main.py`, `backend/app/config.py`

- [ ] **Step 1: Create project structure**

```bash
mkdir -p odds-optimizer/backend/app/{scrapers,engine,api} odds-optimizer/backend/tests
cd odds-optimizer
```

- [ ] **Step 2: Create pyproject.toml**

```toml
[project]
name = "odds-optimizer"
version = "0.1.0"
description = "Sports betting odds optimizer"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "playwright>=1.40.0",
    "beautifulsoup4>=4.12.0",
    "httpx>=0.25.0",
    "pydantic>=2.5.0",
    "aiosqlite>=0.19.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.23.0",
    "ruff>=0.1.0",
]

[tool.ruff]
line-length = 100
target-version = "py311"
```

- [ ] **Step 3: Create requirements.txt**

```
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
playwright>=1.40.0
beautifulsoup4>=4.12.0
httpx>=0.25.0
pydantic>=2.5.0
aiosqlite>=0.19.0
pytest>=7.4.0
pytest-asyncio>=0.23.0
ruff>=0.1.0
```

- [ ] **Step 4: Create config.py**

```python
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
```

- [ ] **Step 5: Create models.py**

```python
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class BetType(str, Enum):
    WIN_DRAW_LOSS = "win_draw_loss"      # 胜平负
    HANDICAP = "handicap"                 # 让球盘
    OVER_UNDER = "over_under"            # 大小球
    CORRECT_SCORE = "correct_score"      # 比分
    BOTH_TEAMS_SCORE = "both_teams_score" # 双方进球


class RiskLevel(str, Enum):
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


class Match(BaseModel):
    id: str
    league: str
    home_team: str
    away_team: str
    match_time: datetime
    odds: dict[str, float]  # {"home": 1.85, "draw": 3.40, "away": 4.20}
    bet_type: BetType
    source: str
    scraped_at: datetime = Field(default_factory=datetime.now)


class BetRecommendation(BaseModel):
    match_id: str
    match_summary: str
    bet_type: BetType
    selection: str          # "home", "draw", "away", "over", "under", etc.
    odds: float
    stake: float           # Amount to bet (RMB)
    potential_return: float
    kelly_fraction: float  # Optimal fraction from Kelly
    ev_score: float        # Expected value score
    confidence: float      # 0-1 confidence score


class OptimizeRequest(BaseModel):
    budget: float = Field(gt=0, le=100000)
    risk_level: RiskLevel = RiskLevel.MODERATE
    bet_types: list[BetType] = Field(default_factory=list)
    max_matches: int = Field(default=5, ge=1, le=10)
    min_odds: float = Field(default=1.5, ge=1.0)
    max_odds: float = Field(default=20.0, le=100.0)


class OptimizeResponse(BaseModel):
    budget: float
    risk_level: RiskLevel
    recommendations: list[BetRecommendation]
    total_stake: float
    max_potential_return: float
    average_ev: float
    generated_at: datetime = Field(default_factory=datetime.now)
```

- [ ] **Step 6: Create main.py**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import matches, optimize, history

app = FastAPI(
    title="Odds Optimizer",
    description="竞彩赔率优化器 - 最优盈亏比投注方案",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(matches.router, prefix="/api/matches", tags=["matches"])
app.include_router(optimize.router, prefix="/api/optimize", tags=["optimize"])
app.include_router(history.router, prefix="/api/history", tags=["history"])


@app.get("/")
async def root():
    return {"message": "Odds Optimizer API", "docs": "/docs"}
```

- [ ] **Step 7: Create placeholder API routers**

```python
# backend/app/api/__init__.py
from . import matches, optimize, history
```

```python
# backend/app/api/matches.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_matches():
    return {"matches": [], "message": "Not implemented yet"}
```

```python
# backend/app/api/optimize.py
from fastapi import APIRouter

router = APIRouter()

@router.post("/")
async def optimize_budget():
    return {"recommendations": [], "message": "Not implemented yet"}
```

```python
# backend/app/api/history.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_history():
    return {"history": [], "message": "Not implemented yet"}
```

- [ ] **Step 8: Verify backend starts**

```bash
cd backend && uvicorn app.main:app --reload --port 8000
```

Expected: Server starts on http://localhost:8000, visit /docs to see Swagger UI.

- [ ] **Step 9: Commit**

```bash
git init && git add -A && git commit -m "feat: backend scaffold with FastAPI, models, and placeholder routers"
```

---

## Task 2: Kelly Criterion & EV Engine

**Files:**
- Create: `backend/app/engine/__init__.py`, `backend/app/engine/kelly.py`, `backend/app/engine/ev.py`, `backend/app/engine/optimizer.py`
- Test: `backend/tests/test_kelly.py`, `backend/tests/test_optimizer.py`

- [ ] **Step 1: Write failing test for Kelly Criterion**

```python
# backend/tests/test_kelly.py
import pytest
from app.engine.kelly import kelly_criterion, fractional_kelly


class TestKellyCriterion:
    def test_positive_edge(self):
        # Win prob 60%, odds 2.0 → positive edge
        result = kelly_criterion(win_prob=0.6, odds=2.0)
        assert result > 0
        assert result == pytest.approx(0.2, rel=1e-2)  # 20% of bankroll

    def test_no_edge(self):
        # Win prob 50%, odds 2.0 → break even, no edge
        result = kelly_criterion(win_prob=0.5, odds=2.0)
        assert result == pytest.approx(0.0, abs=1e-2)

    def test_negative_edge(self):
        # Win prob 40%, odds 2.0 → negative edge
        result = kelly_criterion(win_prob=0.4, odds=2.0)
        assert result < 0

    def test_high_odds_low_prob(self):
        # Win prob 10%, odds 10.0 → small positive edge
        result = kelly_criterion(win_prob=0.1, odds=10.0)
        assert result > 0

    def test_invalid_odds(self):
        with pytest.raises(ValueError):
            kelly_criterion(win_prob=0.5, odds=1.0)

    def test_invalid_prob(self):
        with pytest.raises(ValueError):
            kelly_criterion(win_prob=0.0, odds=2.0)


class TestFractionalKelly:
    def test_half_kelly(self):
        full = kelly_criterion(win_prob=0.6, odds=2.0)
        half = fractional_kelly(win_prob=0.6, odds=2.0, fraction=0.5)
        assert half == pytest.approx(full * 0.5, rel=1e-2)

    def test_quarter_kelly(self):
        full = kelly_criterion(win_prob=0.6, odds=2.0)
        quarter = fractional_kelly(win_prob=0.6, odds=2.0, fraction=0.25)
        assert quarter == pytest.approx(full * 0.25, rel=1e-2)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd backend && python -m pytest tests/test_kelly.py -v
```

Expected: FAIL with "ModuleNotFoundError: No module named 'app.engine.kelly'"

- [ ] **Step 3: Implement Kelly Criterion**

```python
# backend/app/engine/__init__.py
from .kelly import kelly_criterion, fractional_kelly
from .ev import expected_value, ev_score
from .optimizer import optimize_budget
```

```python
# backend/app/engine/kelly.py
"""Kelly Criterion calculator for optimal bet sizing."""


def kelly_criterion(win_prob: float, odds: float) -> float:
    """
    Calculate optimal Kelly fraction.
    
    f* = (p * b - q) / b
    where:
        p = probability of winning
        q = 1 - p (probability of losing)
        b = odds - 1 (net odds received on the bet)
    
    Args:
        win_prob: Estimated probability of winning (0, 1]
        odds: Decimal odds (must be > 1)
    
    Returns:
        Optimal fraction of bankroll to bet (can be negative = don't bet)
    """
    if odds <= 1.0:
        raise ValueError(f"Odds must be > 1.0, got {odds}")
    if win_prob <= 0 or win_prob >= 1:
        raise ValueError(f"Win probability must be in (0, 1), got {win_prob}")
    
    b = odds - 1.0
    q = 1.0 - win_prob
    
    return (win_prob * b - q) / b


def fractional_kelly(win_prob: float, odds: float, fraction: float = 0.5) -> float:
    """
    Apply fractional Kelly for reduced variance.
    
    Uses a fraction of the full Kelly bet to reduce volatility
    while maintaining positive expected value.
    
    Args:
        win_prob: Estimated probability of winning
        odds: Decimal odds
        fraction: Kelly fraction to use (0, 1], default 0.5 (half Kelly)
    
    Returns:
        Reduced Kelly fraction
    """
    full_kelly = kelly_criterion(win_prob, odds)
    return full_kelly * fraction
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd backend && python -m pytest tests/test_kelly.py -v
```

Expected: All 9 tests PASS

- [ ] **Step 5: Write failing test for EV Calculator**

```python
# backend/tests/test_ev.py
import pytest
from app.engine.ev import expected_value, ev_score


class TestExpectedValue:
    def test_positive_ev(self):
        # 60% win at 2.0 odds → EV = 0.6*2 - 1 = 0.2
        ev = expected_value(win_prob=0.6, odds=2.0, stake=100)
        assert ev == pytest.approx(20.0, rel=1e-2)

    def test_zero_ev(self):
        # 50% win at 2.0 odds → EV = 0
        ev = expected_value(win_prob=0.5, odds=2.0, stake=100)
        assert ev == pytest.approx(0.0, abs=1e-2)

    def test_negative_ev(self):
        # 40% win at 2.0 odds → EV = -0.2
        ev = expected_value(win_prob=0.4, odds=2.0, stake=100)
        assert ev == pytest.approx(-20.0, rel=1e-2)


class TestEVScore:
    def test_ranking(self):
        # Higher EV score should rank better
        score_a = ev_score(win_prob=0.6, odds=2.0)
        score_b = ev_score(win_prob=0.5, odds=2.0)
        assert score_a > score_b

    def test_high_odds_bonus(self):
        # Higher odds with same prob should score higher
        score_low = ev_score(win_prob=0.3, odds=3.0)
        score_high = ev_score(win_prob=0.3, odds=5.0)
        assert score_high > score_low
```

- [ ] **Step 6: Run test to verify it fails**

```bash
cd backend && python -m pytest tests/test_ev.py -v
```

Expected: FAIL with "ModuleNotFoundError: No module named 'app.engine.ev'"

- [ ] **Step 7: Implement EV Calculator**

```python
# backend/app/engine/ev.py
"""Expected value calculations for betting analysis."""


def expected_value(win_prob: float, odds: float, stake: float = 1.0) -> float:
    """
    Calculate expected value of a bet.
    
    EV = (win_prob * odds * stake) - stake
       = stake * (win_prob * odds - 1)
    
    Args:
        win_prob: Probability of winning
        odds: Decimal odds
        stake: Amount bet
    
    Returns:
        Expected profit/loss
    """
    return stake * (win_prob * odds - 1.0)


def ev_score(win_prob: float, odds: float) -> float:
    """
    Calculate EV-based score for ranking bets.
    
    Combines expected value with odds magnitude to favor
    higher-odds bets with positive EV (your core requirement).
    
    Score = EV * log(odds)
    
    This prioritizes bets that are:
    1. Positive EV (mathematically profitable)
    2. Higher odds (more upside potential)
    
    Args:
        win_prob: Probability of winning
        odds: Decimal odds
    
    Returns:
        Score for ranking (higher = better)
    """
    import math
    ev = win_prob * odds - 1.0  # EV per unit
    if ev <= 0:
        return -1.0  # Penalize negative EV bets
    return ev * math.log(odds)
```

- [ ] **Step 8: Run EV tests**

```bash
cd backend && python -m pytest tests/test_ev.py -v
```

Expected: All tests PASS

- [ ] **Step 9: Write failing test for Budget Optimizer**

```python
# backend/tests/test_optimizer.py
import pytest
from datetime import datetime
from app.engine.optimizer import optimize_budget
from app.models import Match, BetType


@pytest.fixture
def sample_matches():
    return [
        Match(
            id="m1",
            league="英超",
            home_team="利物浦",
            away_team="曼城",
            match_time=datetime(2025, 1, 15, 20, 0),
            odds={"home": 2.10, "draw": 3.40, "away": 3.20},
            bet_type=BetType.WIN_DRAW_LOSS,
            source="test",
        ),
        Match(
            id="m2",
            league="西甲",
            home_team="巴萨",
            away_team="皇马",
            match_time=datetime(2025, 1, 15, 22, 0),
            odds={"home": 1.90, "draw": 3.60, "away": 3.80},
            bet_type=BetType.WIN_DRAW_LOSS,
            source="test",
        ),
        Match(
            id="m3",
            league="德甲",
            home_team="拜仁",
            away_team="多特",
            match_time=datetime(2025, 1, 15, 21, 0),
            odds={"home": 1.60, "draw": 4.00, "away": 5.00},
            bet_type=BetType.WIN_DRAW_LOSS,
            source="test",
        ),
    ]


class TestOptimizeBudget:
    def test_returns_recommendations(self, sample_matches):
        result = optimize_budget(
            matches=sample_matches,
            budget=500,
            risk_level="moderate",
        )
        assert len(result) > 0
        assert len(result) <= 5  # max_matches default

    def test_respects_budget(self, sample_matches):
        result = optimize_budget(
            matches=sample_matches,
            budget=500,
            risk_level="moderate",
        )
        total_stake = sum(r.stake for r in result)
        assert total_stake <= 500

    def test_budget_100(self, sample_matches):
        result = optimize_budget(
            matches=sample_matches,
            budget=100,
            risk_level="conservative",
        )
        total_stake = sum(r.stake for r in result)
        assert total_stake <= 100

    def test_aggressive_risk(self, sample_matches):
        result = optimize_budget(
            matches=sample_matches,
            budget=500,
            risk_level="aggressive",
        )
        # Aggressive should allocate more per bet
        assert len(result) > 0

    def test_empty_matches(self):
        result = optimize_budget(
            matches=[],
            budget=500,
            risk_level="moderate",
        )
        assert result == []
```

- [ ] **Step 10: Run test to verify it fails**

```bash
cd backend && python -m pytest tests/test_optimizer.py -v
```

Expected: FAIL with "ModuleNotFoundError: No module named 'app.engine.optimizer'"

- [ ] **Step 11: Implement Budget Optimizer**

```python
# backend/app/engine/optimizer.py
"""Budget optimization algorithm using Kelly Criterion."""

import math
from app.models import Match, BetRecommendation, BetType
from app.engine.kelly import kelly_criterion, fractional_kelly
from app.engine.ev import ev_score


# Risk multipliers for fractional Kelly
RISK_FRACTIONS = {
    "conservative": 0.25,  # Quarter Kelly
    "moderate": 0.5,       # Half Kelly
    "aggressive": 0.75,    # Three-quarter Kelly
}

# Estimated win probabilities based on odds (implied probability)
def implied_probability(odds: float) -> float:
    """Convert decimal odds to implied probability."""
    return 1.0 / odds


def estimate_true_probability(odds: float, margin: float = 0.05) -> float:
    """
    Estimate true probability from odds.
    
    Bookmakers add margin (~5% typically).
    We estimate true prob = implied_prob * (1 - margin).
    """
    implied = implied_probability(odds)
    return implied * (1 - margin)


def optimize_budget(
    matches: list[Match],
    budget: float,
    risk_level: str = "moderate",
    max_matches: int = 5,
    min_odds: float = 1.5,
    max_odds: float = 20.0,
) -> list[BetRecommendation]:
    """
    Generate optimal betting plan for given budget.
    
    Algorithm:
    1. Score each possible bet by EV * log(odds)
    2. Rank by score (highest first)
    3. Allocate budget using Kelly fractions
    4. Apply risk adjustment
    
    Args:
        matches: Available matches with odds
        budget: Total budget in RMB
        risk_level: "conservative", "moderate", or "aggressive"
        max_matches: Maximum number of matches to include
        min_odds: Minimum odds threshold
        max_odds: Maximum odds threshold
    
    Returns:
        List of betting recommendations
    """
    if not matches:
        return []
    
    fraction = RISK_FRACTIONS.get(risk_level, 0.5)
    candidates = []
    
    for match in matches:
        for selection, odds in match.odds.items():
            if odds < min_odds or odds > max_odds:
                continue
            
            true_prob = estimate_true_probability(odds)
            kelly_f = kelly_criterion(true_prob, odds)
            
            if kelly_f <= 0:
                continue  # Skip negative EV bets
            
            score = ev_score(true_prob, odds)
            
            candidates.append({
                "match": match,
                "selection": selection,
                "odds": odds,
                "true_prob": true_prob,
                "kelly_fraction": kelly_f,
                "score": score,
            })
    
    # Sort by score (highest = best risk-reward)
    candidates.sort(key=lambda x: x["score"], reverse=True)
    
    # Take top N
    top_candidates = candidates[:max_matches]
    
    # Allocate budget using fractional Kelly
    recommendations = []
    remaining_budget = budget
    
    for candidate in top_candidates:
        if remaining_budget <= 0:
            break
        
        # Calculate stake
        optimal_stake = budget * candidate["kelly_fraction"] * fraction
        stake = min(optimal_stake, remaining_budget)
        
        if stake < 1.0:  # Minimum bet
            continue
        
        potential_return = stake * candidate["odds"]
        
        recommendations.append(BetRecommendation(
            match_id=candidate["match"].id,
            match_summary=f"{candidate['match'].home_team} vs {candidate['match'].away_team}",
            bet_type=BetType.WIN_DRAW_LOSS,
            selection=candidate["selection"],
            odds=candidate["odds"],
            stake=round(stake, 2),
            potential_return=round(potential_return, 2),
            kelly_fraction=round(candidate["kelly_fraction"], 4),
            ev_score=round(candidate["score"], 4),
            confidence=round(candidate["true_prob"], 4),
        ))
        
        remaining_budget -= stake
    
    return recommendations
```

- [ ] **Step 12: Run optimizer tests**

```bash
cd backend && python -m pytest tests/test_optimizer.py -v
```

Expected: All 5 tests PASS

- [ ] **Step 13: Commit**

```bash
git add -A && git commit -m "feat: Kelly Criterion engine, EV calculator, and budget optimizer"
```

---

## Task 3: Odds Scraper (Playwright)

**Files:**
- Create: `backend/app/scrapers/__init__.py`, `backend/app/scrapers/base.py`, `backend/app/scrapers/aoke.py`, `backend/app/scrapers/parser.py`
- Test: `backend/tests/test_scraper.py`

- [ ] **Step 1: Write failing test for parser**

```python
# backend/tests/test_scraper.py
import pytest
from app.scrapers.parser import parse_odds_page, parse_match_row


class TestParseMatchRow:
    def test_parse_simple_row(self):
        html = """
        <tr>
            <td>英超</td>
            <td>利物浦</td>
            <td>曼城</td>
            <td>2025-01-15 20:00</td>
            <td>2.10</td>
            <td>3.40</td>
            <td>3.20</td>
        </tr>
        """
        result = parse_match_row(html)
        assert result is not None
        assert result["league"] == "英超"
        assert result["home_team"] == "利物浦"
        assert result["away_team"] == "曼城"
        assert result["odds"]["home"] == 2.10
        assert result["odds"]["draw"] == 3.40
        assert result["odds"]["away"] == 3.20

    def test_returns_none_for_invalid(self):
        result = parse_match_row("<div>not a match</div>")
        assert result is None
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd backend && python -m pytest tests/test_scraper.py -v
```

Expected: FAIL with import error

- [ ] **Step 3: Implement parser**

```python
# backend/app/scrapers/__init__.py
from .base import BaseScraper
from .aoke import AokeScraper
```

```python
# backend/app/scrapers/base.py
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
```

```python
# backend/app/scrapers/parser.py
"""HTML parser for odds data."""

from bs4 import BeautifulSoup
import re
from datetime import datetime


def parse_odds_page(html: str) -> list[dict]:
    """Parse a full odds page HTML into match data."""
    soup = BeautifulSoup(html, "html.parser")
    matches = []
    
    # Find match rows (adjust selectors based on actual site structure)
    rows = soup.find_all("tr", class_=re.compile(r"match|row", re.I))
    
    for row in rows:
        match_data = parse_match_row(str(row))
        if match_data:
            matches.append(match_data)
    
    return matches


def parse_match_row(html: str) -> dict | None:
    """
    Parse a single match row from HTML.
    
    Returns dict with keys: league, home_team, away_team, match_time, odds
    """
    soup = BeautifulSoup(html, "html.parser")
    cells = soup.find_all(["td", "div"])
    
    if len(cells) < 7:
        return None
    
    try:
        league = cells[0].get_text(strip=True)
        home_team = cells[1].get_text(strip=True)
        away_team = cells[2].get_text(strip=True)
        match_time_str = cells[3].get_text(strip=True)
        
        # Parse odds
        home_odds = float(cells[4].get_text(strip=True))
        draw_odds = float(cells[5].get_text(strip=True))
        away_odds = float(cells[6].get_text(strip=True))
        
        # Parse time (try common formats)
        match_time = _parse_time(match_time_str)
        
        return {
            "league": league,
            "home_team": home_team,
            "away_team": away_team,
            "match_time": match_time,
            "odds": {
                "home": home_odds,
                "draw": draw_odds,
                "away": away_odds,
            },
        }
    except (ValueError, IndexError):
        return None


def _parse_time(time_str: str) -> datetime:
    """Try to parse various time formats."""
    formats = [
        "%Y-%m-%d %H:%M",
        "%Y/%m/%d %H:%M",
        "%m-%d %H:%M",
        "%m/%d %H:%M",
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(time_str, fmt)
        except ValueError:
            continue
    
    # Default to now if parsing fails
    return datetime.now()
```

- [ ] **Step 4: Run parser tests**

```bash
cd backend && python -m pytest tests/test_scraper.py -v
```

Expected: All tests PASS

- [ ] **Step 5: Implement Aoke scraper**

```python
# backend/app/scrapers/aoke.py
"""澳客网 odds scraper."""

import asyncio
from datetime import datetime
from playwright.async_api import async_playwright

from app.scrapers.base import BaseScraper
from app.scrapers.parser import parse_odds_page
from app.models import Match, BetType
from app.config import settings


class AokeScraper(BaseScraper):
    """Scraper for aoke8.com odds data."""
    
    BASE_URL = "https://www.aoke8.com/jczq/"
    
    async def fetch_matches(self) -> list[Match]:
        """Fetch today's football matches from 澳客网."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                await page.goto(self.BASE_URL, timeout=settings.SCRAPER_TIMEOUT * 1000)
                await page.wait_for_load_state("networkidle")
                
                # Get page content
                html = await page.content()
                
                # Parse matches
                raw_matches = parse_odds_page(html)
                
                matches = []
                for raw in raw_matches:
                    match = Match(
                        id=f"aoke_{hash(raw['home_team'] + raw['away_team'])}",
                        league=raw["league"],
                        home_team=raw["home_team"],
                        away_team=raw["away_team"],
                        match_time=raw["match_time"],
                        odds=raw["odds"],
                        bet_type=BetType.WIN_DRAW_LOSS,
                        source="aoke",
                        scraped_at=datetime.now(),
                    )
                    matches.append(match)
                
                return matches
                
            finally:
                await browser.close()
    
    async def fetch_match_detail(self, match_id: str) -> Match | None:
        """Fetch detailed odds for a specific match."""
        # TODO: Implement match detail page scraping
        return None
```

- [ ] **Step 6: Verify scraper compiles**

```bash
cd backend && python -c "from app.scrapers import AokeScraper; print('Scraper imports OK')"
```

Expected: "Scraper imports OK"

- [ ] **Step 7: Commit**

```bash
git add -A && git commit -m "feat: odds scraper with 澳客网 parser"
```

---

## Task 4: Database & Caching Layer

**Files:**
- Create: `backend/app/database.py`
- Modify: `backend/app/main.py` (add startup/shutdown)

- [ ] **Step 1: Create database module**

```python
# backend/app/database.py
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
```

- [ ] **Step 2: Update main.py with startup/shutdown**

```python
# backend/app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import matches, optimize, history
from app.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown


app = FastAPI(
    title="Odds Optimizer",
    description="竞彩赔率优化器 - 最优盈亏比投注方案",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(matches.router, prefix="/api/matches", tags=["matches"])
app.include_router(optimize.router, prefix="/api/optimize", tags=["optimize"])
app.include_router(history.router, prefix="/api/history", tags=["history"])


@app.get("/")
async def root():
    return {"message": "Odds Optimizer API", "docs": "/docs"}
```

- [ ] **Step 3: Verify database initializes**

```bash
cd backend && python -c "import asyncio; from app.database import init_db; asyncio.run(init_db()); print('DB initialized')"
```

Expected: "DB initialized" and `data/odds.db` file created

- [ ] **Step 4: Commit**

```bash
git add -A && git commit -m "feat: SQLite caching layer for odds data"
```

---

## Task 5: Wire Up API Endpoints

**Files:**
- Modify: `backend/app/api/matches.py`, `backend/app/api/optimize.py`, `backend/app/api/history.py`

- [ ] **Step 1: Implement matches endpoint**

```python
# backend/app/api/matches.py
from fastapi import APIRouter, HTTPException
from app.scrapers import AokeScraper
from app.database import cache_matches, get_cached_matches
from app.config import settings

router = APIRouter()


@router.get("/")
async def get_matches(refresh: bool = False):
    """Get today's matches with odds.
    
    Args:
        refresh: Force refresh from source (ignore cache)
    """
    # Try cache first
    if not refresh:
        cached = await get_cached_matches()
        if cached:
            return {
                "matches": [m.model_dump() for m in cached],
                "source": "cache",
                "count": len(cached),
            }
    
    # Fetch fresh data
    try:
        scraper = AokeScraper()
        matches = await scraper.fetch_matches()
        
        # Cache results
        await cache_matches(matches)
        
        return {
            "matches": [m.model_dump() for m in matches],
            "source": "live",
            "count": len(matches),
        }
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Scraper error: {str(e)}")


@router.get("/{match_id}")
async def get_match(match_id: str):
    """Get specific match details."""
    cached = await get_cached_matches(max_age_seconds=3600)
    for match in cached:
        if match.id == match_id:
            return match.model_dump()
    raise HTTPException(status_code=404, detail="Match not found")
```

- [ ] **Step 2: Implement optimize endpoint**

```python
# backend/app/api/optimize.py
from fastapi import APIRouter
from app.models import OptimizeRequest, OptimizeResponse
from app.engine.optimizer import optimize_budget
from app.database import get_cached_matches

router = APIRouter()


@router.post("/", response_model=OptimizeResponse)
async def optimize_budget_endpoint(request: OptimizeRequest):
    """Generate optimal betting plan for given budget."""
    # Get available matches
    matches = await get_cached_matches()
    
    if not matches:
        return OptimizeResponse(
            budget=request.budget,
            risk_level=request.risk_level,
            recommendations=[],
            total_stake=0,
            max_potential_return=0,
            average_ev=0,
        )
    
    # Filter by bet types if specified
    if request.bet_types:
        matches = [m for m in matches if m.bet_type in request.bet_types]
    
    # Run optimizer
    recommendations = optimize_budget(
        matches=matches,
        budget=request.budget,
        risk_level=request.risk_level.value,
        max_matches=request.max_matches,
        min_odds=request.min_odds,
        max_odds=request.max_odds,
    )
    
    total_stake = sum(r.stake for r in recommendations)
    max_return = sum(r.potential_return for r in recommendations)
    avg_ev = sum(r.ev_score for r in recommendations) / len(recommendations) if recommendations else 0
    
    return OptimizeResponse(
        budget=request.budget,
        risk_level=request.risk_level,
        recommendations=recommendations,
        total_stake=round(total_stake, 2),
        max_potential_return=round(max_return, 2),
        average_ev=round(avg_ev, 4),
    )
```

- [ ] **Step 3: Implement history endpoint**

```python
# backend/app/api/history.py
from fastapi import APIRouter
from app.database import get_bet_history

router = APIRouter()


@router.get("/")
async def get_history(limit: int = 50):
    """Get bet history."""
    history = await get_bet_history(limit)
    return {"history": history, "count": len(history)}
```

- [ ] **Step 4: Test API endpoints**

```bash
cd backend && uvicorn app.main:app --port 8000 &
sleep 2
curl http://localhost:8000/api/matches/
curl -X POST http://localhost:8000/api/optimize/ -H "Content-Type: application/json" -d '{"budget": 500}'
kill %1
```

Expected: JSON responses from both endpoints

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "feat: wire up API endpoints for matches, optimize, and history"
```

---

## Task 6: Frontend - React + Tailwind Setup

**Files:**
- Create: `frontend/` directory with Vite + React + Tailwind

- [ ] **Step 1: Initialize frontend project**

```bash
cd odds-optimizer
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
npm install -D tailwindcss @tailwindcss/vite
```

- [ ] **Step 2: Configure Tailwind**

```typescript
// frontend/vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
})
```

```css
/* frontend/src/index.css */
@import "tailwindcss";
```

- [ ] **Step 3: Create API client**

```typescript
// frontend/src/lib/api.ts
const API_BASE = '/api';

export interface Match {
  id: string;
  league: string;
  home_team: string;
  away_team: string;
  match_time: string;
  odds: Record<string, number>;
  bet_type: string;
  source: string;
}

export interface BetRecommendation {
  match_id: string;
  match_summary: string;
  bet_type: string;
  selection: string;
  odds: number;
  stake: number;
  potential_return: number;
  kelly_fraction: number;
  ev_score: number;
  confidence: number;
}

export interface OptimizeResponse {
  budget: number;
  risk_level: string;
  recommendations: BetRecommendation[];
  total_stake: number;
  max_potential_return: number;
  average_ev: number;
}

export async function fetchMatches(refresh = false): Promise<Match[]> {
  const res = await fetch(`${API_BASE}/matches/?refresh=${refresh}`);
  const data = await res.json();
  return data.matches || [];
}

export async function optimizeBudget(
  budget: number,
  riskLevel: string = 'moderate',
  maxMatches: number = 5
): Promise<OptimizeResponse> {
  const res = await fetch(`${API_BASE}/optimize/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      budget,
      risk_level: riskLevel,
      max_matches: maxMatches,
    }),
  });
  return res.json();
}
```

- [ ] **Step 4: Create MatchList component**

```tsx
// frontend/src/components/MatchList.tsx
import { Match } from '../lib/api';

interface MatchListProps {
  matches: Match[];
  loading: boolean;
}

export function MatchList({ matches, loading }: MatchListProps) {
  if (loading) {
    return (
      <div className="animate-pulse space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-24 bg-gray-200 rounded-lg" />
        ))}
      </div>
    );
  }

  if (matches.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        暂无比赛数据，请点击刷新
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {matches.map((match) => (
        <div
          key={match.id}
          className="bg-white rounded-lg shadow p-4 border border-gray-100"
        >
          <div className="flex justify-between items-start mb-2">
            <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
              {match.league}
            </span>
            <span className="text-xs text-gray-400">
              {new Date(match.match_time).toLocaleString('zh-CN')}
            </span>
          </div>
          <div className="flex justify-between items-center">
            <div className="font-medium">{match.home_team}</div>
            <div className="text-gray-400 text-sm">vs</div>
            <div className="font-medium">{match.away_team}</div>
          </div>
          <div className="flex gap-2 mt-3">
            {Object.entries(match.odds).map(([key, value]) => (
              <div
                key={key}
                className="flex-1 text-center bg-blue-50 rounded py-1"
              >
                <div className="text-xs text-gray-500">
                  {key === 'home' ? '主胜' : key === 'draw' ? '平' : '客胜'}
                </div>
                <div className="font-mono font-bold text-blue-600">
                  {value.toFixed(2)}
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
```

- [ ] **Step 5: Create BudgetInput component**

```tsx
// frontend/src/components/BudgetInput.tsx
import { useState } from 'react';

interface BudgetInputProps {
  onOptimize: (budget: number, riskLevel: string) => void;
  loading: boolean;
}

const PRESETS = [100, 200, 500, 1000, 2000];
const RISK_LEVELS = [
  { value: 'conservative', label: '保守', desc: '四分之一凯利' },
  { value: 'moderate', label: '适中', desc: '半凯利' },
  { value: 'aggressive', label: '激进', desc: '四分之三凯利' },
];

export function BudgetInput({ onOptimize, loading }: BudgetInputProps) {
  const [budget, setBudget] = useState(500);
  const [riskLevel, setRiskLevel] = useState('moderate');

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-lg font-semibold mb-4">预算设置</h2>
      
      <div className="mb-4">
        <label className="block text-sm text-gray-600 mb-2">投注金额 (元)</label>
        <div className="flex gap-2 mb-2">
          {PRESETS.map((preset) => (
            <button
              key={preset}
              onClick={() => setBudget(preset)}
              className={`px-3 py-1 rounded text-sm ${
                budget === preset
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {preset}
            </button>
          ))}
        </div>
        <input
          type="number"
          value={budget}
          onChange={(e) => setBudget(Number(e.target.value))}
          className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          min={1}
          max={100000}
        />
      </div>

      <div className="mb-4">
        <label className="block text-sm text-gray-600 mb-2">风险偏好</label>
        <div className="grid grid-cols-3 gap-2">
          {RISK_LEVELS.map((level) => (
            <button
              key={level.value}
              onClick={() => setRiskLevel(level.value)}
              className={`p-3 rounded-lg text-center ${
                riskLevel === level.value
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              <div className="font-medium">{level.label}</div>
              <div className="text-xs opacity-75">{level.desc}</div>
            </button>
          ))}
        </div>
      </div>

      <button
        onClick={() => onOptimize(budget, riskLevel)}
        disabled={loading}
        className="w-full bg-green-600 text-white py-3 rounded-lg font-semibold hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? '计算中...' : '生成最优方案'}
      </button>
    </div>
  );
}
```

- [ ] **Step 6: Create PlanCard component**

```tsx
// frontend/src/components/PlanCard.tsx
import { BetRecommendation } from '../lib/api';

interface PlanCardProps {
  recommendations: BetRecommendation[];
  totalStake: number;
  maxReturn: number;
}

export function PlanCard({ recommendations, totalStake, maxReturn }: PlanCardProps) {
  if (recommendations.length === 0) return null;

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-lg font-semibold mb-4">最优投注方案</h2>
      
      <div className="grid grid-cols-3 gap-4 mb-6 text-center">
        <div className="bg-green-50 rounded-lg p-3">
          <div className="text-2xl font-bold text-green-600">
            ¥{totalStake.toFixed(0)}
          </div>
          <div className="text-xs text-gray-500">总投注</div>
        </div>
        <div className="bg-blue-50 rounded-lg p-3">
          <div className="text-2xl font-bold text-blue-600">
            ¥{maxReturn.toFixed(0)}
          </div>
          <div className="text-xs text-gray-500">最高回报</div>
        </div>
        <div className="bg-purple-50 rounded-lg p-3">
          <div className="text-2xl font-bold text-purple-600">
            {((maxReturn / totalStake - 1) * 100).toFixed(0)}%
          </div>
          <div className="text-xs text-gray-500">潜在收益率</div>
        </div>
      </div>

      <div className="space-y-3">
        {recommendations.map((rec, index) => (
          <div
            key={`${rec.match_id}-${rec.selection}`}
            className="border rounded-lg p-4 hover:border-blue-300 transition-colors"
          >
            <div className="flex justify-between items-start mb-2">
              <div className="flex items-center gap-2">
                <span className="w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-xs font-bold">
                  {index + 1}
                </span>
                <span className="font-medium">{rec.match_summary}</span>
              </div>
              <span className="text-xs bg-gray-100 px-2 py-1 rounded">
                {rec.selection === 'home' ? '主胜' : rec.selection === 'draw' ? '平' : '客胜'}
              </span>
            </div>
            
            <div className="grid grid-cols-4 gap-2 text-sm">
              <div>
                <div className="text-gray-500">赔率</div>
                <div className="font-mono font-bold text-blue-600">{rec.odds.toFixed(2)}</div>
              </div>
              <div>
                <div className="text-gray-500">投注</div>
                <div className="font-mono">¥{rec.stake.toFixed(0)}</div>
              </div>
              <div>
                <div className="text-gray-500">潜在回报</div>
                <div className="font-mono text-green-600">¥{rec.potential_return.toFixed(0)}</div>
              </div>
              <div>
                <div className="text-gray-500">EV评分</div>
                <div className="font-mono">{rec.ev_score.toFixed(2)}</div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
```

- [ ] **Step 7: Create main App**

```tsx
// frontend/src/App.tsx
import { useState, useEffect } from 'react';
import { MatchList } from './components/MatchList';
import { BudgetInput } from './components/BudgetInput';
import { PlanCard } from './components/PlanCard';
import { fetchMatches, optimizeBudget, Match, BetRecommendation } from './lib/api';

function App() {
  const [matches, setMatches] = useState<Match[]>([]);
  const [recommendations, setRecommendations] = useState<BetRecommendation[]>([]);
  const [loading, setLoading] = useState(false);
  const [optimizing, setOptimizing] = useState(false);
  const [totalStake, setTotalStake] = useState(0);
  const [maxReturn, setMaxReturn] = useState(0);

  useEffect(() => {
    loadMatches();
  }, []);

  async function loadMatches(refresh = false) {
    setLoading(true);
    try {
      const data = await fetchMatches(refresh);
      setMatches(data);
    } catch (err) {
      console.error('Failed to load matches:', err);
    } finally {
      setLoading(false);
    }
  }

  async function handleOptimize(budget: number, riskLevel: string) {
    setOptimizing(true);
    try {
      const result = await optimizeBudget(budget, riskLevel);
      setRecommendations(result.recommendations);
      setTotalStake(result.total_stake);
      setMaxReturn(result.max_potential_return);
    } catch (err) {
      console.error('Optimization failed:', err);
    } finally {
      setOptimizing(false);
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-gray-900">
            竞彩赔率优化器
          </h1>
          <p className="text-sm text-gray-500">
            基于凯利准则的最优盈亏比投注方案
          </p>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left: Matches */}
          <div className="lg:col-span-2">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold">今日赛事</h2>
              <button
                onClick={() => loadMatches(true)}
                disabled={loading}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 disabled:opacity-50"
              >
                {loading ? '加载中...' : '刷新数据'}
              </button>
            </div>
            <MatchList matches={matches} loading={loading} />
          </div>

          {/* Right: Budget & Plan */}
          <div className="space-y-6">
            <BudgetInput onOptimize={handleOptimize} loading={optimizing} />
            <PlanCard
              recommendations={recommendations}
              totalStake={totalStake}
              maxReturn={maxReturn}
            />
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
```

- [ ] **Step 8: Verify frontend builds**

```bash
cd frontend && npm run build
```

Expected: Build succeeds with no errors

- [ ] **Step 9: Commit**

```bash
git add -A && git commit -m "feat: React frontend with match list, budget input, and plan display"
```

---

## Task 7: Integration Testing & Polish

**Files:**
- Create: `docker-compose.yml`, `README.md`

- [ ] **Step 1: Create docker-compose.yml**

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
      - ./data:/app/data
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: npm run dev -- --host 0.0.0.0
    depends_on:
      - backend
```

- [ ] **Step 2: Create backend Dockerfile**

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install chromium

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 3: Create frontend Dockerfile**

```dockerfile
# frontend/Dockerfile
FROM node:20-slim

WORKDIR /app

COPY package*.json .
RUN npm install

COPY . .

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
```

- [ ] **Step 4: Run all tests**

```bash
cd backend && python -m pytest tests/ -v
```

Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "feat: Docker setup and integration tests"
```

---

## Task 8: README & Documentation

- [ ] **Step 1: Create README.md**

```markdown
# 竞彩赔率优化器 (Odds Optimizer)

基于凯利准则的竞彩投注优化工具，自动计算最优盈亏比投注方案。

## 功能特点

- 实时抓取竞彩赔率数据
- 基于凯利准则计算最优投注比例
- 支持多种风险偏好（保守/适中/激进）
- 按预算生成最优投注组合
- EV评分排序，优先推荐高赔率正EV赛事

## 快速开始

### 使用 Docker

```bash
docker-compose up
```

访问 http://localhost:5173

### 本地开发

**后端：**

```bash
cd backend
pip install -r requirements.txt
playwright install chromium
uvicorn app.main:app --reload
```

**前端：**

```bash
cd frontend
npm install
npm run dev
```

## API 文档

启动后端后访问 http://localhost:8000/docs

## 核心算法

### 凯利准则 (Kelly Criterion)

```
f* = (p * b - q) / b
```

- `f*` = 最优投注比例
- `p` = 胜率估计
- `b` = 赔率 - 1
- `q` = 1 - p

### EV评分

```
score = EV * log(odds)
```

优先推荐：
1. 正期望值 (EV > 0)
2. 高赔率 (更多上行空间)

## 风险说明

本工具仅供参考，不构成投注建议。彩票有风险，投注需谨慎。
```

- [ ] **Step 2: Final commit**

```bash
git add -A && git commit -m "docs: add README with setup instructions and algorithm explanation"
```

---

## Summary

**Total Tasks:** 8
**Estimated Time:** 4-6 hours for experienced developer

**Key Deliverables:**
1. ✅ FastAPI backend with odds scraping
2. ✅ Kelly Criterion optimization engine
3. ✅ SQLite caching layer
4. ✅ React + Tailwind frontend
5. ✅ Docker deployment setup
6. ✅ Complete API documentation

**Next Steps After MVP:**
1. Add more data sources (50.com, 雷速体育)
2. Implement historical odds tracking
3. Add user authentication for bet history
4. Real-time odds updates via WebSocket
5. Mobile-responsive design
