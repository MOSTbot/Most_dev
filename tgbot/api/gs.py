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
from tgbot.misc import clear_cache_globally, cur, db

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
    async def __get_raw_data(cls, call: CallbackQuery, ranges: list, is_service: bool = True) -> dict:
        try:
            service: Any = cls.__sauth() if is_service else cls.__oauth()
            return service.spreadsheets().values().batchGet(ranges=ranges,
                                                            spreadsheetId=cls.spreadsheet_id,
                                                            valueRenderOption=cls.value_render_option,
                                                            dateTimeRenderOption=cls.date_time_render_option).execute()
        except Exception as e:
            await call.message.answer('Не удалось аутентифицироваться. Данные не были изменены')
            raise ValueError('Не удалось аутентифицироваться. Данные не были изменены') from e

    @staticmethod
    async def __check_if_table_exists(table_name, call: CallbackQuery):
        try:
            cur.execute("SELECT * "
                        "FROM information_schema.tables "
                        f"WHERE table_name = '{table_name}'")
            cur.fetchone()
            return cur.execute(f"TRUNCATE {table_name} RESTART IDENTITY CASCADE;")

        except Exception as e:
            await call.message.answer(f'Таблиц(ы) не существует!\n'
                                      f'Проверьте наличие или название таблицы: <b>{table_name}</b>\n\n'
                                      f'Данные не были изменены')
            raise ValueError(f'Таблицы не существует! Таблица: {table_name}') from e

    @staticmethod
    async def __check_if_column_exists(cols, table_name: str, call: CallbackQuery):
        try:
            cur.execute(f'SELECT {cols} FROM {table_name}')
            return cur.fetchone()
        except Exception as e:
            await call.message.answer(f'Столбца(ов) не существует!\n'
                                      f'Таблица: <b>{table_name}</b>,\n'
                                      f'Проверьте названия столбцов: <b>{cols}</b>\n\n'
                                      f'Данные не были изменены')
            raise ValueError(f'Столбца не существует! Таблица: {table_name}, столбцы: {cols}') from e

    @staticmethod
    async def __check_for_validity(values, table_name, cols, call: CallbackQuery):
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
                vals = "('" + str(*values[i]) + "')"

            # Check if there are empty values in required fields
            try:
                # WARNING: FIX THIS! If a table contains empty values replace them with NULL
                if table_name == 'a_assertions':
                    cur.execute(f"INSERT INTO {table_name} ({cols}) VALUES ('{vals[0]}', NULL)")
                    continue
                cur.execute(f"INSERT INTO {table_name} ({cols}) VALUES {vals}")
            except Exception as e:
                await call.message.answer(
                    'Какие-то из столбцов Google Sheets содержат пустые или недопустимые значения')
                raise ValueError(
                    'Какие-то из столбцов Google Sheets содержат пустые или недопустимые значения') from e

    @staticmethod
    async def __replace_and_trim(values, table_name):
        for col in values[0]:
            cur.execute(f"SELECT column_name "
                        f"FROM information_schema.columns "
                        f"WHERE table_name = '{table_name}' AND data_type = 'text';")
            col_text = cur.fetchall()
            col_text = [value for items in col_text for value in items]
            if col in col_text:
                cur.execute(f"UPDATE {table_name} SET {col} = REPLACE({col},'\\n', chr(10));"
                            f"UPDATE {table_name} SET {col} = trim({col});")

    @staticmethod
    async def get_data(ran: str, shts: list, call: CallbackQuery) -> None:  # sourcery skip: de-morgan

        sheets_and_ranges_list: list = [f'{_}!{ran}' for _ in shts]

        data_from_gs: dict = await GoogleSheetsAPI.__get_raw_data(call=call, ranges=sheets_and_ranges_list)

        for tables in range(len(sheets_and_ranges_list)):
            num_of_rows: int = len(data_from_gs['valueRanges'][tables]['values'])
            table_name: str = sheets_and_ranges_list[tables][:sheets_and_ranges_list[tables].find('!')]

            # Checking if the table exists. If exists, clear
            await GoogleSheetsAPI.__check_if_table_exists(table_name, call)

            values: list = [data_from_gs['valueRanges'][tables]['values'][_] for _ in range(num_of_rows)]

            cols: str = ', '.join(values[0])  # Getting column names

            # Checking if all columns exist
            await GoogleSheetsAPI.__check_if_column_exists(cols, table_name, call)

            await GoogleSheetsAPI.__check_for_validity(values, table_name, cols, call)

            # Replacing \n with line feed (otherwise, the newline character is transferred as text)
            await GoogleSheetsAPI.__replace_and_trim(values, table_name)
        db.commit()
        await clear_cache_globally()
        await call.message.answer('Данные успешно обновлены! 🥳')
