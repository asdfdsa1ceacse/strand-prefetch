"""DNA 信号留存——字符级，无词表，零依赖。

从文本中提取原始结构信号，保留所有可用坐标。
不分类、不查表、不丢弃。
"""

import re
from typing import List


def extract_tokens(text: str) -> List[str]:
    """从文本中提取原始结构信号：英文词 + 中文块 + 数字 + 标点。

    使用脚本隔离法逐字符扫描：
      - 连续中文字符 → 中文块
      - 连续英文字母 → 英文词（自动小写）
      - 连续数字 → 数字串
      - 其他 → 单字符保留
    空白被跳过。
    """
    tokens: List[str] = []
    i = 0
    while i < len(text):
        ch = text[i]
        # 跳过空白
        if ch.isspace():
            i += 1
            continue
        # 中文块（连续中文字符）
        if "\u4e00" <= ch <= "\u9fff":
            j = i
            while j < len(text) and "\u4e00" <= text[j] <= "\u9fff":
                j += 1
            tokens.append(text[i:j])
            i = j
            continue
        # 英文词（连续字母）
        if ch.isascii() and ch.isalpha():
            j = i
            while j < len(text) and text[j].isascii() and text[j].isalpha():
                j += 1
            tokens.append(text[i:j].lower())
            i = j
            continue
        # 数字（连续数字）
        if ch.isascii() and ch.isdigit():
            j = i
            while j < len(text) and text[j].isascii() and text[j].isdigit():
                j += 1
            tokens.append(text[i:j])
            i = j
            continue
        # 其他字符
        tokens.append(ch)
        i += 1
    return tokens


def extract_dna_signal(text: str) -> dict[str, list[str]]:
    """字符级信号留存。

    将 Token 按 4 条链放置：
      domain  — 英文词（全小写/数字开头），领域信号
      entity  — 中文块（≤4保留完整，>4拆重叠双字），实体指纹
      pattern — 数字、标点、换行数，模式信号
      context —（预留链，当前未使用但保留）

    这是指纹坐标的提取层，不是分类层。
    不依赖任何词表、关键词库、语义模型。
    """
    tokens = extract_tokens(text)
    dna: dict[str, list[str]] = {
        "domain": [],
        "entity": [],
        "pattern": [],
        "context": [],
    }
    for t in tokens:
        # 中文块 → entity 链
        if all("\u4e00" <= c <= "\u9fff" for c in t):
            if len(t) <= 4:
                dna["entity"].append(t)
            else:
                for k in range(len(t) - 1):
                    dna["entity"].append(t[k : k + 2])
        # 英文词 ≥ 3 字符 → domain/entity
        elif t.isalpha() and len(t) > 2:
            if t[0].islower() or t[:1].isnumeric():
                dna["domain"].append(t)
            else:
                dna["entity"].append(t)
        # 数字 → pattern
        elif t.isdigit():
            dna["pattern"].append(f"num:{t[:4]}")
        # 单字符标点 → pattern
        elif len(t) == 1 and t in "!?？。，；：":
            dna["pattern"].append(f"punct:{t}")

    lines = text.count("\n")
    if lines > 1:
        dna["pattern"].append(f"lines:{lines}")

    return dna
