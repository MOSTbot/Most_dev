from __future__ import annotations

from dataclasses import dataclass

from environs import Env


@dataclass
class TgBot:
    token: str
    superuser_id: list[int]
    spreadsheet_id: str
    api_key_path: str
    token_oauth_path: str
    creds_key_path: str
    creds_oauth_path: str

@dataclass
class Config:
    tg_bot: TgBot


def load_config(path: str | None) -> Config:
    env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot(
            token=env.str("BOT_TOKEN"),
            superuser_id=list(map(int, env.list("ADMINS"))),
            spreadsheet_id=env.str("SPREADSHEET_ID"),
            api_key_path=env.str("API_KEY_PATH"),
            token_oauth_path=env.str("TOKEN_OAUTH_PATH"),
            creds_key_path=env.str("CREDS_KEY_PATH"),
            creds_oauth_path=env.str("CREDS_OAUTH_PATH"),
        )
    )
