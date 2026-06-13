"""投资大师 API 端点"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional

from app.masters.kelly import KellyMaster
from app.masters.warren import WarrenMaster
from app.masters.george import GeorgeMaster
from app.database import get_cached_matches


router = APIRouter()


# 可用的大师实例
MASTERS = {
    "kelly": KellyMaster(),
    "warren": WarrenMaster(),
    "george": GeorgeMaster(),
}


class MasterRecommendRequest(BaseModel):
    """大师推荐请求"""
    budget: float = Field(gt=0, le=100000, description="预算金额")


class MasterCompareRequest(BaseModel):
    """大师对比请求"""
    budget: float = Field(gt=0, le=100000, description="预算金额")
    masters: Optional[List[str]] = Field(
        default=None,
        description="要对比的大师列表，不传则对比所有大师"
    )


@router.get("/")
async def list_masters():
    """获取所有大师列表"""
    masters_info = []
    for master_id, master in MASTERS.items():
        info = master.to_dict()
        info["id"] = master_id
        masters_info.append(info)

    return {
        "masters": masters_info,
        "count": len(masters_info),
    }


@router.post("/{master_id}/recommend")
async def get_master_recommendation(master_id: str, request: MasterRecommendRequest):
    """获取指定大师的推荐方案"""
    if master_id not in MASTERS:
        raise HTTPException(
            status_code=404,
            detail=f"大师 '{master_id}' 不存在。可用: {list(MASTERS.keys())}"
        )

    master = MASTERS[master_id]

    # 获取赛事数据
    matches = await get_cached_matches()
    if not matches:
        # 尝试刷新
        from app.scrapers.sporttery import SportteryScraper
        from app.scrapers.mock import get_mock_matches
        from app.database import cache_matches

        try:
            scraper = SportteryScraper()
            matches = await scraper.fetch_matches()
            if matches:
                await cache_matches(matches)
        except Exception:
            pass

        if not matches:
            matches = get_mock_matches()
            await cache_matches(matches)

    # 过滤未来的赛事
    from datetime import datetime
    now = datetime.now()
    matches = [m for m in matches if m.match_time > now]

    # 获取推荐
    recommendations = master.select_bets(matches, request.budget)

    # 统计
    total_stake = sum(r.stake for r in recommendations)
    max_return = sum(r.potential_return for r in recommendations)

    return {
        "master": master.to_dict(),
        "master_id": master_id,
        "budget": request.budget,
        "recommendations": [r.model_dump() for r in recommendations],
        "total_stake": round(total_stake, 2),
        "max_potential_return": round(max_return, 2),
        "count": len(recommendations),
        "explanation": master.explain_decision(recommendations),
    }


@router.post("/compare")
async def compare_masters(request: MasterCompareRequest):
    """对比多个大师的方案"""
    masters_to_compare = request.masters or list(MASTERS.keys())

    # 验证大师ID
    invalid = [m for m in masters_to_compare if m not in MASTERS]
    if invalid:
        raise HTTPException(
            status_code=400,
            detail=f"无效的大师ID: {invalid}。可用: {list(MASTERS.keys())}"
        )

    # 获取赛事数据
    matches = await get_cached_matches()
    if not matches:
        from app.scrapers.mock import get_mock_matches
        from app.database import cache_matches
        matches = get_mock_matches()
        await cache_matches(matches)

    # 过滤未来的赛事
    from datetime import datetime
    now = datetime.now()
    matches = [m for m in matches if m.match_time > now]

    # 对比结果
    comparisons = []
    for master_id in masters_to_compare:
        master = MASTERS[master_id]
        recommendations = master.select_bets(matches, request.budget)

        total_stake = sum(r.stake for r in recommendations)
        max_return = sum(r.potential_return for r in recommendations)

        comparisons.append({
            "master_id": master_id,
            "master": master.to_dict(),
            "bet_count": len(recommendations),
            "total_stake": round(total_stake, 2),
            "max_return": round(max_return, 2),
            "roi_percent": round((max_return / total_stake - 1) * 100, 1) if total_stake > 0 else 0,
            "risk_level": master.get_risk_level(),
        })

    return {
        "budget": request.budget,
        "comparisons": comparisons,
        "match_count": len(matches),
    }
