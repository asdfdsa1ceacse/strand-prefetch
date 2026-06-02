"""Strand Pool / 记忆存储芯片

DNA-grounded entity storage. The central repository for all entities
in the Strand ecosystem. Each entity has DNA, energy, source tags,
and optional metadata.

DNA 本体存储层。Strand 生态中所有实体的中央仓库。
每个实体含 DNA、能量、来源标签和可选元数据。

Original: strand-pool (pip package)
"""

from typing import Dict, List, Optional, Any
from .encoder import encode
from .lifecycle import decay


class MemoryPool:
    """DNA-grounded memory pool / DNA 本体记忆存储池

    This is the original strand-pool MemoryPool.
    The strand_prefetch.pool.MemoryPool is a simplified standalone version.
    这是原始 strand-pool 的 MemoryPool。strand_prefetch.pool.MemoryPool 是简化独立版。
    """

    def __init__(self):
        self.entities: List[Dict] = []
        self.pinned: set = set()
        self._version: int = 0

    def add(
        self,
        eid: str,
        text: str,
        source: str = "hermes",
        pinned: bool = False,
        energy: float = 0.5,
        meta: Optional[Dict] = None,
    ) -> Dict:
        """Add entity with auto DNA encoding / 添加实体并自动编码 DNA"""
        dna = encode(text)  # Auto-encode / 自动编码
        entity = {
            "id": eid,
            "text": text,
            "dna": dna,
            "energy": energy,
            "pinned": pinned,
            "source": source,
            "meta": meta or {},
            "created": __import__("time").time(),
        }
        self.entities.append(entity)
        if pinned:
            self.pinned.add(eid)
        return entity

    def recall(self, query: str, top_k: int = 5) -> List[Dict]:
        """Recall entities by query / 按查询召回实体

        Extracts query DNA and returns top-k matches.
        Includes energy decay and lifecycle checks.
        提取查询 DNA 并返回 top-k 匹配。含能量衰减和生命周期检查。
        """
        from .matcher import match

        query_dna = encode(query)
        candidates = [decay(e) for e in self.entities if not self._is_fossil(e)]
        results = match(query_dna, candidates, top_k=top_k)
        return [r[1] for r in results]

    def _is_fossil(self, entity: Dict) -> bool:
        """Check if entity is a fossil (below energy floor) / 检查是否为化石"""
        return entity.get("energy", 0.5) <= 0.1 and not entity.get("pinned")

    def save(self, path: str):
        """Save to JSON / 保存到 JSON"""
        import json
        data = {
            "entities": self.entities,
            "pinned": list(self.pinned),
            "_version": self._version,
            "fragments": {},
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, path: str) -> "MemoryPool":
        """Load from JSON / 从 JSON 加载"""
        import json
        pool = cls()
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        pool.entities = data.get("entities", [])
        pool.pinned = set(data.get("pinned", []))
        pool._version = data.get("_version", 0)
        return pool

    def __len__(self):
        return len(self.entities)


# Ecosystem role / 生态角色:
#   Central entity storage / 中央实体存储
#   All 8 chips read/write through the pool / 所有 8 芯片通过池读写
#   JSON persistence with version tracking / 带版本追踪的 JSON 持久化
