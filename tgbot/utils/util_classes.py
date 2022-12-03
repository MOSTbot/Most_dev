from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Iterator


@dataclass
class MessageText:
    message_text: str | Iterator[str] = None


class HashData:
    @staticmethod
    def hash_data(string: (str, int)) -> str:
        hash_obj = hashlib.sha256(str(string).encode())
        return hash_obj.hexdigest()
