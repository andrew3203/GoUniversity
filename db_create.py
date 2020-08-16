import psycopg2
import config

create_db = """
CREATE DATABASE "Application"
    WITH 
    ENCODING = 'UTF8';
"""

create_users = """
CREATE TABLE users
(
    id SERIAL PRIMARY KEY,
    chat_id integer,
    first_name character varying(30),
    last_name character varying(40),
    middle_name character varying(40),
    birthday date,
    date_register date,
    email character varying(40),
    phone character varying(9),
    user_type character varying(50),
    request_per_day integer,
    ege_score integer,
    waiting_for_updates boolean,
    received_code character varying(50),
    shared_code character varying(50)
    directions integer[],
    signed_consent boolean DEFAULT false,
    price integer,
    CONSTRAINT users_chat_id_key UNIQUE (chat_id)
)
"""

create_universities = """
CREATE TABLE universities
(
    id SERIAL PRIMARY KEY,
    name character varying(20) PRIMARY KEY,
    full_name character varying(70),
    site character varying(250),
    CONSTRAINT universities_id_key UNIQUE (id),
    CONSTRAINT universities_short_name_key UNIQUE (name)
)
"""

create_departments = """
CREATE TABLE departments
(
    id SERIAL PRIMARY KEY,
    name character varying(15),
    full_name character varying(70),
    site character varying(150),
    un_id integer,
    CONSTRAINT university FOREIGN KEY (un_id)
        REFERENCES universities (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)


"""

create_directions = """
CREATE TABLE directions
(
    id SERIAL PRIMARY KEY,
    name character varying(50),
    applicants_came integer,
    applicants_limit integer,
    originals_amount integer,
    data_link character varying(250),
    site character varying(250),
    dp_id integer,
    CONSTRAINT department FOREIGN KEY (dp_id)
        REFERENCES departments (id) MATCH SIMPLE
        ON UPDATE CASCADE 
        ON DELETE NO ACTION
)
"""

create_reviews1 = """
CREATE TABLE education_reviews
(
    id SERIAL PRIMARY KEY,
    chat_id integer,
    text character varying(500),
    mark integer,
    ref_id integer,
    add_date date,
    CONSTRAINT university_reviews_un_id_fkey FOREIGN KEY (ref_id)
        REFERENCES universities (id) MATCH SIMPLE
        ON UPDATE CASCADE 
        ON DELETE NO ACTION
)
"""

create_reviews2 = """
CREATE TABLE service_reviews
(
    id SERIAL PRIMARY KEY,
    chat_id integer,
    text character varying(500),
    mark integer,
    add_date date
)
"""

create_problems = """
CREATE TABLE problems
(
    id SERIAL PRIMARY KEY,
    problem character varying(150),
    date_add date,
    need_update boolean DEFAULT false,
    chat_id integer
)
"""

create_payments = """
CREATE TABLE payments
(
    id SERIAL PRIMARY KEY,
    price real,
    chat_id integer,
    pay_date date,
    license_period date
)
"""

create_states = """
CREATE TABLE states
(
    id SERIAL PRIMARY KEY,
    chat_id integer,
    link character varying(250),
    full_name character varying(150),
    current_state integer,
    CONSTRAINT states_full_name_key UNIQUE (full_name)
)
"""
commands = [
    create_db,
    create_users,
    create_universities,
    create_departments,
    create_directions,
    create_reviews1,
    create_reviews2,
    create_problems,
    create_payments,
    create_states
]


def main():
    try:
        with psycopg2.connect(config.DATABASE_URL, sslmode='require') as conn:
            with conn.cursor() as cur:
                for command in commands:
                    cur.execute(command)

                conn.commit()
                print('DB has created\n')

                return True
    except Exception as e:
        print(e)
        return False


main()
