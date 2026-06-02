"""Strand Router / 联想引擎芯片

Cross-domain graph routing. Given a matched entity, BFS-expand K hops
through the graph to discover "semantically different but structurally same"
cross-domain associations.

跨域图路由。给定一个匹配实体，从图谱中 BFS 展开 K 跳关联，
发现"语义不同但结构相同"的跨域关联。

Original: strand-router (pip package)
"""

from typing import Dict, List, Set, Tuple, Optional
from collections import deque


def route(
    seed_id: str,
    entities: List[Dict],
    max_hops: int = 2,
    max_results: int = 10,
) -> List[Dict]:
    """BFS graph routing from seed / 从种子 BFS 图路由

    Each hop follows entity connections. Discovers cross-domain associations
    that direct DNA matching would miss.

    每跳跟随实体连接。发现直接 DNA 匹配无法发现的跨域关联。
    """
    # Build ID lookup / 构建 ID 查找表
    entity_map = {e.get("id", ""): e for e in entities if e.get("id")}

    # Build adjacency via DNA similarity / 通过 DNA 相似度构建邻接关系
    adjacency: Dict[str, List[str]] = {}
    for e in entities:
        eid = e.get("id", "")
        if not eid:
            continue
        adjacency[eid] = []
        for other in entities:
            oid = other.get("id", "")
            if not oid or oid == eid:
                continue
            sim = _dna_similarity(e.get("dna", {}), other.get("dna", {}))
            if sim > 0.3:  # Adjacency threshold / 邻接阈值
                adjacency[eid].append(oid)

    # BFS / 广度优先搜索
    visited: Set[str] = {seed_id}
    queue = deque([(seed_id, 0)])
    results = []

    while queue:
        current_id, hop = queue.popleft()
        if hop >= max_hops:
            continue
        for neighbor_id in adjacency.get(current_id, []):
            if neighbor_id not in visited:
                visited.add(neighbor_id)
                neighbor = entity_map.get(neighbor_id)
                if neighbor:
                    results.append(neighbor)
                if hop + 1 < max_hops:
                    queue.append((neighbor_id, hop + 1))
                if len(results) >= max_results:
                    return results

    return results


def _dna_similarity(dna1: Dict, dna2: Dict) -> float:
    """Jaccard similarity between two DNA fingerprints / 两个 DNA 指纹的 Jaccard 相似度"""
    all_keys = set(dna1.keys()) | set(dna2.keys())
    if not all_keys:
        return 0.0
    sim = 0.0
    for k in all_keys:
        s1, s2 = set(dna1.get(k, [])), set(dna2.get(k, []))
        if s1 | s2:
            sim += len(s1 & s2) / len(s1 | s2)
    return sim / len(all_keys)


# Ecosystem role / 生态角色:
#   Discovers "semantic difference, structural similarity" / 发现"语义不同但结构相同"
#   BFS across entity graph / 跨实体图 BFS
#   Router + Wormhole = full associative recall / Router + Wormhole = 完整联想召回
