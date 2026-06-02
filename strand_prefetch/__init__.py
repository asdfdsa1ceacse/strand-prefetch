"""Strand Prefetch — 字符级 DNA 信号留存 + 磁吸共振 + 虫洞展开。

零外部依赖，纯 Python stdlib。

快速开始::

    from strand_prefetch import prefetch

    # 加载实体池
    from strand_prefetch.pool import MemoryPool
    pool = MemoryPool.load("data/seed_pool.json")

    # 运行管线
    result, matches, replicas = prefetch("帮我修一下wsl", pool.entities)
    print(result)
"""

from .dna import extract_dna_signal, extract_tokens
from .resonance import (
    coordinate_resonance,
    magnetic_resonance,
)
from .wormhole import wormhole_expand
from .render import _format_for_injection, set_budget


def prefetch(
    query: str,
    entities: list[dict],
    top_k: int = 5,
    max_hops: int = 1,
) -> tuple[str, list[dict], list[dict]]:
    """完整 prefetch 管线：信号留存 → 磁吸匹配 → 虫洞展开 → 上下文注入。

    参数:
        query: 用户查询字符串
        entities: 实体池列表（每个实体需含 text 字段）
        top_k: 初始匹配数量（默认 5）
        max_hops: 虫洞展开跳数（默认 1，推荐）

    返回:
        (injection_text, matches, replicas) 三元组。
        - injection_text: 可直接注入系统 prompt 的 ``<strand_context>`` 文本
        - matches: 初始匹配的实体列表
        - replicas: 虫洞展开的新实体列表

    如果无匹配，返回 ("", [], [])。
    """
    if not query or not query.strip() or not entities:
        return ("", [], [])

    query_signal = extract_dna_signal(query)
    matches = magnetic_resonance(query_signal, entities, top_k=top_k)
    if not matches:
        return ("", [], [])

    replicas = wormhole_expand(matches, entities, max_hops=max_hops)
    result = _format_for_injection(matches + replicas)
    return (result, matches, replicas)


__all__ = [
    "prefetch",
    "extract_dna_signal",
    "extract_tokens",
    "coordinate_resonance",
    "magnetic_resonance",
    "wormhole_expand",
    "set_budget",
]
