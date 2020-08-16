import psycopg2
import datetime
from psycopg2 import sql

import parsers
import config


# ------- user functions --------
def update_names(message, val='first_name', table='users', lenn=40):
    text = message.text.strip()
    if len(text) < lenn and text.isalpha():
        try:
            with psycopg2.connect(config.DATABASE_URL, sslmode='require') as conn:
                with conn.cursor() as cur:
                    qur = sql.SQL("UPDATE {} SET  {} = %s WHERE chat_id = %s").format(sql.Identifier(table),
                                                                                          sql.Identifier(val))
                    text.capitalize()
                    cur.execute(qur, (text, message.chat.id))
                    conn.commit()
        except Exception as e:
            print(e)
            return False

        return True
    else:
        return False


def update_birthday(message):
    # need dd.mm.year
    text = message.text.strip()
    li = text.split('.')
    try:
        if (len(li) == 3) \
                and (0 < len(li[0]) <= 2) and (0 < len(li[1]) <= 2) and ( len(li[2]) == 4) \
                and (int(li[0]) > 0) and (int(li[1]) > 0) and (int(li[2]) > 0):

            birthday = datetime.date(int(li[2]), int(li[1]), int(li[0]))
            with psycopg2.connect(config.DATABASE_URL, sslmode='require') as conn:
                with conn.cursor() as cur:
                    cur.execute("UPDATE users SET  birthday = %s  WHERE chat_id = %s", (birthday,  message.chat.id))
                    conn.commit()

            return True

    except Exception as e:
        # send message to user
        print(e)
    return False


def update_email(message):
    email = message.text
    user_default_status = 'user:unpaid'
    try:
        with psycopg2.connect(config.DATABASE_URL, sslmode='require') as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE users SET  email = %s, user_type = %s WHERE chat_id = %s",
                            (email, user_default_status, message.chat.id))
                conn.commit()

    except Exception as e:
        print(e)
        return False

    return True


# check limit of directions in each university
def update_directions(chat_id, dr_id):
    try:
        with psycopg2.connect(config.DATABASE_URL, sslmode='require') as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT directions FROM users WHERE chat_id = %(int)s", {'int': chat_id})
                directions = cur.fetchone()[0]
                if directions is None:
                    directions = [dr_id]
                elif dr_id not in directions:
                    directions.append(dr_id)
                else:
                    return 2

                cur.execute("UPDATE users SET  directions = %s  WHERE chat_id = %s", (directions, chat_id))
                conn.commit()
        return 1
    except Exception as e:
        print(e)
        return 0


def get_user_data(chat_id):
    data = {}
    try:
        with psycopg2.connect(config.DATABASE_URL, sslmode='require') as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM public.users WHERE chat_id = %(int)s;", {'int': chat_id})
                fet = cur.fetchone()
                data = {
                    'first_name': fet[0],
                }
                return data
    except Exception as e:
        # send message to user
        print(e)
    return data


def is_new(chat_id):
    try:
        with psycopg2.connect(config.DATABASE_URL, sslmode='require') as conn:
            with conn.cursor() as cur:
                cur.execute("""
                INSERT INTO public.users( date_register, chat_id, user_type, request_per_day, 
                signed_consent) VALUES (%s, %s, %s, %s, %s);""",
                            (datetime.date.today(), chat_id, 'guest', 0, False))

                conn.commit()
            return True

    except Exception as e:
        print(e)
        return False


# ------- for universities & departments & directions  --------
def get_data_from(table, val_where, val):
    try:
        with psycopg2.connect(config.DATABASE_URL, sslmode='require') as conn:
            with conn.cursor() as cur:
                if table == 'universities':
                    cur.execute("SELECT * FROM universities")
                else:
                    qur = sql.SQL("SELECT * FROM  {} WHERE {} = %(int)s").format(sql.Identifier(table),
                                                                            sql.Identifier(val_where))
                    cur.execute(qur, {'int': val})
                return cur.fetchall()

    except Exception as e:
        print(e)
        return []


def get_all_user_directions(chat_id):
    try:
        with psycopg2.connect(config.DATABASE_URL, sslmode='require') as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT directions FROM users WHERE chat_id = %(int)s", {'int': chat_id})
                directions = tuple(cur.fetchone()[0])
                sql = "SELECT universities.name, departments.name, directions.name, directions.id " \
                      "FROM universities, departments, directions  " \
                      "WHERE directions.dp_id = departments.id and departments.un_id = universities.id " \
                      "and directions.id in %s;"
                cur.execute(sql, (directions,))
                return cur.fetchall()

    except Exception as e:
        print(e)
        return []


def get_direction(un_name, dp_name, dr_name, chat_id):
    try:
        with psycopg2.connect(config.DATABASE_URL, sslmode='require') as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT directions FROM users WHERE chat_id = %(int)s", {'int': chat_id})
                directions_id = tuple(cur.fetchone()[0])

                cur.execute("SELECT dp_id FROM directions WHERE id in %s and name = %s", (directions_id, dr_name))
                dp_ids = tuple([num[0] for num in cur.fetchall()])

                if len(dp_ids) == 0:
                    return None
                elif len(dp_ids) == 1:
                    cur.execute("SELECT applicants_came, originals_amount, data_link "
                                "FROM directions WHERE id in %s and name = %s", (directions_id, dr_name))
                    return cur.fetchone()

                cur.execute("SELECT un_id FROM departments WHERE id in %s and name = %s", (dp_ids, dp_name))
                un_ids = tuple([num[0] for num in cur.fetchall()])

                # back
                cur.execute("SELECT id FROM universities WHERE id in %s and name = %s", (un_ids, un_name))
                un_id = cur.fetchone()

                cur.execute("SELECT id FROM departments WHERE un_id = %s and name = %s", (un_id, dp_name))
                dp_id = cur.fetchone()

                cur.execute("""
                SELECT applicants_came, originals_amount, data_link
                FROM directions WHERE dp_id = %s and name = %s""", (dp_id, dr_name))

                return cur.fetchone()

    except Exception as e:
        print(e)
        return None


def request_count(chat_id):
    try:
        with psycopg2.connect(config.DATABASE_URL, sslmode='require') as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT request_per_day, user_type "
                            "FROM users WHERE chat_id = %(int)s", {'int': chat_id})
                ans = cur.fetchone()
                print(ans)
                res = int(ans[0]) + 1
                if ans[1] == 'user:unpaid' and \
                        int(ans[0]) + 1 >= config.REQUEST_PER_DAY_AMOUNT:
                    cur.execute("UPDATE users SET  user_type = %s WHERE chat_id = %s", ('user:unpaid:limited', chat_id))
                    conn.commit()
                    return False
                elif ans[1] == 'user:unpaid' and \
                        res < config.REQUEST_PER_DAY_AMOUNT:
                    cur.execute("UPDATE users SET request_per_day = %s WHERE chat_id = %s",
                                (res, chat_id))
                    conn.commit()

                return True

    except Exception as e:
        print(e)
        return True


def delete_directions(chat_id, remove):
    try:
        with psycopg2.connect(config.DATABASE_URL, sslmode='require') as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT directions FROM users WHERE chat_id = %(int)s", {'int': int(chat_id)})
                ans = cur.fetchall()[0]
                res = []
                for num in ans[0]:
                    if num not in remove:
                        res.append(num)

                cur.execute("UPDATE users SET  directions = %s WHERE chat_id = %s", (res, chat_id))

                conn.commit()

                return True

    except Exception as e:
        print(e)
        return False


def get_departments_by_un_id(un_id):
    try:
        with psycopg2.connect(config.DATABASE_URL, sslmode='require') as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, name FROM departments WHERE un_id = %(int)s", {'int': un_id})
                ans = cur.fetchall()
                return ans

    except Exception as e:
        print(e)
        return None


def sign_consent(chat_id, st=True):
    try:
        with psycopg2.connect(config.DATABASE_URL, sslmode='require') as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE users SET  signed_consent = %s WHERE chat_id = %s", (st, chat_id))
                return True

    except Exception as e:
        print(e)
        return False


def check_sign_consent(chat_id):
    try:
        with psycopg2.connect(config.DATABASE_URL, sslmode='require') as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT signed_consent FROM users WHERE chat_id = %(int)s", {'int': chat_id})
                qur = cur.fetchone()
                return qur[0]

    except Exception as e:
        print(e)
        return False


def get_user_type(chat_id):
    try:
        with psycopg2.connect(config.DATABASE_URL, sslmode='require') as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT user_type FROM users WHERE chat_id = %(int)s", {'int': chat_id})
                qur = cur.fetchone()
                return qur[0]

    except Exception as e:
        print(e)
        return 'guest'


def save_user_problem(chat_id, problem):
    try:
        with psycopg2.connect(config.DATABASE_URL, sslmode='require') as conn:
            with conn.cursor() as cur:
                cur.execute("""INSERT INTO public.problems(chat_id, problem, date_add, need_update) 
                VALUES (%s, %s, %s, %s);""", (chat_id, problem, datetime.datetime.now(), True))
                return True

    except Exception as e:
        print(e)
        return False


def save_review(chat_id, table='service_reviews', text=None, mark=None):
    try:
        with psycopg2.connect(config.DATABASE_URL, sslmode='require') as conn:
            with conn.cursor() as cur:
                if mark is not None:
                    sql = "SELECT id FROM {} WHERE chat_id = %s and add_date = %s;".format(table)
                    cur.execute(sql, (chat_id, datetime.date.today()))
                    ans = cur.fetchone()
                    if ans is None:
                        sql = "INSERT INTO {} (chat_id, mark, add_date) VALUES (%s, %s, %s);".format(table)
                        cur.execute(sql, (chat_id, mark, datetime.date.today()))
                    else:
                        sql = "UPDATE {} SET mark = %s " \
                              "WHERE chat_id = %s and add_date = %s;".format(table)
                        cur.execute(sql, (mark, chat_id, datetime.date.today()))

                else:
                    sql = "UPDATE {} SET text = %s " \
                          "WHERE chat_id = %s and add_date = %s;".format(table)
                    cur.execute(sql, (text, chat_id, datetime.date.today()))

                conn.commit()
                return True

    except Exception as e:
        print(e)
        return False


def manage_directions_notify(chat_id, names, todo='add'):
    try:
        with psycopg2.connect(config.DATABASE_URL, sslmode='require') as conn:
            with conn.cursor() as cur:
                if todo == 'add':
                    sql = "INSERT INTO states (chat_id, link, full_name, current_state) " \
                          "VALUES (%s, %s, %s, %s);"
                    for name in names:
                        un_name, dp_name, dr_name = name.split('. ')
                        link = get_direction(un_name, dp_name, dr_name, chat_id)[-1]
                        current_state = parsers.get_current_state(name, link)
                        cur.execute(sql, (chat_id, link, name, current_state))
                else:
                    sql = "DELETE FROM states WHERE chat_id = %s and full_name in %s"
                    cur.execute(sql, (chat_id, tuple(names)))
                conn.commit()
                return True

    except Exception as e:
        print(e)
        return False


def get_notify_directions(chat_id):
    try:
        with psycopg2.connect(config.DATABASE_URL, sslmode='require') as conn:
            with conn.cursor() as cur:
                sql = "SELECT full_name FROM states WHERE chat_id = %(int)s;"
                cur.execute(sql, {'int': chat_id})
                resp = cur.fetchall()
                ans = []
                for i in range(len(resp)):
                    ans.append(tuple(resp[i][0].split('. ')) + (i,))
                return ans

    except Exception as e:
        print(e)
        return None


def get_available_notify_directions(chat_id):
    names = ["{}. {}. {}".format(num[0], num[1], num[2]) for num in get_all_user_directions(chat_id)]
    try:
        with psycopg2.connect(config.DATABASE_URL, sslmode='require') as conn:
            with conn.cursor() as cur:
                sql = "SELECT full_name FROM states WHERE chat_id = %(int)s;"
                cur.execute(sql, {'int': chat_id})
                resp = [num[0] for num in cur.fetchall()]
                ans = []
                for i in range(len(names)):
                    if names[i] not in resp:
                        ans.append(tuple(names[i].split('. ')) + (i,))

                return ans

    except Exception as e:
        print(e)
        return None


def update_user_type(chat_id):
    try:
        with psycopg2.connect(config.DATABASE_URL, sslmode='require') as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE users SET user_type = %s WHERE chat_id = %s", ('user:active', chat_id))
                conn.commit()

                return True

    except Exception as e:
        print(e)
        return False


def commit_payment(chat_id, price=185):
    try:
        with psycopg2.connect(config.DATABASE_URL, sslmode='require') as conn:
            with conn.cursor() as cur:
                update_user_type(chat_id)
                sql = "INSERT INTO payments (price, chat_id, pay_date, license_period) " \
                      "VALUES (%s, %s, %s, %s);"
                delta = datetime.date(2000, 6, 1) - datetime.date(2000, 1, 1)
                cur.execute(sql, (price, chat_id, datetime.date.today(), datetime.date.today() + delta))
                conn.commit()

                return True

    except Exception as e:
        print(e)
