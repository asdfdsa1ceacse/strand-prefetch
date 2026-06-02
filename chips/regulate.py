"""Strand Regulate / 安全护栏芯片

Intent collision engine. Before executing an action, check if the intent
conflicts with preset principles (iron laws). Each principle has a DNA
match pattern. Collision = block or warn.

意图碰撞引擎。在执行动作前，检查意图是否与预设原则（铁律）冲突。
每条原则包含 DNA 匹配模式，碰撞则阻止或警告。

Original: strand-regulate (pip package)
"""

from typing import Dict, List, Optional, Callable


class IronLaw:
    """An iron law — constitutional principle that cannot be violated / 不可违反的宪法原则"""

    def __init__(
        self,
        name: str,
        description: str,
        match_pattern: Dict[str, List[str]],
        action: str = "block",
    ):
        self.name = name
        self.description = description
        self.match_pattern = match_pattern  # DNA pattern that triggers this law
        self.action = action  # "block" | "warn" | "log"


class RegulateEngine:
    """Intent collision detection engine / 意图碰撞检测引擎"""

    def __init__(self):
        self.laws: List[IronLaw] = []

    def add_law(self, law: IronLaw):
        """Register an iron law / 注册一条铁律"""
        self.laws.append(law)

    def check(self, intent_dna: Dict[str, List[str]]) -> List[Dict]:
        """Check intent against all laws / 检查意图是否触碰铁律

        Returns list of collisions. Empty list = safe.
        返回碰撞列表。空列表 = 安全。
        """
        collisions = []
        for law in self.laws:
            if self._matches(intent_dna, law.match_pattern):
                collisions.append({
                    "law": law.name,
                    "description": law.description,
                    "action": law.action,
                })
        return collisions

    def _matches(self, intent: Dict, pattern: Dict) -> bool:
        """Check if intent DNA matches a law pattern / 检查意图 DNA 是否匹配铁律模式"""
        all_chains = set(intent.keys()) & set(pattern.keys())
        if not all_chains:
            return False
        for chain in all_chains:
            i_set = set(intent.get(chain, []))
            p_set = set(pattern.get(chain, []))
            if p_set and not (i_set & p_set):
                return False
        return True


# Example iron laws / 铁律示例:
#   "reseach_first" — check sources before asserting / 断言前检查来源
#   "zero_hallucination" — no absolute claims without evidence / 无证据不绝对断言
