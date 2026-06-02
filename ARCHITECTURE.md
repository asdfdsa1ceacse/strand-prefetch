# Strand Architecture / Strand 架构

> **DNA 是指纹，不是标签。匹配是坐标共振，不是语义翻译。**
> **DNA is a fingerprint, not a label. Matching is coordinate resonance, not semantic translation.**

## Overview / 概述

Strand is a cognitive prefetch pipeline for AI agents. Instead of relying on vector embeddings, keyword dictionaries, or semantic models, it extracts **structural DNA signals** from text at the character level and matches them against entity pools through **coordinate resonance** — a three-layer character/substring/exact overlap scoring system.

Strand 是 AI 智能体的认知预取管线。不依赖向量嵌入、关键词词表或语义模型，而是从文本中提取**字符级 DNA 信号**，通过**三级坐标共振**（字符/子串/精确）与实体池匹配。

The name "Strand" comes from the concept of DNA strands — multiple independent chains of signal that together form a unique fingerprint.

"Strand" 的名字来源于 DNA 链的概念——多条独立的信号链共同构成唯一的指纹坐标。

## Why Not Vector Search? / 为什么不用向量搜索？

| Aspect | Vector Search | Strand DNA |
|--------|--------------|------------|
| Dependency | embedding model, GPU, vector DB | **zero** — pure stdlib |
| Cold start | needs training / fine-tuning | **instant** — character-level rules |
| Language mixing | struggles with 中英混合 | **native** — script-isolated tokenizer |
| Precision | semantic similarity (fuzzy) | **deterministic** coordinate resonance |
| Speed | 50-500ms per query | **<1ms** matching over 600+ entities |
| Transparency | black box | **fully inspectable** — each score is traceable |
| Footprint | 500MB+ model | **14KB** code + memory pool |

## Pipeline / 管线

```
User Query / 用户查询
    │
    ▼
┌─────────────────────────────┐
│  DNA Signal Extraction      │  character-level, no vocabulary
│  DNA 信号留存               │  字符级，无词表，不分类
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│  Magnetic Resonance         │  3-layer scoring × 994 entities
│  磁吸共振                   │  三级打分 × 全部实体
│  top_k=15                   │  top-1 accuracy 86%
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│  Context Injection          │  <strand_context> formatted
│  上下文注入                  │  ~800-3500 chars, pure matching
└─────────────────────────────┘
    │
    ▼
  LLM Inference / 推理
```

## Core Algorithms / 核心算法

### 1. DNA Signal Extraction / DNA 信号提取

Pure character-level tokenization. No vocabulary, no classification, no discarding.

纯字符级分词。无词表，不分类，不丢弃。

```
Input:  "帮我修一下wsl's network"
Tokens: ['帮我修一下wsl', 's', 'network']
  ↓
4-chain DNA:
  domain:  ['network']           ← English lowercase words
  entity:  ['帮我', '我修', '修一', '一下', 'wsl']  ← Chinese bigrams + English proper nouns
  pattern: []                    ← digits, punctuation
  context: []                    ← reserved chain
```

**Key principle:** DNA is extracted from the text's inherent structure, not assigned by a model. The same text always produces the same DNA. Deterministic.

**核心原则：** DNA 是文本的固有结构特征，不是模型赋予的。同一段文本总是产生相同的 DNA。确定性。

### 2. Coordinate Resonance / 坐标共振

Three-layer overlap scoring between query DNA and entity DNA:

三层结构重叠打分：

| Layer / 层 | What / 内容 | Weight / 权重 |
|------------|------------|--------------|
| Character / 字符级 | Single character overlap / 单字符重叠 | 0.3 |
| Substring / 子串级 | 2+ char consecutive overlap / 连续片段重叠 | 0.3 |
| Exact / 精确级 | Full token match / 完整 token 匹配 | 0.4 |

Each entity is scored in **one pass** — no iteration, no graph traversal, no recursion.

每个实体**一次扫描**完成打分——无迭代、无图遍历、无递归。

### 3. Wormhole Expansion / 虫洞展开（可选）

> **Note:** Default pipeline uses pure matching only. Wormhole is available as a lower-level function for specific use cases where broader associative recall is desired, accepting the precision tradeoff.
>
> **注意：** 默认管线使用纯匹配模式。虫洞展开作为底层函数保留，适用于需要更广泛联想召回且接受精度折损的场景。

Each matched entity emits its own DNA signal to independently find neighbors. Replicas have fixed energy 0.7, never decay, and never modify original entities.

每个匹配实体用自己的 DNA 信号独立寻找邻居。复制体固定能量 0.7，永不衰减，不修改原始实体。

## 8-Chip Architecture / 8 芯片架构

The full Strand ecosystem consists of 8 independent packages ("chips"), each an installable pip package:

完整 Strand 生态由 8 个独立包（"芯片"）组成，每个都是可安装的 pip 包：

```
                          ┌──────────┐
                          │  Router  │  Cross-domain graph routing
                          │  联想引擎  │  跨域图路由
                          └────┬─────┘
                               │
┌──────────┐    ┌──────────┐   │    ┌──────────┐    ┌──────────┐
│ Encoder  │───▶│ Matcher  │───┴───▶│ Regulate │───▶│  Immune  │
│ 编码器    │    │ 匹配引擎   │        │ 安全护栏   │    │ 免疫系统   │
└──────────┘    └──────────┘        └──────────┘    └──────────┘
     │               │                                   │
     ▼               ▼                                   ▼
┌──────────────────────────────────────────────────────────┐
│                     Memory Pool / 记忆池                    │
│              (strand_pool — DNA 本体存储层)                  │
└──────────────────────────────────────────────────────────┘
     │               │                                   │
     ▼               ▼                                   ▼
┌──────────┐    ┌──────────┐    ┌──────────┐
│ Predator │    │Lifecycle │    │   ...    │
│ 养蛊演化   │    │ 生命周期   │    │  future  │
└──────────┘    └──────────┘    └──────────┘
```

### Chip Descriptions / 芯片说明

| Chip / 芯片 | Role / 角色 | Description / 说明 |
|-------------|------------|-------------------|
| **Encoder** | DNA 编码器 | Maps text to multi-chain DNA vectors / 将文本映射到多链 DNA 向量 |
| **Matcher** | 匹配引擎 | Weighted multi-chain voting + anti-chain suppression / 加权多链投票 + 反链抑制 |
| **Predator** | 养蛊演化 | Cannibalize similar entities, hybrid crossover, rank survival / 同类吞噬、杂交、排名生存 |
| **Lifecycle** | 生命周期 | Ebbinghaus half-life decay, fossil revival / 艾宾浩斯半衰期衰减、化石复活 |
| **Immune** | 免疫系统 | Disagreement-driven learning, antibody auto-generation / 分歧驱动学习，抗体自动生成 |
| **Regulate** | 安全护栏 | Intent collision detection against iron laws / 意图碰撞检测，对照铁律审查 |
| **Router** | 联想引擎 | Cross-domain BFS graph routing / 跨域 BFS 图路由 |
| **Pool** | 本体存储 | DNA-grounded entity storage, load/save/persistence / DNA 实体存储，加载/保存/持久化 |

## Project Structure / 项目结构

```
strand-prefetch/
├── ARCHITECTURE.md          # This document / 本文档
├── README.md                # Quick start / 快速开始
├── LICENSE                  # MIT
├── pyproject.toml
├── strand_prefetch/         # Core pipeline / 核心管线
│   ├── __init__.py          #   Public API / 公共接口
│   ├── dna.py               #   DNA signal extraction / DNA 信号提取
│   ├── resonance.py         #   Coordinate resonance / 坐标共振匹配
│   ├── wormhole.py          #   Wormhole expansion / 虫洞展开
│   ├── render.py            #   Context formatting / 上下文格式化
│   └── pool.py              #   Memory pool / 记忆池管理
├── chips/                   # 8-chip reference / 8芯片参考
│   ├── __init__.py
│   ├── encoder.py           #   Multi-chain DNA encoder / 多链DNA编码
│   ├── matcher.py           #   Weighted voting matcher / 加权投票匹配
│   ├── predator.py          #   Cannibalize & evolve / 吞噬与演化
│   ├── lifecycle.py         #   Ebbinghaus half-life / 艾宾浩斯半衰期
│   ├── immune.py            #   Disagreement learning / 分歧学习
│   ├── regulate.py          #   Intent collision / 意图碰撞检测
│   ├── router.py            #   Graph routing / 图路由
│   └── pool.py              #   Entity storage / 实体存储
├── data/
│   └── seed_pool.json       # Seed entity pool (22 demo entities)
└── examples/
    ├── basic.py             # Python API example
    ├── cli.py               # CLI tool
    └── benchmark.py         # 7-dimension benchmark suite
```

## Performance Benchmarks / 性能基准

| Dimension / 维度 | Metric / 指标 | Result / 结果 |
|-----------------|--------------|--------------|
| Speed / 速度 | Average latency | **9ms** (seed) / **110ms** (994 full pool) |
| Precision / 精度 | Top-1 accuracy | **86%** |
| | P@5 | **74%** |
| Response / 响应 | P50 / P95 / P99 | **8ms / 13ms / 18ms** |
| Memory / 内存 | Resident set | **14.1 MB** |
| Energy / 能耗 | Pool load | **27.8 KB** |
| Dependencies / 依赖 | pip packages required | **zero** |

## Philosophy / 哲学

1. **DNA is a fingerprint, not a label** — extracted from inherent structure, not assigned by a model
2. **Matching is resonance, not translation** — character-level coordinate overlap, not semantic similarity
3. **Pure matching beats associative expansion** — one hop is optimal, more hops introduce noise
4. **Zero external dependencies** — pure Python stdlib, no models, no GPUs, no vector DBs
5. **Deterministic and inspectable** — same input always produces same output, each score is traceable

---

*Strand Prefetch v0.1.0 — Built by zym15, 2026*
