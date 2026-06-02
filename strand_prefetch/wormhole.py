"""虫洞展开——联想激发。

从种子实体出发，用每个实体的 DNA 信号独立激发新磁吸。
复制体固定能量 0.7，不衰减，不修改原始实体。
"""

from typing import Dict, List

from .dna import extract_dna_signal
from .resonance import magnetic_resonance


def wormhole_expand(
    seeds: list[dict],
    entities: list[dict],
    max_hops: int = 1,
) -> list[dict]:
    """虫洞展开：种子实体的 DNA 信号独立激发磁吸。

    每跳计算种子实体的 DNA 信号，用该信号对完整实体池做磁吸匹配，
    找到新邻居（未出现在 seeds 或之前跳中的实体）。
    复制体固定能量 0.7，不衰减。

    参数:
        seeds: 初始种子实体列表
        entities: 完整实体池
        max_hops: 展开跳数。1 跳只展开一层邻居（推荐），
                  >1 跳会进一步扩散但精度下降。

    返回:
        按展开顺序排列的新实体列表（不含 seeds）。
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
                    probe["energy"] = 0.7  # 固定能量，不衰减
                    seen_ids.add(nb_id)
                    next_replicas.append(probe)

        if not next_replicas:
            break
        replicas.extend(next_replicas)
        current = next_replicas

    return replicas
