import typing
from aiogram.dispatcher.filters import BoundFilter
from tgbot.config import Config


class SUFilter(BoundFilter):
    key = 'is_su'

    def __init__(self, is_su: typing.Optional[bool] = None):
        self.is_su = is_su

    async def check(self, obj):
        if self.is_su is not None:
            config: Config = obj.bot.get('config')
            return (obj.from_user.id in config.tg_bot.superuser_id) == self.is_su
        return False
