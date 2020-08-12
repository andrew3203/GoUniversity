import psycopg2
import datetime
from psycopg2 import sql


from classes.direction import Direction

DNS = "dbname=Application user=kuand"


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


def get_data(chat_id):
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


class User:

    def __init__(self):
        self.id = None
        self.first_name = None
        self.last_name = None
        self.middle_name = None

        self.chat_id = None

        self.payed = None
        self.user_type = None
        self.subscription = None

        self.is_waiting_for_updates = None

        self.directions = []

    def validate(self, chat_id):
        # returns 0 - need to be registered
        # returns 1 - has been registered, did not pay yat
        # returns 2 - has been registered, request limited
        # returns 3 - has been registered, payed
        # returns 4 - data error
        # returns 5 - connection error
        try:
            with psycopg2.connect(DNS) as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                    SELECT id, first_name, last_name, middle_name, payed, subscription, directions
                    FROM public.users WHERE chat_id = %s
                    """, chat_id)
                    info = cur.fetchall()
                    if len(info) == 0:
                        # there is new user, need to be registered
                        self.chat_id = chat_id
                        return 0

                    elif len(info) == 1:
                        # there is old user, need to check:
                        # his updates
                        self.chat_id = chat_id
                        self.id = info[0][0]
                        self.first_name = info[0][1]
                        self.last_name = info[0][2]
                        self.middle_name = info[0][3]

                        self.payed = info[0][4]
                        self.subscription = info[0][6]

                        self.get_directions_list(info[0][7])

                        return 1
                    else:
                        # send message to user
                        print('\n ------- data error \n -------\n')
                        return 2

        except Exception as e:
            # send message to user
            print(e)

        return 3

    def insert_values(self):
        try:
            with psycopg2.connect(DNS) as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                    INSERT INTO users (id, uname, lastname, middlename, birthday, dateregister, email, chat_id, is_active, 
                    user_type,has_subscription, requests_per_day, payment, ege_score, is_waiting_for_updates, came_from_code, 
                    send_to_code, does_code_expire) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                    %s, %s, %s, %s, %s);
                    """, (self.id, self.name, self.last_name, self.middle_name, self.birthday, self.date_register,
                          self.email, self.chat_id, self.is_active, self.user_type, self.has_subscription,
                          self.requests_per_day, self.payment, self.scores_ege, self.is_waiting_for_updates,
                          self.came_from_code, self.send_to_code, self.does_code_expire))
        except Exception as e:
            # send message to user
            print(e)

    def update_values(self):
        try:
            with psycopg2.connect(DNS) as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                    UPDATE public.users SET uname=%s, lastname=%s, middlename=%s, birthday=%s, dateregister=%s, 
                    email=%s, chat_id=%s, is_active=%s, user_type=%s, has_subscription=%s, requests_per_day=%s, 
                    payment=%s, ege_score=%s, is_waiting_for_updates=%s, came_from_code=%s, send_to_code=%s, 
                    does_code_expire=%s WHERE id = %s;
                    """, (self.name, self.last_name, self.middle_name, self.birthday, self.date_register,
                          self.email, self.chat_id, self.is_active, self.user_type, self.has_subscription,
                          self.requests_per_day, self.payment, self.scores_ege, self.is_waiting_for_updates,
                          self.came_from_code, self.send_to_code, self.does_code_expire, self.id))
        except Exception as e:
            # send message to user
            print(e)

    def get_directions_list(self, id_list):
        self.directions = []
        try:
            with psycopg2.connect(DNS) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM directions WHARE id in %s", id_list)
                    for direction in cur.fetchall():
                        self.directions.append(Direction(direction))

        except Exception as e:
            # send message to user
            print(e)

    def check_email(self, message):

        pass

    def generate_friend_link(self):
        pass

    def delete(self, user_id):  # why exception??
        if self.chat_id == 379082921:
            try:
                with psycopg2.connect(DNS) as conn:
                    with conn.cursor() as cur:
                        cur.execute("DELETE FROM public.users WHERE id = %s;", str(user_id))
                        return True

            except Exception as e:
                # send message to user
                print(e)
        return False



