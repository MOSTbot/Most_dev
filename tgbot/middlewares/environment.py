from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import Update, Message
from tgbot.utils import all_admins_list


class AdminsMiddleware(BaseMiddleware):

    async def on_pre_process_update(self, update: Update, data: dict):
        # print(all_admins_list())
        return



class EnvironmentMiddleware(LifetimeControllerMiddleware):
    skip_patterns = ["error", "update"]

    def __init__(self, **kwargs):
        super().__init__()
        self.kwargs = kwargs

    async def pre_process(self, obj, data, *args):
        data.update(**self.kwargs)
