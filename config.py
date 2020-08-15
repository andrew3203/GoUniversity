# -*- coding: utf-8 -*-

from enum import Enum
from dbworkers import dbworker

TOKEN = '1232696304:AAHjcTwO3oelfj6fWAmg1pcADKG081jlqpY'
db_file = "database.vdb"

ACCESS_LEVEL_1 = ['admin']
ACCESS_LEVEL_2 = ['admin', 'user:active', 'user:unpaid']
ACCESS_LEVEL_3 = ['admin', 'user:active', 'user:unpaid', 'user:unpaid:limited']
ACCESS_LEVEL_4 = ['admin', 'user:active', 'user:unpaid', 'user:unpaid:limited', 'guest']


class States(Enum):
    S_START = "0"  # Начало нового диалога
    S_START_MESSAGE = 'Давайте для начала зарегистрируемся'

    S_NAME = "1"
    S_NAME_MESSAGE = 'Введите имя:'

    S_LAST_NAME = "2"
    S_LAST_NAME_MESSAGE = "Укажи, пожалуйста, свою фаммилию."

    S_MIDDLE_NAME = "3"
    S_MIDDLE_NAME_MESSAGE = "Отлично! Теперь укажи, пожалуйста, отчество."

    S_BIRTHDAY = "4"
    S_BIRTHDAY_MESSAGE = "Принято! Теперь укажи, пожалуйста, дату рождения в формате день.месяц.год."

    S_EMAIL = "5"
    S_EMAIL_MESSAGE = "Теперь укажи, пожалуйста, почту."

    S_ERROR_MESSAGE = "Что то пошло не так...\n" \
                      "Вероятно вы допустили кукую-то ошибку.\n" \
                      "Попробуйте ввести свои данные еще раз"

    S_FINISH_MESSAGE = "*Все данные успешно сохранены!*\n" \
                       "Теперь давай добавим университет.\n"

    S_PROBLEM = "6"
    S_PROBLEM_MESSAGE = 'Пожайлуста, опишите с начала проблему, о которой хотели сообщить'


def finished_registration(chat_id):
    if not dbworker.get_current_state(chat_id) == States.S_START.value:
        cur = dbworker.get_current_state(chat_id)

        if cur == '1':
            text = States.S_NAME_MESSAGE.value
        elif cur == '2':
            text = States.S_LAST_NAME_MESSAGE.value
        elif cur == '3':
            text = States.S_MIDDLE_NAME_MESSAGE.value
        elif cur == '4':
            text = States.S_BIRTHDAY_MESSAGE.value
        elif cur == '5':
            text = States.S_EMAIL_MESSAGE.value
        elif cur == '6':
            text = States.S_PROBLEM_MESSAGE.value
        else:
            text = States.S_ERROR_MESSAGE.value

        return text
    return None


def name_filter(chat_id):
    return dbworker.get_current_state(chat_id) == States.S_NAME.value


def lastname_filter(chat_id):
    return dbworker.get_current_state(chat_id) == States.S_LAST_NAME.value


def middlename_filter(chat_id):
    return dbworker.get_current_state(chat_id) == States.S_MIDDLE_NAME.value


def birthday_filter(chat_id):
    return dbworker.get_current_state(chat_id) == States.S_BIRTHDAY.value


def email_filter(chat_id):
    return dbworker.get_current_state(chat_id) == States.S_EMAIL.value


def problem_filter(chat_id):
    return dbworker.get_current_state(chat_id) == States.S_PROBLEM.value


def direction_filter(data):
    try:
        arr = data.split('. ')
        if len(arr) == 3 and \
                arr[0].isalpha() and arr[1].isalpha() and arr[2].isalpha():
            return True
        else:
            return False
    except:
        return False









