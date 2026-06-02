"""Strand Prefetch / Strand 预取管线

Cognitive prefetch pipeline for AI agents.
Character-level DNA signal extraction → magnetic resonance matching → context injection.

AI 智能体认知预取管线。
字符级 DNA 信号留存 → 磁吸共振匹配 → 上下文注入。

Pipeline / 管线::

    query → extract_dna_signal → magnetic_resonance(top_k=15) → <strand_context>

Zero external dependencies. Pure Python stdlib. Deterministic. Inspectable.
零外部依赖。纯 Python stdlib。确定性。可追溯。

Core philosophy / 核心哲学:
    - DNA is a fingerprint, not a label / DNA 是指纹不是标签
    - Matching is resonance, not translation / 匹配是共振不是翻译
    - Pure matching beats associative expansion / 纯匹配优于联想展开

Quick start / 快速开始::

    from strand_prefetch import prefetch
    from strand_prefetch.pool import MemoryPool

    pool = MemoryPool.load("data/seed_pool.json")
    result, matches, _ = prefetch("帮我修一下wsl", pool.entities)
    print(result)
"""

from typing import Optional
from .dna import extract_dna_signal, extract_tokens
from .resonance import coordinate_resonance, magnetic_resonance, compute_idf
from .wormhole import wormhole_expand
from .render import _format_for_injection, set_budget


def prefetch(
    query: str,
    entities: list[dict],
    top_k: int = 15,
    idf_weights: Optional[dict[str, float]] = None,
) -> tuple[str, list[dict], list[dict]]:
    """Run the full prefetch pipeline / 运行完整预取管线

    Pure matching mode — no wormhole expansion. All injected entities are filtered
    through the same query DNA signal, guaranteeing precision without noise.

    纯匹配模式——无虫洞展开。所有注入实体都经过同一套查询 DNA 信号筛选，
    保证精度不引入噪音。

    Args:
        query: User query string / 用户查询字符串
        entities: List of entity dicts (each must have "text") / 实体字典列表
        top_k: Number of matches to return (default 15) / 返回匹配数
        idf_weights: Optional IDF weights from compute_idf(). When provided,
                     distinctive tokens get higher weight in exact-match layer.
                     可选 IDF 权重。提供时特异性词在精确匹配层获得更高权重。

    Returns:
        (injection_text, matches, [])  # replicas is empty in pure mode
        If no matches, returns ("", [], [])
    """
    if not query or not query.strip() or not entities:
        return ("", [], [])

    query_signal = extract_dna_signal(query)
    matches = magnetic_resonance(query_signal, entities, top_k=top_k, idf_weights=idf_weights)
    if not matches:
        return ("", [], [])

    result = _format_for_injection(matches)
    return (result, matches, [])


__all__ = [
    "prefetch",
    "extract_dna_signal",
    "extract_tokens",
    "coordinate_resonance",
    "magnetic_resonance",
    "wormhole_expand",
    "set_budget",
]
