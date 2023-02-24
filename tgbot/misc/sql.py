from __future__ import annotations

from functools import lru_cache

import psycopg

from tgbot import load_config
from tgbot.misc import HashData

config = load_config(".env")

db = psycopg.connect(dbname=config.tg_bot.pg_db_name,
                     user=config.tg_bot.pg_user,
                     password=config.tg_bot.pg_pass,
                     host=config.tg_bot.pg_host,
                     port=config.tg_bot.pg_port)
cur = db.cursor()


def _init_db() -> None:
    """Create database"""
    with open('tgbot/db/create_db.sql', 'r') as f:
        sql = f.read()
    cur.execute(sql)
    db.commit()


_init_db()


class SQLDeletions:
    @staticmethod
    def delete_from_table(table: str, column: str, value: str) -> bool:
        cur.execute(f"SELECT * "
                    f"FROM {table} "
                    f"WHERE {column} = %s", (value,))
        if cur.fetchone():
            cur.execute(f"DELETE FROM {table} "
                        f"WHERE {column} = %s", (value,))
            db.commit()
            return True
        return False


class SQLRequests:
    maxsize = 300

    @staticmethod
    @lru_cache(maxsize=maxsize)
    def get_practice_questions() -> list:
        cur.execute('SELECT question_name, pr_id '
                    'FROM practice_questions '
                    'ORDER BY 1')
        return cur.fetchall()

    @staticmethod
    @lru_cache(maxsize=maxsize)
    def select_by_table_and_column(from_: str, select_: str, where_: None | str = None,
                                   is_: None | int | str = None) -> list:
        if is_ is None:
            cur.execute(f"SELECT {select_} "
                        f"FROM {from_}")
            res = cur.fetchall()
        elif where_ is not None:
            cur.execute(f"SELECT {select_} "
                        f"FROM {from_} "
                        f"WHERE {where_} = %s", (is_,))
            res = cur.fetchall()
        else:
            raise ValueError('"from_" and "is_" must be set')
        # TODO: Logging here
        return [row[0] for row in res]

    @staticmethod
    @lru_cache(maxsize=maxsize)
    def select_main_menu_description() -> str:
        cur.execute("SELECT * "
                    "FROM main_menu")
        description = cur.fetchall()
        string = ''
        for i in description:
            string = f'{string}<b>{i[1]}</b>\n{i[2]}\n\n'
        # TODO: Logging here
        return 'Список меню пуст' if string == '' else string

    @staticmethod
    def select_all_admins() -> str:
        cur.execute("SELECT * "
                    "FROM list_of_admins")
        admins_list = cur.fetchall()
        string = ''
        for i in admins_list:
            string = f'{string}Имя: <b>{i[1]}</b>\nХеш ID: <b>{i[2]}</b>\n\n'
        if string == '':
            return 'Список Администраторов пуст'
        else:
            return f'<b>Список Администраторов:</b>\n\n{string}'

    @staticmethod
    def last10_fb() -> str:
        cur.execute("SELECT * "
                    "FROM user_feedback "
                    "ORDER BY feedback_datetime "
                    "DESC LIMIT 10")
        last_10 = cur.fetchall()
        string = ''
        for i in last_10:
            string = f'{string}Последние 10 цифр хеша: <b>{i[1]}</b>\nДата и время: <b>{i[2]}</b>\nОтзыв: <b>{i[3]}</b>\n\n'
        if string == '':
            return 'Список отзывов пока пуст 😶'
        else:
            return f'<b>Последние 10 отзывов:</b>\n\n{string}'

    @staticmethod
    @lru_cache(maxsize=maxsize)
    def get_assertions(assertion_name: None | str = None) -> list:
        cur.execute('SELECT a_assertion_name '
                    'FROM a_assertions '
                    'LEFT JOIN assertions a '
                    'ON a.assertion_id = a_assertions.assertion_id '
                    'WHERE assertion_name = %s '
                    'ORDER BY 1', (assertion_name,))
        assertions = cur.fetchall()
        # TODO: Logging here
        return [assertions[i][0] for i in range(len(assertions))]

    @staticmethod
    @lru_cache(maxsize=maxsize)
    def get_facts(message_text: str) -> list:
        cur.execute('SELECT fact_name '
                    'FROM assertions '
                    'LEFT JOIN facts f '
                    'ON assertions.assertion_id = f.assertion_id '
                    'WHERE assertion_name = %s '
                    'ORDER BY 1', (message_text,))
        return cur.fetchall()

    @staticmethod
    @lru_cache(maxsize=maxsize)
    def get_ad_facts(message_text: str) -> list:
        cur.execute('SELECT a_fact_name '
                    'FROM a_facts '
                    'LEFT JOIN a_assertions aa '
                    'ON aa.a_assertion_id = a_facts.a_assertion_id '
                    'WHERE a_assertion_name = %s '
                    'ORDER BY 1', (message_text,))
        return cur.fetchall()

    @staticmethod
    @lru_cache(maxsize=maxsize)
    def get_practice_answers(p_key: str) -> list:
        cur.execute('SELECT commentary, score, answer_num '
                    'FROM practice_answers '
                    'LEFT JOIN practice_questions pq '
                    'ON pq.pr_id = practice_answers.pr_id '
                    'WHERE pq.pr_id = %s '
                    'ORDER BY 3', (p_key,))
        return cur.fetchall()

    @staticmethod
    def rnd_questions() -> list:
        cur.execute("SELECT * "
                    "FROM (SELECT assertion_name "
                    "FROM assertions "
                    "UNION "
                    "SELECT a_assertion_name "
                    "FROM a_assertions) AS dt "
                    "ORDER BY RANDOM() "
                    "LIMIT 10;")
        random_questions = cur.fetchall()
        return [random_questions[i][0] for i in range(len(random_questions))]

    @staticmethod
    def get_search_index() -> list:
        cur.execute("SELECT assertion_name "
                    "FROM assertions "
                    "UNION "
                    "SELECT a_assertion_name "
                    "FROM a_assertions;")
        res = cur.fetchall()
        return [row[0] for row in res]


class SQLInserts:
    @staticmethod
    async def create_admin(admin_id: str | int, admin_name: None | str = None) -> bool:
        # TODO: Logging here
        hash_admin_id = HashData.hash_data(admin_id)[54:]
        cur.execute('SELECT admin_id FROM list_of_admins ')
        loa = cur.fetchone()
        if loa is None or hash_admin_id not in loa:
            cur.execute('INSERT INTO list_of_admins (admin_name, admin_id) '
                        'VALUES(%s, %s)', (admin_name, hash_admin_id))
            db.commit()
            return True
        return False

    @staticmethod
    def send_feedback(table: str, user_id: str = '', datetime: str = '', feedback: str = '') -> None:
        cur.execute(f'INSERT INTO {table} (user_id, feedback_datetime, user_feedback) '
                    f'VALUES(%s, %s, %s)', (user_id, datetime, feedback))
        db.commit()
