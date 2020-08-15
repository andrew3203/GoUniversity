import psycopg2
import datetime
from psycopg2 import sql


from classes.direction import Direction

DNS = "dbname=Application user=kuand"


# ------- user functions --------
def update_names(message, val='first_name', table='users', lenn=40):
    text = message.text.strip()
    if len(text) < lenn and text.isalpha():
        try:
            with psycopg2.connect(DNS) as conn:
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
            with psycopg2.connect(DNS) as conn:
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
    try:
        with psycopg2.connect(DNS) as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE users SET  email = %s, user_type = %s WHERE chat_id = %s",
                            (email, 'user:unpaid', message.chat.id))
                conn.commit()

    except Exception as e:
        print(e)
        return False

    return True


# check limit of directions in each university
def update_directions(chat_id, dr_id):
    try:
        with psycopg2.connect(DNS) as conn:
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
        with psycopg2.connect(DNS) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM public.users WHERE chat_id = %(int)s;", {'int': chat_id})
                fet = cur.fetchone()
                data = {
                    'first_name': fet[0],
                    'last_name': fet[1],
                    'middle_name': fet[2],
                    'birthday': fet[3],
                    'date_register': fet[4],
                    'email': fet[5],
                    'phone': fet[6],
                    'user_type': fet[7],
                    'subscription': fet[8],
                    'request_per_day': fet[9],
                    'coast': fet[10],
                    'ege_score': fet[11],
                    'waiting_for_updates': fet[12],
                    'received_code': fet[13],
                    'shared_code': fet[14],
                    'directions': fet[15],
                    'id': fet[16],
                    'chat_id': fet[17],
                    'signed_consent': fet[18],
                }
                return data
    except Exception as e:
        # send message to user
        print(e)
    return data


def is_new(chat_id):
    try:
        with psycopg2.connect(DNS) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                INSERT INTO public.users( date_register, chat_id, user_type, subscription, request_per_day, 
                signed_consent) VALUES (%s, %s, %s, %s, %s, %s);""",
                            (datetime.datetime.now(), chat_id, 'guest', False, 0, False))

                conn.commit()
            return True

    except Exception as e:
        print(e)
        return False


# ------- for universities & departments & directions  --------
def get_data_from(table, val_where, val):
    try:
        with psycopg2.connect(DNS) as conn:
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
        with psycopg2.connect(DNS) as conn:
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
        with psycopg2.connect(DNS) as conn:
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


def delete_directions(chat_id, remove):
    try:
        with psycopg2.connect(DNS) as conn:
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
        with psycopg2.connect(DNS) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, name FROM departments WHERE un_id = %(int)s", {'int': un_id})
                ans = cur.fetchall()
                return ans

    except Exception as e:
        print(e)
        return None


def sign_consent(chat_id, st=True):
    try:
        with psycopg2.connect(DNS) as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE users SET  signed_consent = %s WHERE chat_id = %s", (st, chat_id))
                return True

    except Exception as e:
        print(e)
        return False


def check_sign_consent(chat_id):
    try:
        with psycopg2.connect(DNS) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT signed_consent FROM users WHERE chat_id = %(int)s", {'int': chat_id})
                qur = cur.fetchone()
                return qur[0]

    except Exception as e:
        print(e)
        return False


def get_user_type(chat_id):
    try:
        with psycopg2.connect(DNS) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT user_type FROM users WHERE chat_id = %(int)s", {'int': chat_id})
                qur = cur.fetchone()
                return qur[0]

    except Exception as e:
        print(e)
        return 'guest'


def save_user_problem(chat_id, problem):
    try:
        with psycopg2.connect(DNS) as conn:
            with conn.cursor() as cur:
                cur.execute("""INSERT INTO public.problems(chat_id, problem, date_add, need_update) 
                VALUES (%s, %s, %s, %s);""", (chat_id, problem, datetime.datetime.now(), True))
                return True

    except Exception as e:
        print(e)
        return False
