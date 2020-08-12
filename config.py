# -*- coding: utf-8 -*-

from enum import Enum

import dbworker

TOKEN = '1232696304:AAHjcTwO3oelfj6fWAmg1pcADKG081jlqpY'
db_file = "database.vdb"


class States(Enum):
    S_START = "0"  # Начало нового диалога
    S_START_MESSAGE = 'Давайте продолжим регистрацию'

    S_NAME = "1"
    S_NAME_MESSAGE = 'Введите имя:'

    S_LAST_NAME = "2"
    S_LAST_NAME_MESSAGE = "Запомню! Теперь укажи, пожалуйста, свою фаммилию."

    S_MIDDLE_NAME = "3"
    S_MIDDLE_NAME_MESSAGE = "Отлично! Теперь укажи, пожалуйста, отчество."

    S_BIRTHDAY = "4"
    S_BIRTHDAY_MESSAGE = "Принято! Теперь укажи, пожалуйста, дату рождения в формате день.месяц.год."

    S_EMAIL = "5"
    S_EMAIL_MESSAGE = "Теперь укажи, пожалуйста, почту."

    S_ERROR_MESSAGE = "Что то пошло не так...\n" \
                      "Вероятно вы допустили кукую-то ошибку.\n" \
                      "Попробуйте ввести еще раз"

    S_FINISH_MESSAGE = "*Все данные успешно сохранены!*\nТеперь давай добавим университет"


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
        else:
            text = States.S_EMAIL_MESSAGE.value

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




