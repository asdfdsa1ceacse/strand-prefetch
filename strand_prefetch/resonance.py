"""磁吸共振——字符/子串/精确三级坐标共振。

查询的 DNA 信号 vs 实体 DNA 坐标，
通过三层结构重叠打分，不依赖语义对齐。
"""

from typing import Dict, List

from .dna import extract_dna_signal


def _flatten(dna: dict[str, list[str]]) -> list[str]:
    """展平 DNA 4 链为 token 列表。"""
    result: list[str] = []
    for vals in dna.values():
        if isinstance(vals, list):
            for v in vals:
                if isinstance(v, str) and v:
                    result.append(v)
    return result


def coordinate_resonance(
    query: dict[str, list[str]],
    entity: dict[str, list[str]],
) -> float:
    """三级共振打分。

    三层结构重叠，逐层加权求和：
      1. 字符级（单字符重叠 × 0.3）
      2. 子串级（2+字符连续片段重叠 × 0.3）
      3. 精确级（完整 token 匹配 × 0.4）

    返回 0.0~1.0 的浮点分数。
    0 = 无重叠，1 = 完全一致。
    """
    score = 0.0
    q_all = _flatten(query)
    e_all = _flatten(entity)
    if not q_all or not e_all:
        return 0.0

    # 1. 字符级
    q_chars: set[str] = set("".join(q_all))
    e_chars: set[str] = set("".join(e_all))
    if q_chars and e_chars:
        common_chars = q_chars & e_chars
        score += len(common_chars) / max(len(q_chars | e_chars), 1) * 0.3

    # 2. 子串级（重叠双字）
    q_bigrams: set[str] = set()
    for token in q_all:
        for i in range(len(token) - 1):
            q_bigrams.add(token[i : i + 2])
    e_bigrams: set[str] = set()
    for token in e_all:
        for i in range(len(token) - 1):
            e_bigrams.add(token[i : i + 2])
    if q_bigrams and e_bigrams:
        common_bigrams = q_bigrams & e_bigrams
        score += len(common_bigrams) / max(len(q_bigrams | e_bigrams), 1) * 0.3

    # 3. 精确级
    q_set: set[str] = set(q_all)
    e_set: set[str] = set(e_all)
    if q_set and e_set:
        common_tokens = q_set & e_set
        score += len(common_tokens) / max(len(q_set | e_set), 1) * 0.4

    return round(score, 4)


def magnetic_resonance(
    query_signal: dict[str, list[str]],
    entities: list[dict],
    top_k: int = 5,
) -> list[dict]:
    """磁吸匹配：查询 DNA 信号 vs 所有实体的实时 DNA 坐标。

    始终从实体 text 字段实时提取 DNA 信号，
    不依赖实体存储的旧格式 DNA。

    返回按分数降序排列的 top_k 实体列表，
    每个实体附加 ``_score`` 字段。
    """
    if not query_signal or not entities:
        return []

    scored: list[tuple[float, dict]] = []
    for ent in entities:
        text = ent.get("text", "")
        if not text:
            continue
        ent_signal = extract_dna_signal(text)
        score = coordinate_resonance(query_signal, ent_signal)
        if score > 0.01:
            scored.append((score, ent))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [dict(e, _score=s) for s, e in scored[:top_k]]
