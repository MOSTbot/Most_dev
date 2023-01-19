from __future__ import annotations

import sqlite3 as sq
from functools import lru_cache
from typing import Any

from tgbot.utils import HashData

db = sq.connect('tgbot/db/bot.db')
cur = db.cursor()


def _init_db() -> None:
    """Create database"""
    with open('tgbot/db/create_db.sql', 'r') as f:
        sql = f.read()
    cur.executescript(sql)
    db.commit()


_init_db()


class SQLDeletions:
    @staticmethod
    async def delete_from_table(table: str, column: str, value: str) -> bool:
        if cur.execute(f"SELECT * "
                       f"FROM {table} "
                       f"WHERE {column} IS ?", (value,)).fetchone():
            cur.execute(f"DELETE FROM {table} "
                        f"WHERE {column} IS ?", (value,))
            db.commit()
            return True
        return False


class SQLRequests:
    @staticmethod
    @lru_cache
    def select_by_table_and_column(from_: str, select_: str, where_: None | str = None,
                                   is_: None | int | str = None) -> list:
        if is_ is None:
            res = cur.execute(f"SELECT {select_} "
                              f"FROM {from_}").fetchall()
        elif where_ is not None:
            res = cur.execute(f"SELECT {select_} "
                              f"FROM {from_} "
                              f"WHERE {where_} IS ?", (is_,)).fetchall()
        else:
            raise ValueError('"from_" and "is_" must be set')
        # TODO: Logging here
        return [row[0] for row in res]

    @staticmethod
    @lru_cache
    def select_main_menu_description() -> str:
        description = cur.execute("SELECT * "
                                  "FROM main_menu").fetchall()
        string = ''
        for i in description:
            string = f'{string}<b>{i[1]}</b>\n{i[2]}\n\n'
        # TODO: Logging here
        return 'Список меню пуст' if string == '' else string

    @staticmethod
    def select_all_admins() -> str:
        admins_list = cur.execute("SELECT * "
                                  "FROM list_of_admins").fetchall()
        string = ''
        for i in admins_list:
            string = f'{string}Имя: <b>{i[1]}</b>\nХеш ID: <b>{i[2]}</b>\n\n'
        if string == '':
            return 'Список Администраторов пуст'
        else:
            return f'<b>Список Администраторов:</b>\n\n{string}'

    @staticmethod
    def last10_fb() -> str:
        last_10 = cur.execute("SELECT * "
                              "FROM user_feedback "
                              "ORDER BY feedback_datetime "
                              "DESC LIMIT 10").fetchall()
        string = ''
        for i in last_10:
            string = f'{string}Последние 10 цифр хеша: <b>{i[1]}</b>\nДата и время: <b>{i[2]}</b>\nОтзыв: <b>{i[3]}</b>\n\n'
        if string == '':
            return 'Список отзывов пока пуст 😶'
        else:
            return f'<b>Последние 10 отзывов:</b>\n\n{string}'

    @staticmethod
    @lru_cache
    def get_assertions(assertion_name: None | str = None) -> list:
        assertions = cur.execute('SELECT a_assertion_name '
                                 'FROM a_assertions '
                                 'LEFT JOIN assertions a '
                                 'ON a.assertion_id = a_assertions.assertion_id '
                                 'WHERE assertion_name IS ?', (assertion_name,)).fetchall()
        # TODO: Logging here
        return [assertions[i][0] for i in range(len(assertions))]

    # WARNING: Needs caching!
    @staticmethod
    def get_practice_answers(p_key: str) -> list:
        return cur.execute('SELECT commentary, score '
                           'FROM practice_answers '
                           'LEFT JOIN practice_questions pq '
                           'ON pq.pr_id = practice_answers.pr_id '
                           'WHERE pq.pr_id IS ?', (p_key,)).fetchall()

    # WARNING: Needs caching!
    @staticmethod
    def rnd_questions() -> list:
        random_questions = cur.execute("SELECT * "
                                       "FROM (SELECT assertion_name "
                                       "FROM assertions "
                                       "UNION "
                                       "SELECT a_assertion_name "
                                       "FROM a_assertions) "
                                       "ORDER BY RANDOM() "
                                       "LIMIT 6;").fetchall()
        return [random_questions[i][0] for i in range(len(random_questions))]


class SQLInserts:
    @staticmethod
    async def create_admin(admin_id: str | int, admin_name: None | str = None) -> bool:
        # TODO: Logging here
        hash_admin_id = HashData.hash_data(admin_id)[54:]
        loa = cur.execute('SELECT admin_id FROM list_of_admins ').fetchone()
        if loa is None or hash_admin_id not in loa:
            cur.execute('INSERT INTO list_of_admins (admin_name, admin_id) '
                        'VALUES(?, ?)', (admin_name, hash_admin_id))
            db.commit()
            return True
        return False

    @staticmethod
    def send_feedback(table: str, user_id: str = '', datetime: str = '', feedback: str = '') -> None:
        cur.execute(f'INSERT INTO {table} (user_id, feedback_datetime, user_feedback) '
                    f'VALUES(?, ?, ?)', (user_id, datetime, feedback))
        db.commit()


# WARNING: Needs caching!
class GetFacts:
    def __init__(self, message_text: str) -> None:
        self.message_text = message_text
        self.iteration_num = 0

    def __iter__(self) -> GetFacts:
        return self

    def __next__(self) -> Any:
        facts = cur.execute('SELECT fact_name '
                            'FROM assertions '
                            'LEFT JOIN facts f '
                            'ON assertions.assertion_id = f.assertion_id '
                            'WHERE assertion_name IS ?', (self.message_text,)).fetchall()
        if self.iteration_num < len(facts):
            res = facts[self.iteration_num][0]
            self.iteration_num += 1
            return res
        raise StopIteration


# WARNING: Needs caching!
class GetAdFacts:
    def __init__(self, message_text: str) -> None:
        self.message_text = message_text
        self.iteration_num = 0

    def __iter__(self) -> GetAdFacts:
        return self

    def __next__(self) -> Any:
        facts = cur.execute('SELECT a_fact_name '
                            'FROM a_facts '
                            'LEFT JOIN a_assertions aa '
                            'ON aa.a_assertion_id = a_facts.a_assertion_id '
                            'WHERE a_assertion_name IS ?', (self.message_text,)).fetchall()
        if self.iteration_num < len(facts):
            res = facts[self.iteration_num][0]
            self.iteration_num += 1
            return res
        raise StopIteration


# WARNING: Needs caching!
class GetPracticeQuestions:
    def __init__(self) -> None:
        self.iteration_num = 0

    def __iter__(self) -> GetPracticeQuestions:
        return self

    def __next__(self) -> tuple:
        practice_questions = cur.execute("SELECT question_name, pr_id "
                                         "FROM practice_questions").fetchall()
        if self.iteration_num < len(practice_questions):
            res = practice_questions[self.iteration_num][0], practice_questions[self.iteration_num][1]
            self.iteration_num += 1
            return res
        raise StopIteration
