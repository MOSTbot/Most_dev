CREATE TABLE IF NOT EXISTS list_of_admins
(
    a_id       INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    admin_name TEXT    NOT NULL,
    admin_id   TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS user_feedback
(
    fb_id             INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    user_id           TEXT    NOT NULL,
    feedback_datetime TEXT    NOT NULL,
    user_feedback     TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS assertions
(
    assertion_id   INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    assertion_name TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS facts
(
    fact_id      INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    fact_name    TEXT    NOT NULL,
    ext_source   TEXT,
    assertion_id INTEGER NOT NULL,
    FOREIGN KEY (assertion_id) REFERENCES assertions (assertion_id)
);

CREATE TABLE IF NOT EXISTS practice_questions
(
    pr_id         INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    question_name TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS practice_answers
(
    answer_id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    answer_num TEXT    NOT NULL,
    commentary TEXT    NOT NULL,
    score      INTEGER NOT NULL,
    pr_id      INTEGER NOT NULL,
    FOREIGN KEY (pr_id) REFERENCES practice_questions (pr_id)
);

CREATE TABLE IF NOT EXISTS adv_assertions
(
    adv_id          INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    adv_assertion   TEXT    NOT NULL,
    adv_description TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS adv_answers
(
    adv_ans_id      INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    adv_answers     TEXT    NOT NULL,
    adv_description TEXT    NOT NULL,
    adv_id          INTEGER NOT NULL,
    FOREIGN KEY (adv_id) REFERENCES adv_assertions (adv_id)
);

CREATE TABLE IF NOT EXISTS main_menu
(
    mm_id          INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    main_menu_name TEXT    NOT NULL,
    description    TEXT
);

CREATE TABLE IF NOT EXISTS a_assertions
(
    a_assertion_id   INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    a_assertion_name TEXT    NOT NULL,
    assertion_id     INTEGER NOT NULL,
    FOREIGN KEY (assertion_id) REFERENCES assertions (assertion_id)
);

CREATE TABLE IF NOT EXISTS a_facts
(
    a_fact_id      INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    a_fact_name    TEXT    NOT NULL,
    a_ext_source   TEXT,
    a_assertion_id INTEGER NOT NULL,
    FOREIGN KEY (a_assertion_id) REFERENCES a_assertions (a_assertion_id)
);

CREATE TABLE IF NOT EXISTS data_privacy
(
    dp_id       INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    dp_question TEXT    NOT NULL,
    dp_answer   TEXT
);