from __future__ import annotations

from typing import Any

from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import Message

from tgbot.misc import cur, HashData

from tgbot.config import Config


class SUFilter(BoundFilter):
    key = 'is_su'

    def __init__(self, is_su: bool | None) -> None:
        self.is_su = is_su

    async def check(self, obj: Any) -> bool:
        if self.is_su is not None:
            config: Config = obj.bot.get('config')
            return (obj.from_user.id in config.tg_bot.superuser_id) == self.is_su
        return False


class AdFilter(BoundFilter):
    key = 'is_admin'

    def __init__(self, is_admin: bool | None) -> None:
        self.is_admin = is_admin

    async def check(self, message: Message) -> bool:
        if self.is_admin is not None:
            hash_admin_id = HashData.hash_data(message.from_user.id)[54:]
            cur.execute("SELECT admin_id FROM list_of_admins")
            admins_list = cur.fetchall()
            return (hash_admin_id in [i[0] for i in admins_list]) == self.is_admin
        return False
