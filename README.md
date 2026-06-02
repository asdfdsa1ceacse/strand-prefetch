# Strand Prefetch

> **DNA 是指纹，不是标签。匹配是坐标共振，不是语义翻译。**
> **DNA is a fingerprint, not a label. Matching is coordinate resonance, not semantic translation.**

Zero-dependency cognitive prefetch pipeline for AI agents. Character-level DNA signal extraction + magnetic resonance matching + context injection.

零依赖 AI 智能体认知预取管线。字符级 DNA 信号提取 + 磁吸共振匹配 + 上下文注入。

```python
from strand_prefetch import prefetch
from strand_prefetch.pool import MemoryPool

pool = MemoryPool.load("data/seed_pool.json")
result, matches, _ = prefetch("帮我修一下wsl", pool.entities)
print(result)
# → <strand_context> ... </strand_context>
```

## Benchmark / 基准测试

| 维度 | 指标 | 结果 |
|------|------|------|
| Speed / 速度 | Average / 平均 | **9ms** (seed) / **110ms** (994 pool) |
| Precision / 精度 | Top-1 | **86%** |
| | P@5 | **74%** |
| Response / 响应 | P95 | **13ms** |
| Memory / 内存 | RSS | **14.1 MB** |
| Dependencies / 依赖 | pip packages | **zero** |

## Pipeline / 管线

```
Query / 查询
  ↓
extract_dna_signal()    Character-level / 字符级 (无词表, <0.01ms)
  ↓
magnetic_resonance()    Top-k=15 matching / 磁吸匹配 (三级共振)
  ↓
<strand_context>        Formatted injection / 格式化注入 (800-3500 chars)
```

**Pure matching mode — no wormhole expansion.** All entities filtered through the same query DNA signal. `wormhole_expand()` available as low-level function.

**纯匹配模式，无虫洞展开。** 所有注入实体经同一套查询 DNA 信号筛选。`wormhole_expand()` 作为底层函数保留。

## 8-Chip Architecture / 8 芯片架构

| Chip / 芯片 | Role / 角色 |
|-------------|------------|
| **Encoder** | DNA encoding / 多链 DNA 编码 |
| **Matcher** | Weighted voting / 加权投票匹配 |
| **Predator** | Cannibalize & evolve / 吞噬演化 |
| **Lifecycle** | Ebbinghaus decay / 艾宾浩斯衰减 |
| **Immune** | Disagreement learning / 分歧学习 |
| **Regulate** | Intent collision / 意图碰撞检测 |
| **Router** | Graph routing / 图路由 |
| **Pool** | Entity storage / 实体存储 |

See [ARCHITECTURE.md](ARCHITECTURE.md) for full explanation of each chip.
详见 [ARCHITECTURE.md](ARCHITECTURE.md) 完整架构说明。

## Install / 安装

```bash
# From GitHub / 从 GitHub
pip install git+https://github.com/asdfdsa1ceacse/strand-prefetch.git

# Or locally / 或本地
git clone https://github.com/asdfdsa1ceacse/strand-prefetch.git
cd strand-prefetch
pip install -e .
```

## Usage / 使用

### Python API

```python
from strand_prefetch import prefetch, extract_dna_signal, coordinate_resonance
from strand_prefetch.pool import MemoryPool

# Load pool / 加载实体池
pool = MemoryPool.load("data/seed_pool.json")

# Run pipeline / 运行管线
result, matches, _ = prefetch("github怎么创建pr", pool.entities)
print(result)
# → <strand_context> ... </strand_context>

# Inspect DNA signal / 查看 DNA 信号
sig = extract_dna_signal("GPU成本优化")
print(sig)
# → {'domain': ['gpu'], 'entity': ['成本优化'], 'pattern': [], 'context': []}
```

### CLI

```bash
# Query / 查询
python examples/cli.py "帮我修一下wsl"

# Show DNA signal only / 只看 DNA 信号
python examples/cli.py "GPU成本优化" --signal

# Inspect pool / 检查实体池
python examples/cli.py --inspect
```

### Benchmark / 跑基准

```bash
python examples/benchmark.py
```

## Project Structure / 项目结构

```
strand-prefetch/
├── ARCHITECTURE.md          # Full architecture / 完整架构文档
├── README.md                # This file
├── pyproject.toml           # Package config
├── LICENSE                  # MIT
├── strand_prefetch/         # Core pipeline / 核心管线
│   ├── __init__.py          #   Public API
│   ├── dna.py               #   DNA signal extraction
│   ├── resonance.py         #   Magnetic matching
│   ├── wormhole.py          #   Wormhole expansion
│   ├── render.py            #   Context formatting
│   └── pool.py              #   Memory pool manager
├── chips/                   # 8-chip reference / 8芯片参考
│   ├── __init__.py
│   ├── encoder.py matcher.py predator.py
│   ├── lifecycle.py immune.py regulate.py
│   ├── router.py pool.py
├── data/
│   └── seed_pool.json       # Demo entity pool
└── examples/
    ├── basic.py             # Python API demo
    ├── cli.py               # CLI tool
    └── benchmark.py         # 7-dimension benchmark
```

## Philosophy / 哲学

1. **DNA is a fingerprint, not a label** — extracted from inherent structure, not assigned
2. **Matching is resonance, not translation** — character-level coordinate overlap
3. **Pure matching beats associative expansion** — one hop is optimal
4. **Zero external dependencies** — pure stdlib, no GPU, no vector DB
5. **Deterministic and inspectable** — same input = same output, traceable scores

## License / 许可

MIT
