from __future__ import annotations
from typing import Any

import pickle
import os

from aiogram.types import CallbackQuery
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

from googleapiclient import discovery

from tgbot import load_config
from tgbot.utils import clear_cache_globally

config = load_config(".env")


class GoogleSheetsAPI:
    spreadsheet_id = config.tg_bot.spreadsheet_id
    value_render_option = 'UNFORMATTED_VALUE'
    date_time_render_option = 'FORMATTED_STRING'
    scope = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    api_key_path = config.tg_bot.api_key_path
    token_oauth_path = config.tg_bot.token_oauth_path
    creds_key_path = config.tg_bot.creds_key_path
    creds_oauth_path = config.tg_bot.creds_oauth_path

    # Under normal circumstances, the method below should never be used
    @classmethod
    def __oauth(cls) -> Any | None:
        creds = None

        if os.path.exists(cls.token_oauth_path):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    cls.creds_oauth_path, cls.scope)
                creds = flow.run_local_server(port=0)

            # Pickle the credentials for the next run
            with open(cls.token_oauth_path, 'wb') as token:
                pickle.dump(creds, token)
        return discovery.build('sheets', 'v4', credentials=creds)

    @classmethod
    def __sauth(cls) -> Any | None:

        if os.path.exists(cls.api_key_path):
            with open('key.pickle', 'rb') as token:
                creds = pickle.load(token)
        else:
            creds = service_account.Credentials.from_service_account_file(
                cls.creds_key_path, scopes=cls.scope)
            with open(cls.api_key_path, 'wb') as token:
                pickle.dump(creds, token)

        return discovery.build('sheets', 'v4', credentials=creds)

    @classmethod
    def get_sheet_ranges(cls, ranges: list, is_service: bool = True) -> dict:
        service: Any = cls.__sauth() if is_service else cls.__oauth()
        return service.spreadsheets().values().batchGet(ranges=ranges,
                                                        spreadsheetId=cls.spreadsheet_id,
                                                        valueRenderOption=cls.value_render_option,
                                                        dateTimeRenderOption=cls.date_time_render_option).execute()

    # noinspection SqlWithoutWhere
    @staticmethod
    async def get_data(ran: str, shts: list, call: CallbackQuery) -> None:  # sourcery skip: de-morgan
        from tgbot.utils import cur

        range_ = [f'{_}!{ran}' for _ in shts]

        # Checking tokens and authenticating
        try:
            res = GoogleSheetsAPI.get_sheet_ranges(range_)
        except Exception as e:
            await call.message.answer('Не удалось аутентифицироваться. Данные не были изменены')
            raise ValueError('Не удалось аутентифицироваться. Данные не были изменены') from e

        for tables in range(len(range_)):
            num_of_rows = len(res['valueRanges'][tables]['values'])
            table_name = range_[tables][:range_[tables].find('!')]

            # Checking if the table exists. If exists, clear
            try:
                cur.execute(f"""SELECT name 
                                FROM sqlite_master 
                                WHERE type='table' AND name='{table_name}';""").fetchone()
                cur.executescript(f"""DELETE FROM {table_name};
                                      DELETE FROM sqlite_sequence WHERE name = '{table_name}';""")

            except Exception as e:
                await call.message.answer(f'Таблиц(ы) не существует!\n'
                                          f'Проверьте наличие или название таблицы: <b>{table_name}</b>\n\n'
                                          f'Данные не были изменены')
                raise ValueError(f'Таблицы не существует! Таблица: {table_name}') from e

            values = [res['valueRanges'][tables]['values'][_] for _ in range(num_of_rows)]

            cols = ', '.join(values[0])  # Getting column names

            # Checking if all columns exist
            try:
                cur.execute(f'SELECT {cols} FROM {table_name}').fetchone()
            except Exception as e:
                await call.message.answer(f'Столбца(ов) не существует!\n'
                                          f'Таблица: <b>{table_name}</b>,\n'
                                          f'Проверьте названия столбцов: <b>{cols}</b>\n\n'
                                          f'Данные не были изменены')
                raise ValueError(f'Столбца не существует! Таблица: {table_name}, столбцы: {cols}') from e

            for i in range(1, len(values)):

                # If the database has more than one column, convert to tuple
                if not len(values[0]) == 1 and len(values[0]) == len(values[i]):
                    vals: tuple | str = tuple(values[i])

                # If the number of columns in the database is greater than comes from API,
                # fill in the missing columns with empty values
                elif len(values[0]) > len(values[i]):
                    vals = tuple(values[i]) + ('',) * (len(values[0]) - 1)

                # If the table has only one column
                else:
                    vals = '("' + str(*values[i]) + '")'

                # Check if there are empty values in required fields
                try:
                    cur.execute(f"INSERT INTO {table_name} ({cols}) VALUES {vals}")
                except Exception as e:
                    await call.message.answer(
                        'Какие-то из столбцов Google Sheets содержат пустые или недопустимые значения')
                    raise ValueError(
                        'Какие-то из столбцов Google Sheets содержат пустые или недопустимые значения') from e

            # Replacing \n with line feed (otherwise, the newline character is transferred as text)
            for i in values[0]:
                # noinspection SqlSignature
                cur.executescript(f"UPDATE {table_name} SET {i} = replace({i},'\\n', char(10));"
                                  f"UPDATE {table_name} SET {i} = trim({i});")
        from tgbot.utils import db
        db.commit()
        await clear_cache_globally()
        await call.message.answer('Данные успешно обновлены! 🥳')
