"""Strand DNA Signal Extraction / DNA 信号留存

Character-level signal extraction from raw text. No vocabulary, no classification, no discarding.
字符级信号提取。无词表，不分类，不丢弃。

Core principle / 核心原则:
    DNA is a fingerprint, not a label. Extracted from the text's inherent structure,
    not assigned by a model. The same text always produces the same DNA. Deterministic.

    DNA 是指纹不是标签。从文本的固有结构中提取，不是模型赋予的。
    同一段文本总是产生相同的 DNA。确定性。

4 chains / 4 条链:
    domain  — English lowercase words (>2 chars)        / 英文小写词（领域信号）
    entity  — Chinese blocks + English proper nouns     / 中文块 + 英文专有名词（实体指纹）
    pattern — Digits, punctuation, line counts         / 数字、标点、行数（模式信号）
    context — Reserved chain                            / 预留链
"""

import re
from typing import List


def extract_tokens(text: str) -> List[str]:
    """Extract raw structural tokens from text / 从文本中提取原始结构信号

    Uses script-isolation scanning: / 使用脚本隔离法逐字符扫描:
      - consecutive CJK chars → Chinese block / 连续中文字符 → 中文块
      - consecutive ASCII alpha → English word (lowercased) / 连续英文字母 → 英文词（小写）
      - consecutive ASCII digit → number string / 连续数字 → 数字串
      - other → single char preserved / 其他 → 单字符保留
    Whitespace is skipped. / 空白被跳过。

    Args:
        text: Input text in any language / 任意语言的输入文本

    Returns:
        List of token strings / Token 字符串列表
    """
    tokens: List[str] = []
    i = 0
    while i < len(text):
        ch = text[i]
        # Skip whitespace / 跳过空白
        if ch.isspace():
            i += 1
            continue
        # Chinese block / 中文块
        if "\u4e00" <= ch <= "\u9fff":
            j = i
            while j < len(text) and "\u4e00" <= text[j] <= "\u9fff":
                j += 1
            tokens.append(text[i:j])
            i = j
            continue
        # English word / 英文词
        if ch.isascii() and ch.isalpha():
            j = i
            while j < len(text) and text[j].isascii() and text[j].isalpha():
                j += 1
            tokens.append(text[i:j].lower())
            i = j
            continue
        # Number string / 数字串
        if ch.isascii() and ch.isdigit():
            j = i
            while j < len(text) and text[j].isascii() and text[j].isdigit():
                j += 1
            tokens.append(text[i:j])
            i = j
            continue
        # Other character / 其他字符
        tokens.append(ch)
        i += 1
    return tokens


def extract_dna_signal(text: str) -> dict[str, list[str]]:
    """Extract 4-chain DNA signal from text / 从文本提取 4 链 DNA 信号

    Token placement rules / Token 放置规则:
      - Chinese blocks → entity chain (≤4 chars full, >4 chars overlapping bigrams)
      - English 3+ lowercase → domain chain / 英文 3+ 小写词 → domain 链
      - English 3+ capitalized → entity chain / 英文 3+ 大写词 → entity 链
      - Digits → pattern chain (prefixed with "num:") / 数字 → pattern 链
      - Punctuation → pattern chain (prefixed with "punct:") / 标点 → pattern 链
      - Multi-line → pattern chain (prefixed with "lines:") / 多行 → pattern 链

    Args:
        text: Input text / 输入文本

    Returns:
        4-chain DNA dict: {"domain": [...], "entity": [...], "pattern": [...], "context": [...]}
    """
    tokens = extract_tokens(text)
    dna: dict[str, list[str]] = {
        "domain": [],
        "entity": [],
        "pattern": [],
        "context": [],
    }
    for t in tokens:
        # Chinese block → entity chain / 中文块 → entity 链
        if all("\u4e00" <= c <= "\u9fff" for c in t):
            if len(t) <= 4:
                dna["entity"].append(t)
            else:
                for k in range(len(t) - 1):
                    dna["entity"].append(t[k : k + 2])
        # English word ≥ 3 chars / 英文词 ≥ 3 字符
        elif t.isalpha() and len(t) > 2:
            if t[0].islower():
                dna["domain"].append(t)  # lowercase → domain
            else:
                dna["entity"].append(t)  # capitalized → entity
        # Digits → pattern / 数字 → pattern
        elif t.isdigit():
            dna["pattern"].append(f"num:{t[:4]}")
        # Single-char punctuation → pattern / 单字符标点 → pattern
        elif len(t) == 1 and t in "!?？。，；：":
            dna["pattern"].append(f"punct:{t}")

    # Multi-line indicator / 多行标记
    lines = text.count("\n")
    if lines > 1:
        dna["pattern"].append(f"lines:{lines}")

    return dna
