# Strand Prefetch

字符级 DNA 信号留存 + 磁吸共振 + 虫洞展开 — 零依赖认知预取管线。

```python
from strand_prefetch import prefetch
from strand_prefetch.pool import MemoryPool

pool = MemoryPool.load("data/seed_pool.json")
result, matches, replicas = prefetch("帮我修一下wsl", pool.entities)
print(result)
# → <strand_context> ... </strand_context>
```

## 核心思想

传统语义搜索依赖词表、嵌入向量、分类标签。Strand Prefetch 完全不同：

**DNA 是指纹，不是标签。** 从文本的原始字符结构中提取信号，不做"分类"——不做"这个 token 属于什么类别"的决定。匹配是坐标共振，不是语义相似度。

## 管线

```
查询文本
  ↓
extract_dna_signal()   字符级信号留存（无词表，不分类）
  ↓
magnetic_resonance()   磁吸共振（字符/子串/精确三级）
  ↓
wormhole_expand()      虫洞联想展开（固定能量 0.7，1跳）
  ↓
_format_for_injection() <strand_context> 注入格式
```

## 安装

```bash
git clone https://github.com/zym15/strand-prefetch.git
cd strand-prefetch
pip install -e .
```

## 使用

### Python API

```python
from strand_prefetch import prefetch
from strand_prefetch.pool import MemoryPool

pool = MemoryPool.load("data/seed_pool.json")
result, matches, replicas = prefetch("github怎么创建pr", pool.entities)

# result: <strand_context> 格式的注入文本
# matches: 初始匹配的 top-5 实体（含 _score）
# replicas: 虫洞展开的新实体
```

### CLI

```bash
# 基本查询
python examples/cli.py "帮我修一下wsl"

# 只看 DNA 信号
python examples/cli.py "GPU成本优化" --signal
#  domain: gpu
#  entity: 成本优化

# 检查实体池
python examples/cli.py --inspect
#  实体: 22
#  Pinned: 10
#  来源分布: {'seed': 19, 'hub_3d': 3}
```

## 性能基准

| 操作 | 耗时 |
|------|------|
| DNA 信号留存 | < 0.01ms |
| 磁吸匹配（649 实体） | ~11ms |
| 虫洞展开 1 跳 | ~35ms |
| 全链路（典型） | ~50ms |

## 项目结构

```
strand-prefetch/
├── strand_prefetch/
│   ├── __init__.py      # 公共 API: prefetch()
│   ├── dna.py           # extract_tokens, extract_dna_signal
│   ├── resonance.py     # coordinate_resonance, magnetic_resonance
│   ├── wormhole.py      # wormhole_expand
│   ├── render.py        # _format_for_injection
│   └── pool.py          # MemoryPool 实体池管理
├── data/
│   └── seed_pool.json   # 种子实体池（22 实体）
├── examples/
│   ├── basic.py         # Python API 示例
│   └── cli.py           # CLI 工具
├── pyproject.toml
├── README.md
└── LICENSE
```

## 零依赖

纯 Python stdlib，无第三方依赖。只需要 Python ≥ 3.10。

## License

MIT
