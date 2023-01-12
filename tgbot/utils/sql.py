from __future__ import annotations

import sqlite3 as sq
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
    def select_by_table_and_column(from_: str, select_: str, where_: None | str = None,
                                   is_: None | int = None) -> list:
        if is_ is None:
            res = cur.execute(f"SELECT {select_} "
                              f"FROM {from_}").fetchall()
        elif where_ is not None:
            res = cur.execute(f"SELECT {select_} "
                              f"FROM {from_} "
                              f"WHERE {where_} IS ?", (is_,)).fetchall()
        else:
            raise ValueError('"from_" and "is_" must be set')
        return [row[0] for row in res]

    @staticmethod
    def select_main_menu_description() -> str:
        description = cur.execute("SELECT * "
                                  "FROM main_menu").fetchall()
        string = ''
        for i in description:
            string = f'{string}<b>{i[1]}</b>\n{i[2]}\n\n'
        return 'Список меню пуст' if string == '' else string

    @staticmethod
    def check_if_item_exists(table: str, column: str, value: str) -> bool:
        res = cur.execute(f"SELECT {column} "
                          f"FROM {table} "
                          f"WHERE {column} IS ?", (value,)).fetchone()
        return res is not None and res[0] == value

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
    def all_admins_list() -> list:
        list_of_admins = cur.execute("SELECT admin_id "
                                     "FROM list_of_admins").fetchall()
        return [list_of_admins[i][0] for i, item in enumerate(list_of_admins)]

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
    def get_assertions(assertion_name: None | str = None) -> list:
        assertions = cur.execute('SELECT a_assertion_name '
                                 'FROM a_assertions '
                                 'LEFT JOIN assertions a '
                                 'ON a.assertion_id = a_assertions.assertion_id '
                                 'WHERE assertion_name IS ?', (assertion_name,)).fetchall()

        return [assertions[i][0] for i in range(len(assertions))]

    @staticmethod
    def get_practice_answers(p_key: str) -> list:
        return cur.execute('SELECT commentary, score '
                           'FROM practice_answers '
                           'LEFT JOIN practice_questions pq '
                           'ON pq.pr_id = practice_answers.pr_id '
                           'WHERE pq.pr_id IS ?', (p_key,)).fetchall()

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
    async def add_to_table(table: str, column: str, value: str) -> None:
        cur.execute(f"INSERT INTO {table} ({column}) "
                    f"VALUES(?)", (value,))
        db.commit()

    @staticmethod
    async def add_to_child_table(parent_table: str, parent_table_pk_column: str, parent_table_column: str,
                                 parent_table_value: str,
                                 child_table: str, child_table_column: str, child_table_value: str) -> None:
        cur.execute(
            f"INSERT INTO {child_table} ({child_table_column}, {parent_table_pk_column})"
            f" VALUES (?, ?)",
            (child_table_value, cur.execute(f"SELECT {parent_table_pk_column}"
                                            f" FROM {parent_table}"
                                            f" WHERE {parent_table_column} IS ?", (parent_table_value,)).fetchone()[0]))
        db.commit()

    @staticmethod
    async def create_admin(admin_id: str | int, admin_name: None | str = None) -> bool:
        hash_admin_id = HashData.hash_data(admin_id)[54:]
        if SQLRequests.check_if_item_exists(table='list_of_admins', column='admin_id', value=hash_admin_id):
            return False
        cur.execute('INSERT INTO list_of_admins (admin_name, admin_id) '
                    'VALUES(?, ?)', (admin_name, hash_admin_id))
        db.commit()
        return True

    @staticmethod
    def send_feedback(user_id: str = '', datetime: str = '', feedback: str = '') -> None:
        cur.execute('INSERT INTO user_feedback (user_id, feedback_datetime, user_feedback) '
                    'VALUES(?, ?, ?)', (user_id, datetime, feedback))
        db.commit()


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
