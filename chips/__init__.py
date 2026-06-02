"""Strand 8-Chip Architecture / Strand 8 芯片架构

Reference copies of the full Strand ecosystem.
The 8 chips are independent pip packages that together form the complete cognitive ecosystem.

完整 Strand 生态的 8 个独立芯片参考。每个芯片是独立的 pip 包，
共同构成完整的认知生态。

Architecture / 架构::

    Encoder → Matcher → Regulate → Immune
        ↓         ↓          ↓
    ┌──────────────────────────────────┐
    │          Memory Pool             │
    │     (strand_pool — DNA 存储)      │
    └──────────────────────────────────┘
        ↓         ↓          ↓
    Predator   Lifecycle    Router

See ARCHITECTURE.md for full explanation.
详见 ARCHITECTURE.md 完整架构说明。
"""
