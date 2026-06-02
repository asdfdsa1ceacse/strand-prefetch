"""Strand Prefetch — 字符级 DNA 信号留存 + 磁吸共振。

零外部依赖，纯 Python stdlib。
纯匹配模式，无虫洞展开。所有注入实体经同一套查询 DNA 信号筛选。

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
    top_k: int = 15,
) -> tuple[str, list[dict], list[dict]]:
    """完整 prefetch 管线：信号留存 → 磁吸匹配 → 上下文注入。

    纯匹配模式，无虫洞展开。
    top_k=15 保证足够的上下文注入量，同时不引入二跳噪音。
    所有注入实体都经过同一套查询 DNA 信号筛选。

    参数:
        query: 用户查询字符串
        entities: 实体池列表（每个实体需含 text 字段）
        top_k: 匹配数量（默认 15）

    返回:
        (injection_text, matches, []) 三元组。
        - injection_text: 可直接注入的 ``<strand_context>`` 文本
        - matches: 匹配的实体列表
        - replicas: 空列表（保留参数以兼容旧代码）

    如果无匹配，返回 ("", [], [])。
    """
    if not query or not query.strip() or not entities:
        return ("", [], [])

    query_signal = extract_dna_signal(query)
    matches = magnetic_resonance(query_signal, entities, top_k=top_k)
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
