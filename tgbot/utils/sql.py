from __future__ import annotations

import sqlite3 as sq
from typing import Generator

from tgbot.utils import HashData

db = sq.connect('bot.db')
cur = db.cursor()

cur.executescript("""
    CREATE TABLE IF NOT EXISTS list_of_admins
    (a_id             INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    admin_name        TEXT    NOT NULL,
    admin_id          TEXT    NOT NULL);

    CREATE TABLE IF NOT EXISTS user_feedback
    (fb_id            INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    user_id           TEXT    NOT NULL,
    feedback_datetime TEXT    NOT NULL,
    user_feedback     TEXT    NOT NULL);
    
    CREATE TABLE IF NOT EXISTS assertions
    (assertion_id     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    assertion_name    TEXT    NOT NULL);
    
    CREATE TABLE IF NOT EXISTS facts
    (fact_id          INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    fact_name         TEXT    NOT NULL,
    ext_source        TEXT    NOT NULL,
    assertion_id      INTEGER NOT NULL,
    FOREIGN KEY (assertion_id) REFERENCES assertions (assertion_id));
    
    CREATE TABLE IF NOT EXISTS practice_questions
    (pr_id            INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    question_name       TEXT  NOT NULL);
    
    CREATE TABLE IF NOT EXISTS practice_answers
    (answer_id        INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    answer_num        TEXT    NOT NULL,
    commentary        TEXT    NOT NULL,
    quality           INTEGER NOT NULL,
    pr_id             INTEGER NOT NULL,
    FOREIGN KEY (pr_id) REFERENCES practice_questions (pr_id));
    
    CREATE TABLE IF NOT EXISTS adv_assertions
    (adv_id           INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    adv_assertion     TEXT    NOT NULL,
    adv_description   TEXT    NOT NULL);
    
    CREATE TABLE IF NOT EXISTS adv_answers
    (adv_ans_id       INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    adv_answers       TEXT    NOT NULL,
    adv_description   TEXT    NOT NULL,
    adv_id            INTEGER NOT NULL,
    FOREIGN KEY (adv_id) REFERENCES adv_assertions (adv_id));
    
    CREATE TABLE IF NOT EXISTS main_menu
    (mm_id            INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    main_menu_name    TEXT    NOT NULL,
    description       TEXT);
    
    CREATE TABLE IF NOT EXISTS a_assertions
    (a_assertion_id   INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    a_assertion_name  TEXT    NOT NULL,
    assertion_id      INTEGER NOT NULL,
    FOREIGN KEY (assertion_id) REFERENCES assertions (assertion_id));
    
    CREATE TABLE IF NOT EXISTS a_facts
    (a_fact_id        INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    a_fact_name       TEXT    NOT NULL,
    a_ext_source      TEXT    NOT NULL,
    a_assertion_id    INTEGER NOT NULL,
    FOREIGN KEY (a_assertion_id) REFERENCES a_assertions (a_assertion_id));""")


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
            raise ValueError('col_value_is_taken_from and value must be set')
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
    def get_facts(message_text: None | str) -> Generator[None | str, None, None]:
        facts = cur.execute('SELECT fact_name '
                            'FROM assertions '
                            'LEFT JOIN facts f '
                            'ON assertions.assertion_id = f.assertion_id '
                            'WHERE assertion_name IS ?', (message_text,)).fetchall()

        for i in range(len(facts)):
            yield facts[i][0]

    @staticmethod
    def get_a_facts(message_text: str) -> Generator[None | str, None, None]:
        facts = cur.execute('SELECT a_fact_name '
                            'FROM a_facts '
                            'LEFT JOIN a_assertions aa '
                            'ON aa.a_assertion_id = a_facts.a_assertion_id '
                            'WHERE a_assertion_name IS ?', (message_text,)).fetchall()

        for i in range(len(facts)):
            yield facts[i][0]

    @staticmethod
    def get_assertions(assertion_name: None | str = None) -> list:
        assertions = cur.execute('SELECT a_assertion_name '
                                 'FROM a_assertions '
                                 'LEFT JOIN assertions a '
                                 'ON a.assertion_id = a_assertions.assertion_id '
                                 'WHERE assertion_name IS ?', (assertion_name,)).fetchall()

        return [assertions[i][0] for i in range(len(assertions))]

    @staticmethod
    def get_practice_questions() -> Generator[None | tuple, None, None]:
        practice_questions = cur.execute("SELECT question_name, pr_id "
                                         "FROM practice_questions").fetchall()
        for i in range(len(practice_questions)):
            yield practice_questions[i][0], practice_questions[i][1]

    @staticmethod
    def get_practice_answers(p_key: str) -> list:
        return cur.execute('SELECT commentary, quality '
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
        hash_user_id = HashData.hash_data(user_id)[54:]
        cur.execute('INSERT INTO user_feedback (user_id, feedback_datetime, user_feedback) '
                    'VALUES(?, ?, ?)', (hash_user_id, datetime, feedback))
        db.commit()
