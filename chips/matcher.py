"""Strand Matcher / 匹配引擎芯片

Weighted multi-chain voting + optional anti-chain negative feedback.
独立决策引擎：加权多链投票 + 可选反链负反馈抑制。

Original: strand-matcher (pip package)
"""

from typing import Dict, List, Tuple, Optional


def match(
    query_dna: Dict[str, List[str]],
    candidates: List[Dict],
    top_k: int = 5,
    anti_chains: Optional[List[str]] = None,
) -> List[Tuple[float, Dict]]:
    """Weighted multi-chain voting match / 加权多链投票匹配

    Each chain votes independently. Anti-chains suppress scores on specific dimensions.
    每条链独立投票。反链在特定维度抑制分数。

    The strand_prefetch version (magnetic_resonance) uses coordinate_resonance
    for 3-layer character-level scoring instead of chain-weighted voting.
    Both approaches are valid — the prefetch pipeline optimizes for speed (<1ms).

    strand_prefetch 版本 (magnetic_resonance) 使用 3 级字符级坐标共振
    替代链加权投票。两种方案都有效——预取管线优化了速度。
    """
    scored = []
    for cand in candidates:
        score = 0.0
        for chain, keywords in query_dna.items():
            cand_keywords = cand.get("dna", {}).get(chain, [])
            overlap = len(set(keywords) & set(cand_keywords))
            score += overlap / max(len(set(keywords) | set(cand_keywords)), 1)

        # Anti-chain suppression / 反链抑制
        if anti_chains:
            for ac in anti_chains:
                if ac in cand.get("dna", {}):
                    score *= 0.5

        if score > 0:
            scored.append((score, cand))

    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[:top_k]


# Key differences from strand_prefetch / 与 strand_prefetch 的主要区别:
# - Chain-weighted: each chain votes independently / 链加权：每链独立投票
# - Anti-chain: negative feedback on specific dimensions / 反链：特定维度负反馈
# - Slower: ~10ms vs ~1ms for coordinate_resonance / 较慢
