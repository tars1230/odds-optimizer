"""投资大师策略基类"""

from abc import ABC, abstractmethod
from typing import List
from app.models import Match, BetRecommendation


class MasterStrategy(ABC):
    """投资大师策略抽象基类"""

    # 大师基本信息
    name: str = ""           # 中文名
    name_en: str = ""        # 英文名
    emoji: str = ""          # 头像 emoji
    title: str = ""          # 头衔
    philosophy: str = ""     # 投资哲学
    personality: str = ""    # 性格描述
    quotes: List[str] = []   # 经典语录

    @abstractmethod
    def select_bets(
        self,
        matches: List[Match],
        budget: float,
    ) -> List[BetRecommendation]:
        """
        根据大师策略选择投注方案

        Args:
            matches: 可选赛事列表
            budget: 预算金额

        Returns:
            投注推荐列表
        """
        pass

    def explain_decision(self, recommendations: List[BetRecommendation]) -> str:
        """
        解释为什么这样选择

        Args:
            recommendations: 推荐方案

        Returns:
            解释文本
        """
        if not recommendations:
            return f"{self.name}认为当前没有符合策略的投注机会。"

        total_stake = sum(r.stake for r in recommendations)
        avg_odds = sum(r.odds for r in recommendations) / len(recommendations)

        return (
            f"{self.name}基于{self.philosophy}，"
            f"选择了{len(recommendations)}个投注机会，"
            f"总投注{total_stake:.0f}元，平均赔率{avg_odds:.1f}倍。"
        )

    def get_risk_level(self) -> int:
        """
        返回策略风险等级 (1-5星)

        Returns:
            风险星级
        """
        return 3  # 默认中等风险

    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "name": self.name,
            "name_en": self.name_en,
            "emoji": self.emoji,
            "title": self.title,
            "philosophy": self.philosophy,
            "personality": self.personality,
            "quotes": self.quotes,
            "risk_level": self.get_risk_level(),
        }
