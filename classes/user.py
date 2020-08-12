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
                            (email, 'user', message.chat.id))
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
                mas = cur.fetchone()[0]
                if mas is None:
                    mas = [dr_id]
                elif dr_id not in mas:
                    mas.append(dr_id)
                else:
                    return 2

                cur.execute("UPDATE users SET  directions = %s  WHERE chat_id = %s", (mas, chat_id))
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
                    'payed': fet[7],
                    'user_type': fet[8],
                    'subscription': fet[9],
                    'request_per_day': fet[10],
                    'coast': fet[11],
                    'ege_score': fet[12],
                    'waiting_for_updates': fet[13],
                    'received_code': fet[14],
                    'shared_code': fet[15],
                    'directions': fet[16],
                    'id': fet[17],
                    'chat_id': fet[18],
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
                INSERT INTO public.users( date_register, chat_id, payed, user_type, subscription, request_per_day, 
                coast, waiting_for_updates) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);""",
                            (datetime.datetime.now(), chat_id, False, 'guest', False, 0, 300, False))

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

