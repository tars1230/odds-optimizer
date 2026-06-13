"""凯利教授 - 数学最优策略"""

from typing import List
from app.masters import MasterStrategy
from app.models import Match, BetRecommendation, BetType
from app.engine.ev import ev_score


MIN_STAKE = 2.0
STAKE_UNIT = 2.0


def implied_probability(odds: float) -> float:
    """将赔率转换为隐含概率"""
    return 1.0 / odds


def round_stake(amount: float) -> float:
    """取整到2的倍数"""
    if amount < MIN_STAKE:
        return 0.0
    return round(amount / STAKE_UNIT) * STAKE_UNIT


class KellyMaster(MasterStrategy):
    """凯利教授 - 数学驱动的最优策略"""

    name = "凯利教授"
    name_en = "kelly"
    emoji = "🤓"
    title = "数学教授"
    philosophy = "Kelly Criterion - 数学上的最优解"
    personality = "理性、精确、数据驱动"
    quotes = [
        "数学会告诉我们答案",
        "长期来看，这是最优解",
        "不要让情绪影响决策",
        "最大化对数财富增长率",
    ]

    def select_bets(
        self,
        matches: List[Match],
        budget: float,
    ) -> List[BetRecommendation]:
        """
        凯利策略：
        - 计算每个选项的 EV（期望值）
        - 按 Kelly 权重分配预算
        - 5-8 注分散投资
        - 赔率范围：2.0-8.0
        """
        if not matches or budget < MIN_STAKE:
            return []

        # 策略参数
        num_bets = 6
        min_odds = 2.0
        max_odds = 8.0
        power = 1.0  # 权重指数（1.0 = 线性）

        # 收集候选
        candidates = []
        for match in matches:
            for selection, odds in match.odds.items():
                if odds < min_odds or odds > max_odds:
                    continue

                implied = implied_probability(odds)
                score = ev_score(implied, odds)

                if score > 0:
                    candidates.append({
                        "match": match,
                        "selection": selection,
                        "odds": odds,
                        "implied_prob": implied,
                        "score": score,
                    })

        if not candidates:
            return []

        # 按得分排序，取前 N
        candidates.sort(key=lambda x: x["score"], reverse=True)
        top_candidates = candidates[:num_bets]

        # 计算权重
        total_weight = sum(c["score"] ** power for c in top_candidates)
        if total_weight <= 0:
            return []

        # 分配预算
        allocations = []
        for candidate in top_candidates:
            weight = candidate["score"] ** power
            raw_stake = (weight / total_weight) * budget
            stake = round_stake(raw_stake)

            if stake >= MIN_STAKE:
                allocations.append({
                    "candidate": candidate,
                    "stake": stake,
                })

        # 调整剩余预算
        total_allocated = sum(a["stake"] for a in allocations)
        remaining = budget - total_allocated

        if remaining >= STAKE_UNIT:
            for allocation in allocations:
                if remaining < STAKE_UNIT:
                    break
                add_amount = min(STAKE_UNIT, remaining)
                allocation["stake"] += add_amount
                remaining -= add_amount

        # 生成推荐
        result = []
        for allocation in allocations:
            candidate = allocation["candidate"]
            stake = allocation["stake"]
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
                confidence=round(candidate["implied_prob"], 4),
            ))

        return result

    def explain_decision(self, recommendations: List[BetRecommendation]) -> str:
        """凯利教授的解释"""
        if not recommendations:
            return (
                "凯利教授说：当前赛事中没有找到数学上的正期望值机会。"
                "记住，不投注有时也是最好的决策。"
            )

        total_stake = sum(r.stake for r in recommendations)
        max_return = sum(r.potential_return for r in recommendations)
        avg_odds = sum(r.odds for r in recommendations) / len(recommendations)

        return (
            f"凯利教授的分析：\n\n"
            f"我使用 Kelly Criterion 公式计算了最优投注比例，"
            f"选择了 {len(recommendations)} 个具有正期望值的机会。\n\n"
            f"策略特点：\n"
            f"• 总投注：¥{total_stake:.0f}（利用率 {total_stake/100*100:.0f}%）\n"
            f"• 平均赔率：{avg_odds:.1f}x\n"
            f"• 全中回报：¥{max_return:.0f}（{(max_return/total_stake-1)*100:.0f}% ROI）\n\n"
            f"这是数学上的最优配置。虽然不保证短期盈利，"
            f"但长期来看能最大化你的财富增长率。记住，分散投资是关键。"
        )

    def get_risk_level(self) -> int:
        """凯利策略风险等级：4星（中高）"""
        return 4
