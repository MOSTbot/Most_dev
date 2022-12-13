import sqlite3 as sq
from typing import Iterator

from tgbot.utils.util_classes import HashData

db = sq.connect('bot.db')
cur = db.cursor()

# WARNING: Use cur.executescript!
cur.execute("""CREATE TABLE IF NOT EXISTS list_of_admins
     (a_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
      admin_name TEXT NOT NULL,
       admin_id TEXT NOT NULL)""")

cur.execute("""CREATE TABLE IF NOT EXISTS user_feedback
(fb_id            INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
user_id           TEXT    NOT NULL,
feedback_datetime TEXT    NOT NULL,
user_feedback     TEXT    NOT NULL)""")

cur.execute("""CREATE TABLE IF NOT EXISTS assertions
(assertion_id     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
assertion_name    TEXT    NOT NULL);""")

cur.execute("""CREATE TABLE IF NOT EXISTS facts
(fact_id          INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
fact_name         TEXT    NOT NULL,
ext_source        TEXT    NOT NULL,
assertion_id      INTEGER NOT NULL,
FOREIGN KEY (assertion_id) REFERENCES assertions (assertion_id));""")

cur.execute("""CREATE TABLE IF NOT EXISTS practice_questions
(pr_id            INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
question_name       TEXT  NOT NULL);""")

cur.execute("""CREATE TABLE IF NOT EXISTS practice_answers
(answer_id        INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
answer_num        TEXT    NOT NULL,
commentary        TEXT    NOT NULL,
quality           INTEGER NOT NULL,
pr_id             INTEGER NOT NULL,
FOREIGN KEY (pr_id) REFERENCES practice_questions (pr_id));""")

cur.execute("""CREATE TABLE IF NOT EXISTS advice
(topic_id         INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
topic_name        TEXT    NOT NULL,
topic_description TEXT    NOT NULL);""")

cur.execute("""CREATE TABLE IF NOT EXISTS main_menu
(mm_id            INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
main_menu_name      TEXT  NOT NULL,
description         TEXT);""")

cur.execute("""CREATE TABLE IF NOT EXISTS a_assertions
(a_assertion_id   INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
a_assertion_name  TEXT    NOT NULL,
assertion_id      INTEGER NOT NULL,
FOREIGN KEY (assertion_id) REFERENCES assertions (assertion_id));""")

cur.execute("""CREATE TABLE IF NOT EXISTS a_facts
(a_fact_id        INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
a_fact_name       TEXT    NOT NULL,
a_ext_source      TEXT    NOT NULL,
a_assertion_id    INTEGER NOT NULL,
FOREIGN KEY (a_assertion_id) REFERENCES a_assertions (a_assertion_id));""")


def select_by_table_and_column(table: str, column: str, col_value_is_taken_from: str = None, value: int = None) -> list:
    if value is None:
        res = cur.execute(f"SELECT {column} FROM {table}").fetchall()
    elif col_value_is_taken_from is not None:
        res = cur.execute(f"SELECT {column} FROM {table} WHERE {col_value_is_taken_from} IS '{value}'").fetchall()
    else:
        raise ValueError('col_value_is_taken_from and value must be set')
    return [row[0] for row in res]


def select_main_menu_description() -> str:
    description = cur.execute("SELECT * FROM main_menu").fetchall()
    string = ''
    for i in description:
        string = f'{string}<b>{i[1]}</b>\n{i[2]}\n\n'
    return 'Список меню пуст' if string == '' else string


def check_if_item_exists(table: str, column: str, value: str) -> bool:
    res = cur.execute(f"SELECT {column} FROM {table} WHERE {column} IS '{value}'").fetchone()
    return res is not None and res[0] == value


async def add_to_table(table: str, column: str, value: str) -> None:
    cur.execute(f"INSERT INTO {table} ({column}) VALUES(?)", (value,))
    db.commit()


async def add_to_child_table(parent_table: str, parent_table_pk_column: str, parent_table_column: str,
                             parent_table_value: str,
                             child_table: str, child_table_column: str, child_table_value: str) -> None:
    cur.execute(
        f"INSERT INTO {child_table} ({child_table_column}, {parent_table_pk_column})"
        f" VALUES (?, ?)",
        (child_table_value, cur.execute(f"SELECT {parent_table_pk_column}"
                                        f" FROM {parent_table}"
                                        f" WHERE {parent_table_column} IS '{parent_table_value}'").fetchone()[0]))
    db.commit()


async def create_admin(admin_id=None, admin_name=None) -> bool:
    hash_admin_id = HashData.hash_data(admin_id)
    if check_if_item_exists(table='list_of_admins', column='admin_id', value=hash_admin_id):
        return False
    cur.execute('INSERT INTO list_of_admins (admin_name, admin_id) VALUES(?, ?)', (admin_name, hash_admin_id))
    db.commit()
    return True


async def delete_from_table(table: str, column: str, value: str) -> bool:
    if cur.execute(f"SELECT * FROM {table} WHERE {column} IS '{value}'").fetchone():
        cur.execute(f"DELETE FROM {table} WHERE {column} IS '{value}'")
        db.commit()
        return True
    return False


def select_all_admins() -> str:
    admins_list = cur.execute("SELECT * FROM list_of_admins").fetchall()
    string = ''
    for i in admins_list:
        string = f'{string}Имя: <b>{i[1]}</b>\nХеш ID: <b>{i[2]}</b>\n\n'
    if string == '':
        return 'Список Администраторов пуст'
    else:
        return f'<b>Список Администраторов:</b>\n\n{string}'


def all_admins_list() -> list:
    list_of_admins = cur.execute("SELECT admin_id FROM list_of_admins").fetchall()
    list_of_admins = [list_of_admins[i][0] for i, item in enumerate(list_of_admins)]
    return list_of_admins


def send_feedback(user_id: str = None, datetime: str = None, feedback: str = None) -> None:
    hash_user_id = HashData.hash_data(user_id)
    cur.execute('INSERT INTO user_feedback (user_id, feedback_datetime, user_feedback) '
                'VALUES(?, ?, ?)', (hash_user_id, datetime, feedback))

    db.commit()


def last10_fb() -> str:
    last_10 = cur.execute("SELECT * FROM user_feedback ORDER BY feedback_datetime DESC LIMIT 10").fetchall()
    string = ''
    for i in last_10:
        string = f'{string}Последние 5 цифр хеша: <b>{i[1][59:]}</b>\nДата и время: <b>{i[2]}</b>\nОтзыв: <b>{i[3]}</b>\n\n'
    if string == '':
        return 'Список отзывов пока пуст 😶'
    else:
        return f'<b>Последние 10 отзывов:</b>\n\n{string}'


def get_facts(message_text: str) -> Iterator[str]:
    facts = cur.execute(f"SELECT fact_name FROM assertions "
                        f"LEFT JOIN facts f ON assertions.assertion_id = f.assertion_id "
                        f"WHERE assertion_name IS '{message_text}'").fetchall()
    for i in range(len(facts)):
        yield facts[i][0]


def get_a_facts(message_text: str) -> Iterator[str]:
    facts = cur.execute(f"SELECT a_fact_name FROM a_facts "
                        f"LEFT JOIN a_assertions aa ON aa.a_assertion_id = a_facts.a_assertion_id "
                        f"WHERE a_assertion_name IS '{message_text}'").fetchall()
    for i in range(len(facts)):
        yield facts[i][0]


def get_assertions(assertion_id=None) -> list:
    assertions = cur.execute(f"SELECT a_assertion_name FROM a_assertions"
                             f" LEFT JOIN assertions a ON a.assertion_id = a_assertions.assertion_id"
                             f" WHERE assertion_name IS '{assertion_id}'").fetchall()
    return [assertions[i][0] for i in range(len(assertions))]


def get_practice_questions() -> Iterator[str]:
    practice_questions = cur.execute("SELECT question_name, pr_id "
                                     "FROM practice_questions").fetchall()
    for i in range(len(practice_questions)):
        yield practice_questions[i][0], practice_questions[i][1]


def get_practice_answers(p_key: str) -> list:
    return cur.execute("SELECT commentary, quality "
                       "FROM practice_answers "
                       "LEFT JOIN practice_questions pq "
                       "ON pq.pr_id = practice_answers.pr_id "
                       f"WHERE pq.pr_id IS '{p_key}';").fetchall()


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
