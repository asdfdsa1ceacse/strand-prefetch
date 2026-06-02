"""Memory Pool Manager / 实体池管理

Minimal entity pool for loading/saving JSON-format memory pools.
Zero external dependencies — pure Python stdlib.
Designed for the standalone strand-prefetch package.

最小化实体池，用于加载/保存 JSON 格式的记忆池。
零外部依赖——纯 Python stdlib。
为独立版 strand-prefetch 包设计。

Entity format / 实体格式::
    {
        "id": str,           # Unique identifier / 唯一标识
        "text": str,         # Natural language description (DNA extracted from this)
        "energy": float,     # Energy value 0.0~1.0 / 能量值
        "source": str,       # Source tag / 来源标签
        "pinned": bool,      # Immune to ecosystem culling / 免疫生态淘汰
        "dna": dict,         # Optional cached DNA signal / 可选缓存的 DNA 信号
    }
"""

import json
import os
from typing import Any, Dict, List, Optional


class MemoryPool:
    """In-memory entity pool / 内存实体池"""

    def __init__(self) -> None:
        self.entities: list[dict] = []
        self.pinned: set[str] = set()
        self._version: int = 0

    def add(
        self,
        eid: str,
        text: str,
        source: str = "hermes",
        energy: float = 0.5,
        pinned: bool = False,
    ) -> dict:
        """Add a new entity / 添加新实体"""
        ent = {
            "id": eid,
            "text": text,
            "energy": energy,
            "source": source,
            "pinned": pinned,
            "dna": {},
        }
        self.entities.append(ent)
        if pinned:
            self.pinned.add(eid)
        self._version += 1
        return ent

    def get(self, eid: str) -> Optional[dict]:
        """Find entity by ID / 按 ID 查找"""
        for e in self.entities:
            if e.get("id") == eid:
                return e
        return None

    def remove(self, eid: str) -> bool:
        """Remove entity by ID / 按 ID 删除"""
        before = len(self.entities)
        self.entities = [e for e in self.entities if e.get("id") != eid]
        self.pinned.discard(eid)
        self._version += 1
        return len(self.entities) < before

    def save(self, path: str) -> None:
        """Save to JSON file / 保存到 JSON 文件"""
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
        """Load from JSON file / 从 JSON 文件加载"""
        pool = cls()
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        pool.entities = data.get("entities", [])
        pool.pinned = set(data.get("pinned", []))
        pool._version = data.get("_version", 0)
        return pool

    def __len__(self) -> int:
        return len(self.entities)

    def __repr__(self) -> str:
        return f"<MemoryPool {len(self.entities)} entities, {len(self.pinned)} pinned>"
