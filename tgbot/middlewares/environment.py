from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import Update


class AdminsMiddleware(BaseMiddleware):

    async def on_pre_process_update(self, update: Update, data: dict) -> None:
        # print(SQLRequests.all_admins_list())
        return