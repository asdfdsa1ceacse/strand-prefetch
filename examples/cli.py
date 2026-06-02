#!/usr/bin/env python3
"""Strand Prefetch CLI — 在终端中直接使用。"""

import sys, os, json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from strand_prefetch import prefetch, extract_dna_signal
from strand_prefetch.pool import MemoryPool


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Strand Prefetch CLI")
    parser.add_argument("query", nargs="?", help="查询文本")
    parser.add_argument(
        "--pool",
        default=os.path.join(os.path.dirname(__file__), "..", "data", "seed_pool.json"),
        help="记忆池 JSON 路径",
    )
    parser.add_argument("--top-k", type=int, default=5, help="初始匹配数")
    parser.add_argument("--hops", type=int, default=1, help="虫洞展开跳数")
    parser.add_argument("--signal", action="store_true", help="只显示 DNA 信号")
    parser.add_argument("--inspect", action="store_true", help="检查实体池统计")

    args = parser.parse_args()

    if args.inspect:
        pool = MemoryPool.load(args.pool)
        sources = {}
        for e in pool.entities:
            s = e.get("source", "?")
            sources[s] = sources.get(s, 0) + 1
        print(f"实体: {len(pool)}")
        print(f"Pinned: {len(pool.pinned)}")
        print(f"来源分布: {sources}")
        return

    if not args.query:
        parser.print_help()
        return

    if args.signal:
        sig = extract_dna_signal(args.query)
        for chain, vals in sig.items():
            if vals:
                print(f"  {chain}: {', '.join(vals[:8])}")
        return

    pool = MemoryPool.load(args.pool)
    result, matches, replicas = prefetch(args.query, pool.entities, args.top_k, args.hops)
    print(result)


if __name__ == "__main__":
    main()
