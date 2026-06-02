"""Strand Prefetch 基础使用示例。"""

import os, sys

# 确保能找到 strand_prefetch 包
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from strand_prefetch import prefetch
from strand_prefetch.pool import MemoryPool

# 加载种子池
pool_path = os.path.join(os.path.dirname(__file__), "..", "data", "seed_pool.json")
pool = MemoryPool.load(pool_path)
print(f"实体池: {len(pool)} 实体, {len(pool.pinned)} pinned\n")

# 测试查询
queries = [
    "帮我修一下wsl",
    "github怎么创建pr",
    "测试驱动开发",
    "DNA提取原理",
    "GPU成本优化",
    "调试agent问题",
]

for q in queries:
    result, matches, replicas = prefetch(q, pool.entities)

    if not result:
        print(f'╔══ "{q}" — 无匹配')
        print("╚")
        print()
        continue

    lines = result.split("\n")
    source_info = {}
    for e in matches + replicas:
        src = e.get("source", "?")
        source_info[src] = source_info.get(src, 0) + 1
    sources = ", ".join(f"{k}={v}" for k, v in source_info.items())

    print(f'╔══ "{q}"')
    print(f'║  匹配: {len(matches)} 虫洞: {len(replicas)} | 来源: {sources}')
    print(f'║  体积: {len(result)} chars')

    # 打印前几名
    for i, e in enumerate(matches[:3]):
        text = e.get("text", "")[:60].replace("\n", " ")
        print(f'║  #{i+1} [{e.get("source","?")}] (score={e.get("_score",0):.4f}) {text}')
    print("╚")
    print()
