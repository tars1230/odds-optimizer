"""巴菲特 - 价值投资策略"""

from typing import List
from app.masters import MasterStrategy
from app.models import Match, BetRecommendation, BetType


MIN_STAKE = 2.0
STAKE_UNIT = 2.0


def round_stake(amount: float) -> float:
    if amount < MIN_STAKE:
        return 0.0
    return round(amount / STAKE_UNIT) * STAKE_UNIT


class WarrenMaster(MasterStrategy):
    """巴菲特 - 价值投资大师"""

    name = "巴菲特"
    name_en = "warren"
    emoji = "👴"
    title = "价值猎手"
    philosophy = "只投资确定性高的机会"
    personality = "保守、耐心、长期主义"
    quotes = [
        "别人恐惧时我贪婪，但我只贪婪确定的",
        "第一条规则：不要亏钱",
        "复利是世界第八大奇迹",
        "投资的秘诀是：在别人贪婪时恐惧，在别人恐惧时贪婪",
    ]

    def select_bets(
        self,
        matches: List[Match],
        budget: float,
    ) -> List[BetRecommendation]:
        """
        巴菲特策略：
        - 只选低赔率高胜率（1.5-2.5倍）
        - 10-15 注超分散
        - 强队主场优先
        - 求稳不求爆
        """
        if not matches or budget < MIN_STAKE:
            return []

        # 策略参数
        min_odds = 1.5
        max_odds = 2.5
        max_bets = 12

        # 收集候选（只要低赔率）
        candidates = []
        for match in matches:
            for selection, odds in match.odds.items():
                if min_odds <= odds <= max_odds:
                    # 优先主场
                    is_home = selection == "home"
                    priority = odds + (0 if is_home else 0.2)

                    candidates.append({
                        "match": match,
                        "selection": selection,
                        "odds": odds,
                        "priority": priority,  # 越低越好
                    })

        if not candidates:
            return []

        # 按优先级排序（低赔率 + 主场优先）
        candidates.sort(key=lambda x: x["priority"])
        selected = candidates[:max_bets]

        # 平均分配预算
        if len(selected) == 0:
            return []

        stake_per_bet = budget / len(selected)
        stake_per_bet = round_stake(stake_per_bet)

        if stake_per_bet < MIN_STAKE:
            # 预算太小，减少注数
            affordable = int(budget // MIN_STAKE)
            selected = selected[:affordable]
            stake_per_bet = MIN_STAKE

        # 生成推荐
        result = []
        remaining = budget

        for candidate in selected:
            if remaining < MIN_STAKE:
                break

            stake = min(stake_per_bet, remaining)
            stake = round_stake(stake)

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
                ev_score=1.0 / candidate["odds"],  # 简单评分
                confidence=1.0 / candidate["odds"],
            ))

            remaining -= stake

        return result

    def explain_decision(self, recommendations: List[BetRecommendation]) -> str:
        """巴菲特的解释"""
        if not recommendations:
            return (
                "巴菲特说：我没有找到足够确定的投资机会。"
                "宁可错过，也不冒险。耐心等待好球再挥棒。"
            )

        total_stake = sum(r.stake for r in recommendations)
        max_return = sum(r.potential_return for r in recommendations)
        avg_odds = sum(r.odds for r in recommendations) / len(recommendations)
        home_count = sum(1 for r in recommendations if r.selection == "home")

        return (
            f"巴菲特的分析：\n\n"
            f"我只投资我看得懂、有把握的机会。这次选择了 {len(recommendations)} 个"
            f"低赔率高胜率的选项，全部超分散配置。\n\n"
            f"策略特点：\n"
            f"• 总投注：¥{total_stake:.0f}\n"
            f"• 平均赔率：{avg_odds:.2f}x（保守区间）\n"
            f"• 主场投注：{home_count} 个（主场优势）\n"
            f"• 全中回报：¥{max_return:.0f}（{(max_return/total_stake-1)*100:.0f}% ROI）\n\n"
            f"我的目标不是一夜暴富，而是稳定增长。"
            f"记住，复利的魔力需要时间和耐心。"
        )

    def get_risk_level(self) -> int:
        """巴菲特策略风险等级：2星（保守）"""
        return 2
