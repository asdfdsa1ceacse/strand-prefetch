"""Strand Immune / 免疫系统芯片

Disagreement-driven learning. When the matcher makes a wrong match,
user feedback triggers a disagreement record. The immune system computes
the diff, writes to staging, and auto-promotes to antibody on threshold.

分歧驱动学习：当匹配引擎做出错误匹配时，用户反馈触发分歧记录。
免疫系统自动计算差集、写入暂存区、按阈值提升为抗体。

Original: strand-immune (pip package)
"""

from typing import Dict, List, Optional, Tuple


class Antibody:
    """A learned anti-pattern / 一条学习到的反模式"""

    def __init__(self, pattern: Dict[str, List[str]], weight: float = 1.0):
        self.pattern = pattern  # DNA pattern to recognize / 要识别的 DNA 模式
        self.weight = weight    # Suppression strength / 抑制强度
        self.hits = 0           # Times successfully applied / 成功应用次数


class ImmuneSystem:
    """Disagreement-driven immune system / 分歧驱动免疫系统"""

    def __init__(self):
        self.antibodies: List[Antibody] = []
        self.staging: List[Dict] = []       # Pending promotions / 待提升候选
        self.threshold: int = 3             # Promotions needed / 需要的提升次数

    def record_disagreement(
        self, query_dna: Dict, wrong_match: Dict, correct_match: Dict
    ):
        """Record a user disagreement / 记录用户分歧

        Computes the diff between wrong and correct DNA to derive an anti-pattern.
        计算错误与正确 DNA 之间的差集，推导反模式。
        """
        diff = self._compute_diff(wrong_match.get("dna", {}), correct_match.get("dna", {}))
        if diff:
            self.staging.append({
                "pattern": diff,
                "query": query_dna,
                "count": 1,
            })

    def _compute_diff(self, wrong: Dict, correct: Dict) -> Dict[str, List[str]]:
        """Compute DNA diff: what's in wrong but not in correct / 计算 DNA 差集"""
        diff: Dict[str, List[str]] = {}
        all_chains = set(wrong.keys()) | set(correct.keys())
        for chain in all_chains:
            w_set = set(wrong.get(chain, []))
            c_set = set(correct.get(chain, []))
            extra = w_set - c_set
            if extra:
                diff[chain] = list(extra)
        return diff

    def promote(self) -> List[Antibody]:
        """Promote staging patterns to full antibodies / 提升暂存模式为抗体"""
        from collections import Counter
        for staged in self.staging:
            staged["count"] += 1
            if staged["count"] >= self.threshold:
                ab = Antibody(staged["pattern"])
                self.antibodies.append(ab)
        self.staging = [s for s in self.staging if s["count"] < self.threshold]
        return self.antibodies


# Ecosystem role / 生态角色:
#   Learns from mistakes / 从错误中学习
#   Auto-generates suppression patterns / 自动生成抑制模式
#   Reduces repeat errors over time / 随时间减少重复错误
