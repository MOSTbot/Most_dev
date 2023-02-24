CREATE TABLE IF NOT EXISTS list_of_admins
(
    a_id       SERIAL  NOT NULL PRIMARY KEY,
    admin_name TEXT    NOT NULL,
    admin_id   TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS user_feedback
(
    fb_id             SERIAL  NOT NULL PRIMARY KEY,
    user_id           TEXT    NOT NULL,
    feedback_datetime TEXT    NOT NULL,
    user_feedback     TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS user_feedback_private
(
    fb_id             SERIAL  NOT NULL PRIMARY KEY,
    user_id           TEXT    NOT NULL,
    feedback_datetime TEXT    NOT NULL,
    user_feedback     TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS assertions
(
    assertion_id   SERIAL PRIMARY KEY,
    assertion_name TEXT
);

CREATE TABLE IF NOT EXISTS facts
(
    fact_id      SERIAL PRIMARY KEY,
    fact_name    TEXT,
    ext_source   TEXT,
    assertion_id INTEGER,
    FOREIGN KEY (assertion_id) REFERENCES assertions (assertion_id)
);

CREATE TABLE IF NOT EXISTS practice_questions
(
    pr_id         SERIAL PRIMARY KEY,
    question_name TEXT
);

CREATE TABLE IF NOT EXISTS practice_answers
(
    answer_id  SERIAL PRIMARY KEY,
    answer_num INTEGER,
    commentary TEXT,
    score      INTEGER,
    pr_id      INTEGER,
    FOREIGN KEY (pr_id) REFERENCES practice_questions (pr_id)
);

CREATE TABLE IF NOT EXISTS adv_assertions
(
    adv_id          SERIAL PRIMARY KEY,
    adv_assertion   TEXT,
    adv_description TEXT
);

CREATE TABLE IF NOT EXISTS adv_answers
(
    adv_ans_id      SERIAL PRIMARY KEY,
    adv_answers     TEXT,
    adv_description TEXT,
    adv_id          INTEGER,
    FOREIGN KEY (adv_id) REFERENCES adv_assertions (adv_id)
);

CREATE TABLE IF NOT EXISTS main_menu
(
    mm_id          SERIAL PRIMARY KEY,
    main_menu_name TEXT,
    description    TEXT
);

CREATE TABLE IF NOT EXISTS a_assertions
(
    a_assertion_id   SERIAL PRIMARY KEY,
    a_assertion_name TEXT,
    assertion_id     INTEGER,
    FOREIGN KEY (assertion_id) REFERENCES assertions (assertion_id)
);

CREATE TABLE IF NOT EXISTS a_facts
(
    a_fact_id      SERIAL PRIMARY KEY,
    a_fact_name    TEXT,
    a_ext_source   TEXT,
    a_assertion_id INTEGER,
    FOREIGN KEY (a_assertion_id) REFERENCES a_assertions (a_assertion_id)
);

CREATE TABLE IF NOT EXISTS data_privacy
(
    dp_id       SERIAL PRIMARY KEY,
    dp_question TEXT,
    dp_answer   TEXT
);

CREATE TABLE IF NOT EXISTS notifications
(
    n_id            SERIAL PRIMARY KEY,
    notification    TEXT
);

CREATE TABLE IF NOT EXISTS users
(
    tid           BIGINT PRIMARY KEY,
    username      TEXT,
    full_name     TEXT,
    status        TEXT,
    last_activity TEXT,
    subscribed    TEXT

);