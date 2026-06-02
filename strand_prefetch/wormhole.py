"""Wormhole Expansion / 虫洞展开（可选联想层）

Associative expansion from seed entities. Each seed independently emits its DNA signal
to find neighbors via magnetic resonance. Replicas have fixed energy 0.7, never decay,
never modify original entities.

从种子实体出发的联想展开。每个种子独立用 DNA 信号寻找邻居。
复制体固定能量 0.7，永不衰减，不修改原始实体。

⚠️ Note / 注意:
    The default prefetch() uses PURE MATCHING only (no wormhole).
    Wormhole expansion is available as a lower-level function for specific use cases
    where broader recall is desired, accepting the precision tradeoff.

    默认 prefetch() 使用纯匹配模式（无虫洞展开）。
    本函数作为底层接口保留，适用于需要广度联想、接受精度折损的场景。
"""

from typing import Dict, List

from .dna import extract_dna_signal
from .resonance import magnetic_resonance


def wormhole_expand(
    seeds: list[dict],
    entities: list[dict],
    max_hops: int = 1,
) -> list[dict]:
    """Wormhole expansion / 虫洞展开

    Each hop: for each current seed, extract its DNA signal, run magnetic_resonance
    to find up to 5 neighbors not yet seen. New neighbors become the next hop's seeds.

    每跳：对每个当前种子提取 DNA 信号，磁吸匹配找最多 5 个未见邻居。
    新邻居成为下一跳的种子。

    Args:
        seeds: Initial matched entities / 初始匹配实体
        entities: Full entity pool / 完整实体池
        max_hops: Expansion depth (1 recommended) / 展开深度（推荐 1）

    Returns:
        New entities found through expansion (not including seeds) / 新发现的实体
    """
    seen_ids = {e.get("id") for e in seeds if e.get("id")}
    replicas: list[dict] = []
    current = seeds[:]

    for _ in range(max_hops):
        next_replicas: list[dict] = []
        for e in current:
            ent_dna = e.get("dna", {})
            if not ent_dna:
                text = e.get("text", "")
                if text:
                    ent_dna = extract_dna_signal(text)
                else:
                    continue

            neighbors = magnetic_resonance(ent_dna, entities, top_k=5)
            for nb in neighbors:
                nb_id = nb.get("id")
                if nb_id and nb_id not in seen_ids:
                    probe = dict(nb)
                    probe["energy"] = 0.7  # Fixed energy, no decay / 固定能量不衰减
                    seen_ids.add(nb_id)
                    next_replicas.append(probe)

        if not next_replicas:
            break
        replicas.extend(next_replicas)
        current = next_replicas

    return replicas
