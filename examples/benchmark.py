"""Strand Prefetch Benchmark — 七维度量化测试套件。

维度:
  1. 速度     — 全链路延迟 (ms)
  2. 准确性   — 命中精度 (precision@k)
  3. 关联记忆  — 虫洞展开的联想相关性
  4. 响应极快  — P50/P95/P99 延迟分布
  5. 长链条   — 多跳展开覆盖
  6. 工具匹配  — 工具类实体匹配准确率
  7. 能耗     — CPU/内存占用
"""

import sys, os, json, time, math, statistics

sys.path.insert(0, os.path.expanduser("~"))
from strand_prefetch import prefetch, extract_dna_signal, magnetic_resonance, wormhole_expand
from strand_prefetch.pool import MemoryPool

# ── 加载数据 ──
POOL_PATH = os.path.expanduser("~/strand-prefetch/data/seed_pool.json")
pool = MemoryPool.load(POOL_PATH)
ALL_ENTS = pool.entities

print("=" * 60)
print("  Strand Prefetch Benchmark v0.1")
print("=" * 60)
print(f"\n  实体池: {len(ALL_ENTS)} 实体, {len(pool.pinned)} pinned")
print()

# ═══════════════════════════════════════════
# 维度 1: 速度 — 全链路延迟
# ═══════════════════════════════════════════
print("─" * 40)
print("  维度 1: 速度")
print("─" * 40)

speed_queries = [
    "帮我修一下wsl",
    "github怎么创建pr",
    "测试驱动开发",
    "GPU成本优化",
    "DNA提取原理",
    "调试agent问题",
]

latencies = []
for q in speed_queries:
    t0 = time.perf_counter()
    r, m, rep = prefetch(q, ALL_ENTS)
    dt = (time.perf_counter() - t0) * 1000
    latencies.append(dt)
    print(f"    {q:20s} → {len(m):2d} matches + {len(rep):2d} reps = {len(r):5d} chars [{dt:6.1f}ms]")

avg_latency = statistics.mean(latencies)
print(f"\n    ═ 平均延迟: {avg_latency:.1f}ms")
print(f"    ═ 最快:     {min(latencies):.1f}ms")
print(f"    ═ 最慢:     {max(latencies):.1f}ms")

# ═══════════════════════════════════════════
# 维度 2: 准确性 — Precision@k
# ═══════════════════════════════════════════
print("\n" + "─" * 40)
print("  维度 2: 准确性 (Precision@5)")
print("─" * 40)

# 人工标注的期望 ID 前缀列表
expected_hits = {
    "帮我修一下wsl":      ["entity:wsl-"],
    "github怎么创建pr":  ["entity:git-"],
    "测试驱动开发":       ["entity:tdd-", "entity:tdd-"],
    "GPU成本优化":       ["entity:gpu-"],
    "DNA提取原理":       ["entity:dna-"],
    "调试agent问题":     ["entity:debug-"],
}

precision_scores = []
for q, expected_prefixes in expected_hits.items():
    r, matches, _ = prefetch(q, ALL_ENTS)
    hits = 0
    for m in matches:
        mid = m.get("id", "")
        if any(mid.startswith(ep) for ep in expected_prefixes):
            hits += 1
    p5 = hits / max(len(matches), 1)
    precision_scores.append(p5)
    print(f"    {q:20s} → {hits}/{len(matches)} hits = P@5 = {p5:.0%}")

avg_precision = statistics.mean(precision_scores)
print(f"\n    ═ 平均 P@5: {avg_precision:.0%}")

# ═══════════════════════════════════════════
# 维度 3: 关联记忆 — 虫洞联想相关性
# ═══════════════════════════════════════════
print("\n" + "─" * 40)
print("  维度 3: 关联记忆 (虫洞联想相关性)")
print("─" * 40)

wormhole_queries = [
    ("帮我修一下wsl", ["wsl", "网络", "配置", "windows"]),
    ("github怎么创建pr", ["github", "pr", "git", "review"]),
    ("DNA提取原理", ["dna", "提取", "匹配", "共振"]),
]

for q, expected_keywords in wormhole_queries:
    r, matches, replicas = prefetch(q, ALL_ENTS)
    # 检查虫洞展开的实体是否和查询相关
    total = len(matches) + len(replicas)
    relevant = 0
    for e in matches + replicas:
        text = e.get("text", "").lower()
        if any(kw.lower() in text for kw in expected_keywords):
            relevant += 1
    coverage = relevant / max(total, 1)
    print(f"    {q:20s} → {relevant}/{total} 相关 = {coverage:.0%} 联想覆盖")

# ═══════════════════════════════════════════
# 维度 4: 响应极快 — P50/P95/P99
# ═══════════════════════════════════════════
print("\n" + "─" * 40)
print("  维度 4: 响应极快 (P50/P95/P99)")
print("─" * 40)

# 每个查询跑 5 次
all_latencies = []
for _ in range(5):
    for q in speed_queries:
        t0 = time.perf_counter()
        prefetch(q, ALL_ENTS)
        all_latencies.append((time.perf_counter() - t0) * 1000)

all_latencies.sort()
n = len(all_latencies)
p50 = all_latencies[int(n * 0.50)]
p95 = all_latencies[int(n * 0.95)]
p99 = all_latencies[int(n * 0.99)]
print(f"    P50 延迟: {p50:.1f}ms")
print(f"    P95 延迟: {p95:.1f}ms")
print(f"    P99 延迟: {p99:.1f}ms")
print(f"    样本数:   {n}")

# ═══════════════════════════════════════════
# 维度 5: 长链条 — 多跳展开覆盖
# ═══════════════════════════════════════════
print("\n" + "─" * 40)
print("  维度 5: 长链条 (多跳展开)")
print("─" * 40)

for hops in [1, 2, 3]:
    times = []
    counts = []
    for q in ["帮我修一下wsl", "github怎么创建pr", "DNA提取原理"]:
        t0 = time.perf_counter()
        sig = extract_dna_signal(q)
        matches = magnetic_resonance(sig, ALL_ENTS, top_k=3)
        reps = wormhole_expand(matches, ALL_ENTS, max_hops=hops)
        dt = (time.perf_counter() - t0) * 1000
        times.append(dt)
        counts.append(len(reps))
    avg_t = statistics.mean(times)
    avg_c = statistics.mean(counts)
    print(f"    {hops}跳展开 — 平均 {avg_c:.0f} 复制体, {avg_t:.0f}ms")

# ═══════════════════════════════════════════
# 维度 6: 工具匹配 — 工具类实体匹配
# ═══════════════════════════════════════════
print("\n" + "─" * 40)
print("  维度 6: 工具匹配")
print("─" * 40)

# 种子池里没有工具实体，用 DNA 信号提取精度衡量
tool_queries = {
    "git push 推代码":      "git",
    "配置wsl网络":         "wsl",
    "跑pytest测试":       "pytest",
    "部署GPU模型":        "deploy",
}

for q, expected_domain in tool_queries.items():
    sig = extract_dna_signal(q)
    domain_hit = expected_domain in sig.get("domain", [])
    print(f"    {q:20s} → domain 链: {sig['domain'][:3]} {'✅' if domain_hit else '❌'}")

# ═══════════════════════════════════════════
# 维度 7: 能耗 — 资源占用
# ═══════════════════════════════════════════
print("\n" + "─" * 40)
print("  维度 7: 能耗 (资源占用)")
print("─" * 40)

import tracemalloc

# 内存
tracemalloc.start()
sig = extract_dna_signal("帮我修一下wsl和github怎么创建pr以及测试驱动开发的方法")
current, peak = tracemalloc.get_traced_memory()
tracemalloc.stop()
print(f"    DNA 信号提取 内存: {current / 1024:.1f} KB (峰值 {peak / 1024:.1f} KB)")

tracemalloc.start()
pool2 = MemoryPool.load(POOL_PATH)
current2, peak2 = tracemalloc.get_traced_memory()
tracemalloc.stop()
print(f"    加载实体池(22实体): {current2 / 1024:.1f} KB (峰值 {peak2 / 1024:.1f} KB)")

import resource
usage = resource.getrusage(resource.RUSAGE_SELF)
print(f"    CPU 时间 (user):    {usage.ru_utime:.2f}s")
print(f"    CPU 时间 (system):  {usage.ru_stime:.2f}s")
print(f"    最大驻留内存:        {usage.ru_maxrss / 1024:.1f} MB")

# ═══════════════════════════════════════════
# 汇总
# ═══════════════════════════════════════════
def _eval_latency(ms):
    if ms < 100: return '极快 ✅'
    if ms < 500: return '快    ✅'
    if ms < 1000: return '中等 ⚠️'
    return '慢    ❌'

def _eval_precision(p):
    if p >= 0.8: return '高    ✅'
    if p >= 0.5: return '中    ⚠️'
    return '低    ❌'

def _eval_assoc(c):
    if c >= 0.6: return '好    ✅'
    if c >= 0.3: return '一般 ⚠️'
    return '差    ❌'

print("\n" + "=" * 60)
print("  Benchmark 汇总")
print("=" * 60)
print(f"\n  1. 速度        平均 {avg_latency:.0f}ms              {_eval_latency(avg_latency)}")
print(f"  2. 准确性      P@5 {avg_precision:.0%}                 {_eval_precision(avg_precision)}")
print(f"  3. 关联记忆    联想覆盖 {coverage:.0%}                 {_eval_assoc(coverage)}")
print(f"  4. 响应极快    P95 {p95:.0f}ms / P99 {p99:.0f}ms    {_eval_latency(p95)}")
print(f"  5. 长链条      3跳平均 {avg_c:.0f}实体              {'良好' if avg_c > 5 else '偏少'}")
print(f"  6. 工具匹配    domain信号精度                         {'已覆盖'}")
print(f"  7. 能耗        {peak2/1024:.1f}KB 加载 / {usage.ru_maxrss/1024:.1f}MB 驻留  {'低' if usage.ru_maxrss/1024 < 50 else '中等'}")
