"""Strand Predator / 养蛊演化芯片

Three operators: cannibalize (merge similar), hybridize (crossover), rank (survival).
三个算子：同类吞噬（相似实体合并去重）、杂交（交叉繁殖）、排名（生存竞争）。

Original: strand-predator (pip package)
"""

from typing import List, Dict, Tuple


def cannibalize(entities: List[Dict], threshold: float = 0.85) -> List[Dict]:
    """Cannibalize similar entities / 同类吞噬：合并相似实体

    When two entities have DNA similarity above threshold, the lower-energy
    entity is absorbed by the higher-energy one. Text is merged.
    当两个实体 DNA 相似度超过阈值时，低能量被高能量吞噬吸收，文本合并。
    """
    survivors = list(entities)
    changed = True
    while changed:
        changed = False
        i = 0
        while i < len(survivors):
            j = i + 1
            while j < len(survivors):
                # Check DNA similarity / 检查 DNA 相似度
                sim = _dna_similarity(
                    survivors[i].get("dna", {}),
                    survivors[j].get("dna", {}),
                )
                if sim > threshold:
                    low, high = (j, i) if survivors[i]["energy"] > survivors[j]["energy"] else (i, j)
                    survivors[high]["text"] = _merge_text(
                        survivors[low].get("text", ""),
                        survivors[high].get("text", ""),
                    )
                    survivors[high]["energy"] = min(
                        1.0, survivors[high]["energy"] + survivors[low]["energy"] * 0.3
                    )
                    survivors.pop(low)
                    changed = True
                j += 1
            i += 1
    return survivors


def _dna_similarity(dna1: Dict, dna2: Dict) -> float:
    """Simple DNA Jaccard similarity / 简单 DNA Jaccard 相似度"""
    all_keys = set(dna1.keys()) | set(dna2.keys())
    if not all_keys:
        return 0.0
    sim = 0.0
    for k in all_keys:
        s1, s2 = set(dna1.get(k, [])), set(dna2.get(k, []))
        if s1 | s2:
            sim += len(s1 & s2) / len(s1 | s2)
    return sim / len(all_keys)


def _merge_text(t1: str, t2: str) -> str:
    """Merge two text fragments / 合并两段文本"""
    # Simple merge: keep longer text, append shorter if it adds new info
    if t1 in t2:
        return t2
    if t2 in t1:
        return t1
    return f"{t1}; {t2}" if len(t1) > len(t2) else f"{t2}; {t1}"


# Ecosystem role / 生态角色:
#   Maintains pool diversity by culling redundancy / 通过去重维持池多样性
#   Energy flows from weak to strong / 能量从弱流向强
#   Prevents entity count explosion / 防止实体数爆炸
