"""实体池管理——加载/保存 JSON 格式的记忆池。

纯 stdlib 实现，零外部依赖。
"""

import json
import os
from typing import Any, Dict, List, Optional


class MemoryPool:
    """内存实体池。

    实体格式::
        {
            "id": str,
            "text": str,       # 自然语言描述（DNA 从此提取）
            "energy": float,   # 能量值，0.0~1.0
            "source": str,     # 来源标签
            "pinned": bool,    # True=免疫生态淘汰
            "dna": dict,       # 可选，缓存的 DNA 信号
        }
    """

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
        """添加一个新实体。"""
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
        """按 ID 查找实体。"""
        for e in self.entities:
            if e.get("id") == eid:
                return e
        return None

    def remove(self, eid: str) -> bool:
        """删除实体。"""
        before = len(self.entities)
        self.entities = [e for e in self.entities if e.get("id") != eid]
        self.pinned.discard(eid)
        self._version += 1
        return len(self.entities) < before

    def save(self, path: str) -> None:
        """保存到 JSON 文件。"""
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
        """从 JSON 文件加载。"""
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
