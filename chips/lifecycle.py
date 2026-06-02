"""Strand Lifecycle / 生命周期芯片

Per-species Ebbinghaus half-life decay + fossil revival.
按物种配置差异化艾宾浩斯半衰期衰减 + 化石复活。

Original: strand-lifecycle (pip package)
"""

import math
import time
from typing import Dict, List, Optional


# Default half-life per species / 默认按物种的半衰期（秒）
SPECIES_HALF_LIFE: Dict[str, float] = {
    "hermes": 86400 * 7,       # 7 days for user memories / 用户记忆 7 天
    "hindsight": 86400 * 30,   # 30 days for archived / 归档 30 天
    "dna_memory": 86400 * 365, # 1 year for seed / 种子 1 年
    "hub_3d": 86400 * 365 * 10,# 10 years for spatial / 空间节点 10 年
}


def decay(entity: Dict, now: float = None) -> Dict:
    """Apply Ebbinghaus half-life decay / 应用艾宾浩斯半衰期衰减

    E = E0 * 2^(-t / T)
    where T is the species half-life, t is time since last update.
    Energy never drops below 0.1 (fossil floor).
    能量永不降到 0.1（化石地板）以下。
    """
    if now is None:
        now = time.time()
    if entity.get("pinned"):
        return entity  # Pinned entities are immortal / 锁定实体不衰减

    species = entity.get("source", "hermes")
    half_life = SPECIES_HALF_LIFE.get(species, 86400 * 7)
    last_update = entity.get("_last_update", now)
    elapsed = now - last_update

    e0 = entity.get("energy", 0.5)
    decayed = e0 * math.pow(2, -elapsed / half_life)
    entity["energy"] = max(0.1, min(1.0, decayed))  # Clamp [0.1, 1.0]
    entity["_last_update"] = now
    return entity


def fossilize(entity: Dict) -> bool:
    """Check if entity has become a fossil (energy at floor) / 检查是否变为化石"""
    return entity.get("energy", 0.5) <= 0.11


def revive(fossil: Dict, boost: float = 0.5) -> Dict:
    """Revive a fossil entity with energy boost / 用能量提升复活化石实体"""
    fossil["energy"] = boost
    fossil["_last_update"] = time.time()
    return fossil


# Ecosystem role / 生态角色:
#   Prevents stale entities from consuming pool space / 防止僵尸实体占用池空间
#   Ebbinghaus curve models human forgetting / 艾宾浩斯曲线模拟人脑遗忘
#   Fossils can be revived on match / 化石可在命中时复活
