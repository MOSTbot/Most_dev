# TODO: Hash all admin ids in list_of_admins table and user ids in feedback table
import sqlite3 as sq
from typing import Iterator

from tgbot.utils.util_classes import HashData

db = sq.connect('bot.db')
cur = db.cursor()

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
(assertion_id       INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
assertion_name TEXT         NOT NULL);""")

cur.execute("""CREATE TABLE IF NOT EXISTS facts
(fact_id         INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
fact_name        TEXT    NOT NULL,
assertion_id     INTEGER NOT NULL,
FOREIGN KEY (assertion_id) REFERENCES assertions (assertion_id));""")

cur.execute("""CREATE TABLE IF NOT EXISTS practice_questions
(pr_id           INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
question_name      TEXT  NOT NULL);""")

cur.execute("""CREATE TABLE IF NOT EXISTS practice_answers
(answer_id         INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
answer_name        TEXT    NOT NULL,
commentary         TEXT    NOT NULL,
pr_id     INTEGER NOT NULL,
FOREIGN KEY (pr_id) REFERENCES practice_questions (pr_id));""")

cur.execute("""CREATE TABLE IF NOT EXISTS main_menu
(mm_id           INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
main_menu_name     TEXT  NOT NULL,
description        TEXT);""")


def select_main_menu(table: str, col_name: str):
    rows = cur.execute(f"SELECT {col_name} FROM {table}").fetchall()
    return [row[0] for row in rows]


def select_main_menu_description():
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


async def delete_from_table(table: str, column: str, value: str):
    if cur.execute(f"SELECT * FROM {table} WHERE {column} IS '{value}'").fetchone():
        cur.execute(f"DELETE FROM {table} WHERE {column} IS '{value}'")
        db.commit()
        return True
    return False


def select_all_admins():
    admins_list = cur.execute("SELECT * FROM list_of_admins").fetchall()
    string = ''
    for i in admins_list:
        string = f'{string}Имя: <b>{i[1]}</b>\nХеш ID: <b>{i[2]}</b>\n\n'
    if string == '':
        return 'Список Администраторов пуст'
    else:
        return f'<b>Список Администраторов:</b>\n\n{string}'


def all_admins_list():
    list_of_admins = cur.execute("SELECT admin_id FROM list_of_admins").fetchall()
    list_of_admins = [list_of_admins[i][0] for i, item in enumerate(list_of_admins)]
    return list_of_admins


def send_feedback(user_id: str = None, datetime: str = None, feedback: str = None) -> None:
    hash_user_id = HashData.hash_data(user_id)
    cur.execute('INSERT INTO user_feedback (user_id, feedback_datetime, user_feedback) VALUES(?, ?, ?)',
                (hash_user_id, datetime, feedback))

    db.commit()


def last10_fb():
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


def get_assertions():
    assertions = cur.execute("SELECT assertion_name FROM assertions").fetchall()
    return [assertions[i][0] for i in range(len(assertions))]
