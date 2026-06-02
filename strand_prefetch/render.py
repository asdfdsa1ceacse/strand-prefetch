"""上下文渲染——将实体列表格式化为注入文本。

受 token 预算约束，按分数降序注入。
"""

_CONTEXT_BUDGET = 8000


def _format_for_injection(entities: list[dict]) -> str:
    """将实体渲染为 ``<strand_context>`` 注入文本。

    格式::
        <strand_context>
          [source][E=energy] dna_preview text_preview
        </strand_context>

    按实体出现顺序排列（种子在前，虫洞在后）。
    每条截断 150 字符，超过 budget 即停止。
    """
    lines = ["<strand_context>"]
    remaining = _CONTEXT_BUDGET - len("\n".join(lines)) - 20  # 留关闭标签空间

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
    """设置注入文本的字符预算上限（默认 8000）。"""
    global _CONTEXT_BUDGET
    _CONTEXT_BUDGET = chars
