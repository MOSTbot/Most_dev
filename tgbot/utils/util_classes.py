from __future__ import annotations

import gc
import hashlib
from dataclasses import dataclass
from functools import _lru_cache_wrapper

from aiogram import Dispatcher


@dataclass
class SectionName:
    s_name: str | None = None


@dataclass
class Disp:
    disp: Dispatcher = None


class HashData:
    @staticmethod
    def hash_data(string: str | int) -> str:
        hash_obj = hashlib.sha256(str(string).encode())
        return hash_obj.hexdigest()


async def clear_cache_globally() -> None:
    gc.collect()
    objects = [i for i in gc.get_objects()
               if isinstance(i, _lru_cache_wrapper)]
    for obj in objects:
        obj.cache_clear()
