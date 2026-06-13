"""索罗斯 - 反向思维策略"""

from typing import List
from app.masters import MasterStrategy
from app.models import Match, BetRecommendation, BetType
from app.engine.ev import ev_score


MIN_STAKE = 2.0
STAKE_UNIT = 2.0


def implied_probability(odds: float) -> float:
    return 1.0 / odds


def round_stake(amount: float) -> float:
    if amount < MIN_STAKE:
        return 0.0
    return round(amount / STAKE_UNIT) * STAKE_UNIT


class GeorgeMaster(MasterStrategy):
    """索罗斯 - 反身性理论大师"""

    name = "索罗斯"
    name_en = "george"
    emoji = "🦅"
    title = "反身性大师"
    philosophy = "市场是错的，寻找被低估的机会"
    personality = "激进、反向思维、大胆"
    quotes = [
        "在危机中寻找机会",
        "市场总是错的，关键是你什么时候对",
        "冒险才能改变命运",
        "当所有人都往左跑时，我往右看",
    ]

    def select_bets(
        self,
        matches: List[Match],
        budget: float,
    ) -> List[BetRecommendation]:
        """
        索罗斯策略：
        - 只选高赔率冷门（5倍+）
        - 1-3 注集中投资
        - 寻找"被低估"的选项
        - 高风险高回报
        """
        if not matches or budget < MIN_STAKE:
            return []

        # 策略参数
        min_odds = 5.0
        max_bets = 3

        # 收集高赔率候选
        candidates = []
        for match in matches:
            for selection, odds in match.odds.items():
                if odds >= min_odds:
                    implied = implied_probability(odds)
                    score = ev_score(implied, odds)

                    candidates.append({
                        "match": match,
                        "selection": selection,
                        "odds": odds,
                        "score": score,
                    })

        if not candidates:
            return []

        # 按得分排序，取前几个
        candidates.sort(key=lambda x: x["score"], reverse=True)
        selected = candidates[:max_bets]

        # 集中投资：70% 给最高赔率，剩余平分
        allocations = []
        if len(selected) == 1:
            allocations.append({"candidate": selected[0], "weight": 1.0})
        elif len(selected) == 2:
            allocations.append({"candidate": selected[0], "weight": 0.7})
            allocations.append({"candidate": selected[1], "weight": 0.3})
        else:  # 3个
            allocations.append({"candidate": selected[0], "weight": 0.6})
            allocations.append({"candidate": selected[1], "weight": 0.25})
            allocations.append({"candidate": selected[2], "weight": 0.15})

        # 分配预算
        result = []
        for allocation in allocations:
            candidate = allocation["candidate"]
            raw_stake = budget * allocation["weight"]
            stake = round_stake(raw_stake)

            if stake < MIN_STAKE:
                continue

            potential_return = stake * candidate["odds"]

            result.append(BetRecommendation(
                match_id=candidate["match"].id,
                match_summary=f"{candidate['match'].home_team} vs {candidate['match'].away_team}",
                bet_type=BetType.WIN_DRAW_LOSS,
                selection=candidate["selection"],
                odds=candidate["odds"],
                stake=stake,
                potential_return=round(potential_return, 2),
                kelly_fraction=0,
                ev_score=round(candidate["score"], 4),
                confidence=round(1.0 / candidate["odds"], 4),
            ))

        return result

    def explain_decision(self, recommendations: List[BetRecommendation]) -> str:
        """索罗斯的解释"""
        if not recommendations:
            return (
                "索罗斯说：当前没有看到明显的市场错误定价。"
                "我只在确信市场错了的时候出手。耐心等待猎物。"
            )

        total_stake = sum(r.stake for r in recommendations)
        max_return = sum(r.potential_return for r in recommendations)
        top_odds = max(r.odds for r in recommendations)

        return (
            f"索罗斯的分析：\n\n"
            f"我发现了 {len(recommendations)} 个被市场低估的机会。"
            f"这些高赔率选项的真实概率被低估了。\n\n"
            f"策略特点：\n"
            f"• 总投注：¥{total_stake:.0f}（集中配置）\n"
            f"• 最高赔率：{top_odds:.1f}x\n"
            f"• 全中回报：¥{max_return:.0f}（{(max_return/total_stake-1)*100:.0f}% ROI）\n\n"
            f"这是高风险高回报的策略。我把大部分资金押在最被低估的机会上。"
            f"市场往往是错的，关键是抓住那个时刻。\n\n"
            f"⚠️ 风险提示：这是激进策略，可能全军覆没，也可能一战成名。"
        )

    def get_risk_level(self) -> int:
        """索罗斯策略风险等级：5星（极高）"""
        return 5
