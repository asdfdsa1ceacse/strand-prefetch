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

TF-IDF boost / TF-IDF 增强:
    When entity pool is provided, IDF weights suppress high-frequency tokens
    (like "I", "you", "the") and boost distinctive ones (like "degree", "graduate").
    Implemented as a simple multiplicative boost on the exact-match layer.
    
    当提供实体池时，IDF 权重压制高频通用词，增强特异性词。
    在精确匹配层做乘法增强。
"""

import math
from typing import Dict, List, Optional

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


# ── TF-IDF / 词频-逆文档频率 ──


def compute_idf(entities: list[dict]) -> dict[str, float]:
    """Compute IDF weights for all tokens in the entity pool / 计算实体池中所有 token 的 IDF 权重

    IDF(t) = log(N / df(t)) + 1
    where N = total entities, df(t) = entities containing token t.
    Tokens appearing in every entity get weight=1.0 (no boost).
    Tokens appearing in few entities get weight >> 1.0 (strong boost).

    N = 总实体数, df(t) = 包含 token t 的实体数。
    出现在所有实体中的 token 权重=1.0（无增强）。
    出现在少数实体中的 token 权重>>1.0（强增强）。
    """
    N = len(entities)
    if N == 0:
        return {}

    # Document frequency / 文档频率
    df: dict[str, int] = {}
    for ent in entities:
        text = ent.get("text", "")
        if not text:
            continue
        signal = extract_dna_signal(text)
        tokens = set(_flatten(signal))
        for t in tokens:
            df[t] = df.get(t, 0) + 1

    # Compute IDF / 计算 IDF
    idf: dict[str, float] = {}
    for token, doc_count in df.items():
        idf[token] = math.log(N / max(doc_count, 1)) + 1.0

    return idf


# ── Sliding Window Chunking / 滑动窗口分片 ──

_CHUNK_SIZE = 200   # Max chars per chunk / 每片最大字符数
_CHUNK_OVERLAP = 50  # Overlap between chunks / 片间重叠字符数


def _chunk_text(text: str) -> list[str]:
    """Split long text into overlapping short chunks / 长文本切分为重叠短片段

    Chunks at word/sentence boundaries, preferring to split on ``|`` (session turn
    separator), newlines, or spaces. Falls back to character-level slicing.

    优先在 | 、换行、空格处分片，保持语义完整性。
    解决长文本中关键信息被无关内容稀释的问题。
    """
    if len(text) <= _CHUNK_SIZE:
        return [text]

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + _CHUNK_SIZE, len(text))

        # Try to break at a good boundary / 尽量在边界切
        if end < len(text):
            # Prefer '|' separator / 优先在 | 处切断
            sep_pos = text.rfind(" | ", start + _CHUNK_SIZE // 2, end)
            if sep_pos >= start + _CHUNK_SIZE // 2:
                end = sep_pos
            else:
                # Fallback: newline / 其次换行
                nl_pos = text.rfind("\n", start + _CHUNK_SIZE // 2, end)
                if nl_pos >= start + _CHUNK_SIZE // 2:
                    end = nl_pos

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        # Advance — ensure we always move forward / 确保总在前进
        next_start = end - _CHUNK_OVERLAP
        if next_start <= start:
            next_start = end
        start = next_start

        # Safety — last 100 chars, take it all / 最后一段全部纳入
        if len(text) - start <= _CHUNK_SIZE and start < len(text):
            chunks.append(text[start:].strip())
            break

    return chunks


# ── Core / 核心 ──


def coordinate_resonance(
    query: dict[str, list[str]],
    entity: dict[str, list[str]],
    idf_weights: Optional[dict[str, float]] = None,
) -> float:
    """Three-layer coordinate resonance scoring / 三级坐标共振打分

    Each layer uses Jaccard-like overlap: common / union.
    Weighted sum: character(0.3) + substring(0.3) + exact(0.4).

    When idf_weights is provided, the exact-match layer is boosted by IDF:
    each common token contributes weight * idf[token] instead of just weight.
    This suppresses high-frequency tokens and boosts distinctive ones.
    
    当提供 idf_weights 时，精确匹配层受 IDF 增强：
    每个共同 token 贡献 weight × idf[token] 而非单纯的 weight。
    以此压制高频词，增强特异性词。

    Args:
        query: Query DNA signal / 查询 DNA 信号
        entity: Entity DNA signal / 实体 DNA 信号
        idf_weights: Optional IDF weights from compute_idf() / 可选的 IDF 权重

    Returns:
        Score 0.0~1.0 / 分数 0.0~1.0
    """
    score = 0.0
    q_all = _flatten(query)
    e_all = _flatten(entity)
    if not q_all or not e_all:
        return 0.0

    # Layer 1: Character-level / 字符级 (x0.3)
    q_chars: set[str] = set("".join(q_all))
    e_chars: set[str] = set("".join(e_all))
    if q_chars and e_chars:
        common_chars = q_chars & e_chars
        score += len(common_chars) / max(len(q_chars | e_chars), 1) * 0.3

    # Layer 2: Substring-level / 子串级 (x0.3)
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

    # Layer 3: Exact token match / 精确 token 匹配 (x0.4)
    q_set: set[str] = set(q_all)
    e_set: set[str] = set(e_all)
    if q_set and e_set:
        common_tokens = q_set & e_set
        if idf_weights:
            # IDF-weighted: distinctive tokens count more / IDG加权：特异性词权重更高
            weighted_common = sum(idf_weights.get(t, 1.0) for t in common_tokens)
            weighted_union = sum(
                idf_weights.get(t, 1.0)
                for t in (q_set | e_set)
            )
            score += (weighted_common / max(weighted_union, 1)) * 0.4
        else:
            # Plain Jaccard / 普通 Jaccard
            score += len(common_tokens) / max(len(q_set | e_set), 1) * 0.4

    return round(score, 4)


def magnetic_resonance(
    query_signal: dict[str, list[str]],
    entities: list[dict],
    top_k: int = 5,
    idf_weights: Optional[dict[str, float]] = None,
    enable_chunking: bool = True,
) -> list[dict]:
    """Magnetic matching / 磁吸匹配

    Scores ALL entities against the query DNA signal in one pass.
    Always extracts DNA from entity's live ``text`` field.

    When ``enable_chunking`` is True (default), entities with text longer than
    _CHUNK_SIZE are split into overlapping chunks and scored chunk-by-chunk.
    The entity gets the maximum chunk score. This solves the "long text dilution"
    problem where key information is buried in a sea of irrelevant text.

    当 enable_chunking=True（默认）时，长文本实体被切分为重叠片段，
    逐片打分，取最高分。解决长文本中关键信息被稀释的问题。

    Args:
        query_signal: Query DNA / 查询 DNA 信号
        entities: Entity pool / 实体池
        top_k: Max results / 最大返回数
        idf_weights: Optional IDF weights / 可选 IDF 权重
        enable_chunking: Enable sliding window for long text / 启用长文本滑动窗口分片

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

        if enable_chunking and len(text) > _CHUNK_SIZE * 1.2:
            # Long text: score each chunk, take max / 长文本：逐片打分取最高
            chunks = _chunk_text(text)
            best_score = 0.0
            for chunk in chunks:
                ent_signal = extract_dna_signal(chunk)
                score = coordinate_resonance(query_signal, ent_signal, idf_weights)
                if score > best_score:
                    best_score = score
            if best_score > 0.01:
                scored.append((best_score, ent))
        else:
            # Short text: score directly / 短文本：直接打分
            ent_signal = extract_dna_signal(text)
            score = coordinate_resonance(query_signal, ent_signal, idf_weights)
            if score > 0.01:
                scored.append((score, ent))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [dict(e, _score=s) for s, e in scored[:top_k]]
