from dataclasses import dataclass
from environs import Env

from tgbot.utils import all_admins_list


@dataclass
class TgBot:
    token: str
    superuser_id: list[int]


@dataclass
class Config:
    tg_bot: TgBot


def load_config(path: str = None):
    env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot(
            token=env.str("BOT_TOKEN"),
            superuser_id=list(map(int, env.list("ADMINS"))),
            # superuser_id=list(map(int, ['admins_from_sql'])) #WARNING: Temporary!
        )
    )
