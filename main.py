import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

import re
from classes import user
import config
import dbworker

import datetime

bot = telebot.TeleBot(config.TOKEN)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    if not user.is_new(message.chat.id):
        name = user.get_user_data(message.chat.id)['last_name']
    elif not message.from_user.first_name == '':
        name = message.from_user.first_name
    else:
        name = message.from_user.username
    text = "" \
           "*Привет, {},* вечер в Хату!\n" \
           "Я могу быстро показать тебе твое место в рейтинговом списке твоего университета!\n" \
           "*Готов начать?*😉\n" \
           "Для начала давай введем персонадьные данные, для того чтобы я мог искать тебя в списках.".format(name)

    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton("Что ты умеешь?🤔", callback_data="help"),
               InlineKeyboardButton("Ввести персональные данные!", callback_data="complete_personal_data"))
    bot.send_message(message.chat.id, parse_mode='Markdown', text=text, reply_markup=markup)


@bot.message_handler(commands=['help'])
@bot.callback_query_handler(func=lambda call: call.data == 'help')
def ask_help(call):
    text = "Описание возможностей. Перечень доступных команд"
    bot.send_message(call.message.chat.id, text=text)


@bot.callback_query_handler(func=lambda call: call.data == 'complete_personal_data')
def ask_personal_data(call):
    text = "Для начала необходимо подписать согласие на обработку персональных данных: "
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("Даю согласие", callback_data="agreed"),
               InlineKeyboardButton("Прочитать согласие", callback_data="send_consent"))
    bot.send_message(call.message.chat.id, parse_mode='Markdown', text=text, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in ['agreed', 'send_consent'])  # !!double click error
def make_consent(call):
    text = "Отлично👍 Осталось немного!\n\n" \
           "Нажмите: _Ввести данные_, чтобы заполнить необходимую информацию\n" \
           "Старайтесь вводить данные без лишних символов:)"
    if call.data == "agreed":
        markup = InlineKeyboardMarkup()
        markup.row_width = 2
        markup.add(InlineKeyboardButton("Даю согласие✅", callback_data="agreed"),
                   InlineKeyboardButton("Прочитать согласие", callback_data='send_consent'))

        bot.answer_callback_query(call.id, "Согласие получено, продолжаем!")
        bot.edit_message_text(chat_id=call.message.chat.id,
                              text="Для начала необходимо подписать согласие на обработку персональных данных:",
                              message_id=call.message.message_id, reply_markup=markup)

        markup1 = InlineKeyboardMarkup()
        markup1.add(InlineKeyboardButton("Ввести данные", callback_data="register"))
        bot.send_message(chat_id=call.message.chat.id, text=text,
                         timeout=100, reply_markup=markup1, parse_mode='Markdown')
    else:
        bot.answer_callback_query(call.id, "cb_want_read")


# --- register/update profile ----
# @bot.message_handler(commands=['register', 'updateProfile'])
@bot.callback_query_handler(func=lambda call: call.data == 'register')
def profile_register(call):
    chat_id = call.message.chat.id
    dbworker.set_state(chat_id, config.States.S_NAME.value)
    bot.send_message(chat_id, text=config.States.S_NAME_MESSAGE.value)


# NAME
@bot.message_handler(func=lambda message: config.name_filter(message.chat.id))
def user_entering_name(message):
    if user.update_names(message, 'first_name'):
        bot.send_message(message.chat.id, text=config.States.S_LAST_NAME_MESSAGE.value)
        dbworker.set_state(message.chat.id, config.States.S_LAST_NAME.value)
    else:
        bot.send_message(message.chat.id, text=config.States.S_ERROR_MESSAGE.value)
        dbworker.set_state(message.chat.id, config.States.S_NAME.value)


# LAST_NAME
@bot.message_handler(func=lambda message: config.lastname_filter(message.chat.id))
def user_entering_last_name(message):
    if user.update_names(message, 'last_name'):
        bot.send_message(message.chat.id, text=config.States.S_MIDDLE_NAME_MESSAGE.value)
        dbworker.set_state(message.chat.id, config.States.S_MIDDLE_NAME.value)
    else:
        bot.send_message(message.chat.id, text=config.States.S_ERROR_MESSAGE.value)
        dbworker.set_state(message.chat.id, config.States.S_LAST_NAME.value)


# MIDDLE_NAME
@bot.message_handler(func=lambda message: config.middlename_filter(message.chat.id))
def user_entering_middle_name(message):
    if user.update_names(message, 'middle_name'):
        bot.send_message(message.chat.id, text=config.States.S_BIRTHDAY_MESSAGE.value)
        dbworker.set_state(message.chat.id, config.States.S_BIRTHDAY.value)
    else:
        bot.send_message(message.chat.id, text=config.States.S_ERROR_MESSAGE.value)
        dbworker.set_state(message.chat.id, config.States.S_MIDDLE_NAME.value)


# BIRTHDAY
@bot.message_handler(func=lambda message: config.birthday_filter(message.chat.id))
def user_entering_birthday(message):
    if user.update_birthday(message):
        bot.send_message(message.chat.id, text=config.States.S_EMAIL_MESSAGE.value)
        dbworker.set_state(message.chat.id, config.States.S_EMAIL.value)
    else:
        bot.send_message(message.chat.id, text=config.States.S_ERROR_MESSAGE.value)
        dbworker.set_state(message.chat.id, config.States.S_BIRTHDAY.value)


# EMAIL
@bot.message_handler(func=lambda message: config.email_filter(message.chat.id))
def user_entering_email(message):
    try:
        if message.entities[0].type == 'email' and user.update_email(message):
            bot.send_message(message.chat.id, text=config.States.S_FINISH_MESSAGE.value, parse_mode='Markdown')
            dbworker.set_state(message.chat.id, config.States.S_START.value)
            print('ok')
            text = "На данный момент доступны следующие университеты:"
            show_data_from(message.chat.id, text, 'universities', None, None)
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, text=config.States.S_ERROR_MESSAGE.value)
        dbworker.set_state(message.chat.id, config.States.S_EMAIL.value)


# ------- universities & departments & directions  --------

def show_data_from(chat_id, text, table, val_where, val):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    objects = user.get_data_from(table, val_where, val)
    for obj in objects:
        callback = str(obj[0]) + "_" + table
        markup.add(InlineKeyboardButton(obj[1], callback_data=callback))

    bot.send_message(chat_id, text=text, reply_markup=markup)


# ------- add direction --------
@bot.message_handler(commands=['addUniversity'])
def add_university(message):
    text = "На данный момент доступны следующие университеты:"
    show_data_from(message.chat.id, text, 'universities', None, None)


@bot.callback_query_handler(func=lambda call: re.match(r'\d{,}[1-9]_universities', call.data) is not None)
def show_departments(call):
    text = "На данный момент для этого университета доступны следующие факультеты:"
    un_id = int(re.match(r'\d{,}[1-9]', call.data).group())
    show_data_from(call.message.chat.id, text, 'departments', 'un_id', un_id)


@bot.callback_query_handler(func=lambda call: re.match(r'\d{,}[1-9]_departments', call.data) is not None)
def show_directions(call):
    text = "На данный момент для этого факультета доступны следующие направления:"
    dp_id = int(re.match(r'\d{,}[1-9]', call.data).group())
    show_data_from(call.message.chat.id, text, 'directions', 'dp_id', dp_id)


@bot.callback_query_handler(func=lambda call: re.match(r'\d{,}[1-9]_directions', call.data) is not None)
def show_directions(call):
    dr_id = re.match(r'\d{,}[1-9]', call.data).group()
    text = "Вы выбрали университет " + dr_id
    bot.send_message(call.message.chat.id, text=text)


bot.infinity_polling()

