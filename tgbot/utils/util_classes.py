from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

from aiogram import Dispatcher


@dataclass
class MessageText:
    p_key: int
    value: Any = None
    message_text: Any = None
    p_answers: Any = None
    c_generator: Any = None # /chat generator
    p_generator: Any = None # /practice generator
    score: int = 0
    flag: bool = False


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
