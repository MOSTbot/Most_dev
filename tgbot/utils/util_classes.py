from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

from aiogram import Dispatcher


@dataclass
class MessageText:
    value: Any
    message_text: Any
    generator: Any
    p_answers: Any
    p_key: int
    score: int = 0
    flag: bool = False


@dataclass
class Disp:
    disp: Dispatcher = None


class HashData:
    @staticmethod
    def hash_data(string: str | int) -> str:
        hash_obj = hashlib.sha256(str(string).encode())
        return hash_obj.hexdigest()
