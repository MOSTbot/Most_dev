from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Iterator


@dataclass
class MessageText:
    message_text: str = None
    generator: Iterator[str] = None
    value: tuple = None
    p_answers: list = None
    p_key: str = None
    flag: bool = False
    score: int = 0


class HashData:
    @staticmethod
    def hash_data(string: str | int) -> str:
        hash_obj = hashlib.sha256(str(string).encode())
        return hash_obj.hexdigest()
