"""LongMemEval on Strand Prefetch — 长记忆召回评测

Adapts the LongMemEval benchmark (500 questions, haystack-based) to Strand's
prefetch pipeline. Each haystack session becomes a memory pool entity.
The question is the query. Success = answer_session_ids in top-k matches.

LongMemEval: https://huggingface.co/datasets/xiaowu0162/longmemeval
"""

import sys, os, json, time, statistics

sys.path.insert(0, os.path.expanduser('~'))
from strand_prefetch import prefetch, extract_dna_signal, magnetic_resonance, compute_idf
from strand_prefetch.pool import MemoryPool


def load_questions(path: str) -> list[dict]:
    """Load LongMemEval JSONL / 加载 LongMemEval 评测集"""
    questions = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                questions.append(json.loads(line))
    return questions


def haystack_to_entities(q: dict) -> list[dict]:
    """Convert haystack sessions to Strand entities / 将对话历史转换为 Strand 实体

    Each session becomes one entity. The content is the concatenated turns.
    每个会话变成一个实体，内容为对话拼接文本。
    """
    haystack = q.get("haystack_sessions", [])
    session_ids = q.get("haystack_session_ids", [])
    dates = q.get("haystack_dates", [])

    entities = []
    for i, session in enumerate(haystack):
        sid = session_ids[i] if i < len(session_ids) else f"s{i}"
        date_str = f" [{dates[i]}]" if i < len(dates) and dates[i] else ""

        # Concatenate all turns / 拼接所有轮次
        parts = []
        for turn in session:
            role = turn.get("role", "?")
            content = turn.get("content", "")
            parts.append(f"[{role}] {content}")

        text = f"Session {sid}{date_str}: " + " | ".join(parts)
        entities.append({
            "id": f"session:{sid}",
            "text": text,
            "energy": 0.5,
            "source": "longmemeval",
            "pinned": False,
            "dna": {},
        })

    return entities


def evaluate_question(q: dict, entities: list[dict], top_k: int = 15,
                      idf_weights: dict = None) -> dict:
    """Run one LongMemEval question / 运行一条 LongMemEval 问题"""
    question = q.get("question", "")
    answer_sessions = set(q.get("answer_session_ids", []))
    qid = q.get("question_id", "?")

    # Run Strand prefetch / 运行 Strand 预取
    t0 = time.perf_counter()

    # Build memory pool / 构建记忆池
    pool = MemoryPool()
    pool.entities = entities
    all_ents = pool.entities

    signal = extract_dna_signal(question)
    matches = magnetic_resonance(signal, all_ents, top_k=top_k,
                                 idf_weights=idf_weights,
                                 enable_chunking=True)
    dt = (time.perf_counter() - t0) * 1000

    # Check recall / 检查召回
    retrieved_ids = set()
    for m in matches:
        mid = m.get("id", "")
        if mid.startswith("session:"):
            retrieved_ids.add(mid.replace("session:", ""))

    # Hit analysis / 命中分析
    hits = retrieved_ids & answer_sessions
    hit_count = len(hits)
    total_answer = len(answer_sessions)
    recall = hit_count / max(total_answer, 1)

    # Precision / 精度
    retrieved_count = len(retrieved_ids)
    precision = hit_count / max(retrieved_count, 1)

    # F1 / 调和平均
    f1 = 2 * precision * recall / max(precision + recall, 0.001)

    return {
        "qid": qid,
        "question": question[:60],
        "type": q.get("question_type", "?"),
        "answer_sessions": total_answer,
        "hits": hit_count,
        "recall": recall,
        "precision": precision,
        "f1": round(f1, 3),
        "latency_ms": round(dt, 1),
        "retrieved": retrieved_count,
        "top_match": matches[0].get("id", "?") if matches else "none",
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="LongMemEval on Strand Prefetch")
    parser.add_argument("--data",
        default=os.path.expanduser("~/gbrain/test/fixtures/longmemeval-nightly.jsonl"),
        help="LongMemEval JSONL path")
    parser.add_argument("--top-k", type=int, default=25)
    parser.add_argument("--full-dataset",
        help="Path to full 500-question dataset (download from HuggingFace)")
    parser.add_argument("--quiet", action="store_true",
        help="Suppress per-question output / 关闭逐题输出")
    args = parser.parse_args()

    questions = load_questions(args.data)
    print(f"LongMemEval: {len(questions)} questions")
    print(f"Strand top-k: {args.top_k}")

    # Pre-compute IDF weights for each question's haystack / 为每个查询预计算 IDF 权重
    print("Computing IDF weights for each question...")
    all_idf = []
    for q in questions:
        entities = haystack_to_entities(q)
        idf = compute_idf(entities)
        all_idf.append(idf)
    print(f"  Done. Avg {sum(len(i) for i in all_idf)/len(all_idf):.0f} tokens/question\n")

    # Stats by type / 按类型统计
    by_type: dict[str, list] = {}

    results = []
    for idx, q in enumerate(questions):
        entities = haystack_to_entities(q)
        r = evaluate_question(q, entities, args.top_k, idf_weights=all_idf[idx])
        results.append(r)

        qtype = r["type"]
        if qtype not in by_type:
            by_type[qtype] = []
        by_type[qtype].append(r)

        if not args.quiet:
            hits_str = f"{r['hits']}/{r['answer_sessions']}"
            print(f"  {r['qid']:15s} {qtype:25s} "
                  f"recall={r['recall']:.0%} precision={r['precision']:.0%} "
                  f"F1={r['f1']:.3f} [{r['latency_ms']:5.0f}ms] "
                  f"top={r['top_match'][:25]:25s}")

    # Overall summary / 总览
    print(f"\n{'='*60}")
    print(f"  LongMemEval Summary / 总览")
    print(f"{'='*60}")
    all_recall = [r["recall"] for r in results]
    all_precision = [r["precision"] for r in results]
    all_f1 = [r["f1"] for r in results]
    all_latency = [r["latency_ms"] for r in results]

    print(f"  Questions:           {len(results)}")
    print(f"  Recall:              {statistics.mean(all_recall):.0%}")
    print(f"  Precision:           {statistics.mean(all_precision):.0%}")
    print(f"  F1:                  {statistics.mean(all_f1):.3f}")
    print(f"  Latency:             {statistics.mean(all_latency):.0f}ms")
    print(f"  Full matches:        {sum(1 for r in results if r['hits'] == r['answer_sessions'])}/{len(results)}")
    print(f"  Zero hits:           {sum(1 for r in results if r['hits'] == 0)}/{len(results)}")

    # By type / 按类型
    print(f"\n{'─'*60}")
    print(f"  By Question Type / 按问题类型")
    print(f"{'─'*60}")
    for qtype, qresults in sorted(by_type.items()):
        t_recall = statistics.mean([r["recall"] for r in qresults])
        t_precision = statistics.mean([r["precision"] for r in qresults])
        t_f1 = statistics.mean([r["f1"] for r in qresults])
        print(f"  {qtype:25s} n={len(qresults):2d}  "
              f"recall={t_recall:.0%} precision={t_precision:.0%} F1={t_f1:.3f}")


if __name__ == "__main__":
    main()
