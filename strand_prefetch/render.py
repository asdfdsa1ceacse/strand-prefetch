"""Context Injection Formatter / 上下文注入格式化

Renders matched entities into ``<strand_context>`` tags for LLM system prompt injection.
Token-budget constrained, score-ordered.

将匹配的实体渲染为 ``<strand_context>`` 标签，用于 LLM 系统 prompt 注入。
受 Token 预算约束，按分数顺序输出。
"""

_CONTEXT_BUDGET = 8000  # Max chars before closing tag / 关闭标签前最大字符数


def _format_for_injection(entities: list[dict]) -> str:
    """Render entities as ``<strand_context>`` / 将实体渲染为注入文本

    Format / 格式::

        <strand_context>
          [source][E=energy] dna_preview text_preview
        </strand_context>

    Each entity is truncated to 150 chars. Stops when budget is exhausted.
    Matches (seeds) are listed first, followed by wormhole replicas (if any).

    每个实体截断至 150 字符。预算耗尽时停止。
    种子实体在前，虫洞复制体在后。

    Args:
        entities: List of entity dicts / 实体字典列表

    Returns:
        Formatted string, or empty on no entities / 格式化字符串
    """
    if not entities:
        return ""

    lines = ["<strand_context>"]
    remaining = _CONTEXT_BUDGET - len("\n".join(lines)) - 20

    for e in entities:
        text = (e.get("text") or "")[:150].replace("\n", " ")
        dna_preview: list[str] = []
        edna = e.get("dna", {})
        for chain in ("domain", "entity", "pattern", "context"):
            vals = edna.get(chain, [])
            if vals:
                dna_preview.append(
                    f"{chain}:{','.join(str(v)[:12] for v in vals[:2])}"
                )
        dna_str = "|".join(dna_preview[:3])
        line = (
            f"  [{e.get('source', '?')}]"
            f"[E={e.get('energy', 0):.2f}]"
            f" {dna_str} {text}"
        )
        remaining -= len(line)
        if remaining < 0:
            break
        lines.append(line)

    lines.append("</strand_context>")
    return "\n".join(lines)


def set_budget(chars: int) -> None:
    """Set max context budget in chars (default: 8000) / 设置最大上下文预算（字符数）"""
    global _CONTEXT_BUDGET
    _CONTEXT_BUDGET = chars
