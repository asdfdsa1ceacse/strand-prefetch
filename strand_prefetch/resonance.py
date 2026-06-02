"""Magnetic Resonance / 磁吸共振

Three-layer coordinate resonance between query DNA and entity DNA.
查询 DNA 与实体 DNA 之间的三级坐标共振。

Core principle / 核心原则:
    Matching is resonance, not translation. Character-level coordinate overlap,
    not semantic similarity. No embeddings, no vectors, no models.

    匹配是共振不是翻译。字符级坐标重叠，不是语义相似度。
    无嵌入、无向量、无模型。

Three layers / 三级:
    1. Character  / 字符级 — single char overlap / 单字符重叠 (x0.3)
    2. Substring  / 子串级 — 2+ char consecutive fragment / 连续片段 (x0.3)
    3. Exact     / 精确级 — full token identity / 完整 token 相同 (x0.4)

All entities scored in ONE pass. Deterministic. Inspectable.
所有实体一次扫描完成打分。确定性。可追溯。
"""

from typing import Dict, List

from .dna import extract_dna_signal


# ── Helpers / 辅助函数 ──

def _flatten(dna: dict[str, list[str]]) -> list[str]:
    """Flatten 4-chain DNA into a single token list / 展平 4 链为单层 token 列表"""
    result: list[str] = []
    for vals in dna.values():
        if isinstance(vals, list):
            for v in vals:
                if isinstance(v, str) and v:
                    result.append(v)
    return result


# ── Core / 核心 ──


def coordinate_resonance(
    query: dict[str, list[str]],
    entity: dict[str, list[str]],
) -> float:
    """Three-layer coordinate resonance scoring / 三级坐标共振打分

    Each layer uses Jaccard-like overlap: common / union.
    Weighted sum: character(0.3) + substring(0.3) + exact(0.4).
    Returns 0.0 (no overlap) ~ 1.0 (identical).

    每层使用类似 Jaccard 的重叠率：共同集 / 并集。
    加权求和：字符(0.3) + 子串(0.3) + 精确(0.4)。
    返回 0.0（无重叠）~ 1.0（完全一致）。
    """
    score = 0.0
    q_all = _flatten(query)
    e_all = _flatten(entity)
    if not q_all or not e_all:
        return 0.0

    # Layer 1: Character-level / 字符级
    q_chars: set[str] = set("".join(q_all))
    e_chars: set[str] = set("".join(e_all))
    if q_chars and e_chars:
        common_chars = q_chars & e_chars
        score += len(common_chars) / max(len(q_chars | e_chars), 1) * 0.3

    # Layer 2: Substring-level (overlapping bigrams) / 子串级（重叠双字）
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

    # Layer 3: Exact token match / 精确 token 匹配
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
    """Magnetic matching / 磁吸匹配

    Scores ALL entities against the query DNA signal in one pass.
    Always extracts DNA from entity's live `text` field — never relies on stale cached DNA.
    Returns top_k entities sorted by score descending, each with an additional `_score` field.

    一次扫描评估所有实体。始终从实体的实时 text 字段提取 DNA。
    返回按分数降序排列的 top_k 实体，每个带 `_score` 字段。

    Args:
        query_signal: Query DNA from extract_dna_signal / 查询的 DNA 信号
        entities: Pool of entity dicts (each must have "text" key) / 实体字典列表
        top_k: Max results to return / 最大返回数

    Returns:
        Entities with _score added, sorted by relevance / 带 _score 的实体列表
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
