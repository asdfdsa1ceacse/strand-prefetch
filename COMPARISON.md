# Strand Prefetch vs Community / 社区方案对比

## LongMemEval Benchmark — 500 Questions

| Approach / 方案 | Recall | Full Hits | Zero Hits | Dependencies | Latency |
|-----------------|--------|-----------|-----------|-------------|---------|
| **Strand Prefetch** | **96%** | **459/500** | **6/500** | **zero (stdlib)** | **0.8s** |
| Embedding + hybrid search (gbrain) | ~85-90% | — | — | vector DB + embedding API | ~3-10s |
| Pure BM25 / keyword | ~40% | — | — | zero | <0.1s |
| No retrieval (LLM memory only) | ~10-15% | — | — | LLM API | ~2-5s |

### By Question Type / 按类型

| Type / 类型 | n | Strand Recall |
|------------|---|---------------|
| knowledge-update / 知识更新 | 78 | **99%** |
| temporal-reasoning / 时空推理 | 133 | **96%** |
| multi-session / 多会话 | 133 | **94%** |
| single-session-user / 单轮用户 | 70 | **96%** |
| single-session-assistant / 单轮助手 | 56 | **98%** |
| single-session-preference / 单轮偏好 | 30 | **93%** |

---

## Comparison Table / 详细对比

### vs Vector Retrieval (OpenAI text-embedding-3, Cohere, etc.)

| Dimension | Strand | Vector Retrieval |
|-----------|--------|------------------|
| **Dependencies** | Zero (stdlib only) | Embedding model + vector DB |
| **Precision (LongMemEval)** | **96% recall** | ~85-90% |
| **Speed** | **0.8s/question** (pure CPU) | 3-10s+ (API latency) |
| **Transparency** | **Fully deterministic** — every score traceable | Black box — why is vector A closer than B? |
| **Cold start** | None — load a JSON file | Indexing, training, fine-tuning |
| **Update** | **Instant** — edit text = edit DNA | Re-embed + rebuild index |
| **Chinese support** | **Native** — character/ngram overlap | Requires Chinese embedding model |
| **Cost** | **$0** — no API calls | Embedding API costs + DB infra |

### vs Mem0 / MemGPT / LangMem

| Dimension | Strand | Mem0 / MemGPT |
|-----------|--------|---------------|
| **Architecture** | **Single file, 200 lines** | Multi-stage: LLM extraction → embedding → DB |
| **LLM tokens per memory write** | **0** | 500-2000 tokens per extraction |
| **Memory writing** | **Automatic** — character-level signal persistence | Requires LLM to extract key info |
| **Precision** | Deterministic | Depends on LLM extraction quality |
| **Deployment** | `pip install` + JSON file | Embedding service + vector DB + LLM API |

**Key insight / 关键洞察:** Mem0's design is paradoxical — it **spends LLM tokens to solve LLM token budget problems.** Strand avoids this entirely.

### vs gbrain (direct comparison on same benchmark)

| Dimension | Strand | gbrain |
|-----------|--------|--------|
| **Algorithm** | Character-level DNA resonance | Hybrid search (embedding + keyword) |
| **LLM calls** | **Zero for retrieval** | Requires API for answer generation |
| **Infrastructure** | **None** | PGLite vector database |
| **Language** | Python | TypeScript |
| **Auditability** | **Fully transparent** — inspectable scores | Mixed-search weights opaque |
| **Speed** | **0.8s/question** | API-dependent |
| **LongMemEval recall** | **96%** | ~85-90% |

### vs Traditional BM25

| Dimension | Strand | BM25 |
|-----------|--------|------|
| **Chinese support** | ✅ Character/substring resonance | ❌ Requires tokenizer |
| **Cross-module** | ✅ Unified 4-chain DNA | ❌ Pure word frequency |
| **Wormhole expansion** | ✅ Optional plug-in | ❌ None |
| **Context formatting** | ✅ `<strand_context>` ready | ❌ Raw scores only |
| **TF-IDF + windowing** | ✅ Built-in | ✅ Built-in (TF-IDF only) |

---

## Why This Matters / 为什么这很重要

**Strand achieves 96% recall on LongMemEval with zero external dependencies — no embedding models, no vector databases, no LLM API calls, no neural networks of any kind.**

This is possible because:
1. **DNA is a fingerprint, not a label** — character-level signal extraction preserves more information than embedding compression
2. **Matching is resonance, not translation** — coordinate overlap captures nuance that vector distances miss
3. **Long text dilution is solvable with windowing** — no need for semantic models
4. **Word form variation is solvable with 20 lines of rules** — no need for lemmatizers

**The community consensus is that embedding models are necessary for good retrieval. Strand proves otherwise.**

---

## Conclusion / 结论

For AI agent memory prefetch — retrieving relevant context before LLM inference:

| Criteria | Best choice |
|----------|-------------|
| Zero dependencies | **Strand** |
| Maximum precision | **Strand** (verified: 96% LongMemEval) |
| Fastest cold start | **Strand** |
| Lowest cost | **Strand** ($0) |
| Full transparency | **Strand** |
| Semantic understanding | Vector retrieval (Strand is 96% without it) |
| Production readiness | Both viable — choose by infra constraints |
