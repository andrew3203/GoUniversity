import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

import re
from dbworkers import user, dbworker
import config

bot = telebot.TeleBot(config.TOKEN)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    if not user.is_new(message.chat.id):
        name = user.get_user_data(message.chat.id)['first_name']
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


# ------- get help --------
@bot.message_handler(commands=['help'])
def ask_help_command(message):
    text = config.COMMANDS_LIST
    bot.send_message(message.chat.id, text=text, parse_mode='Markdown')


@bot.callback_query_handler(func=lambda call: call.data == 'help')
def ask_help(call):
    text = config.COMMANDS_LIST
    bot.send_message(call.message.chat.id, text=text, parse_mode='Markdown')


# ------- get an agreement --------
def send_consent(chat_id):
    text = "Для начала необходимо подписать согласие на обработку персональных данных: "
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("Даю согласие", callback_data="agreed"),
               InlineKeyboardButton("Прочитать согласие", callback_data="send_consent"))
    bot.send_message(chat_id, parse_mode='Markdown', text=text, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'complete_personal_data')
def ask_personal_data(call):
    send_consent(call.message.chat.id)


@bot.callback_query_handler(func=lambda call: call.data in ['agreed', 'send_consent', 'disagree'])
def make_consent(call):
    text = "Отлично👍 Осталось немного!\n\n" \
           "Нажмите: _Ввести данные_, чтобы заполнить необходимую информацию\n" \
           "Старайтесь вводить данные без лишних символов:)"
    if call.data == "agreed":
        user.sign_consent(call.message.chat.id)
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Даю согласие✅", callback_data="disagree"),
                   InlineKeyboardButton("Прочитать согласие", callback_data='send_consent'))

        bot.answer_callback_query(call.id, "Согласие получено, продолжаем!")
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=markup)

        markup1 = InlineKeyboardMarkup()
        markup1.add(InlineKeyboardButton("Ввести данные", callback_data="register"))
        bot.send_message(chat_id=call.message.chat.id, text=text,
                         timeout=100, reply_markup=markup1, parse_mode='Markdown')

    elif call.data == 'disagree':
        bot.answer_callback_query(call.id, "Вы уже подписали согласие, продолжаем!")
    else:
        bot.answer_callback_query(call.id, "Файл отправлен!")


# ------- register/update profile --------
@bot.message_handler(commands=['register', 'updateprofile'])
def profile_register_command(message):
    if user.check_sign_consent:
        dbworker.set_state(message.chat.id, config.States.S_NAME.value)
        bot.send_message(message.chat.id, text=config.States.S_NAME_MESSAGE.value)
    else:
        send_consent(message.chat.id)


@bot.callback_query_handler(func=lambda call: call.data == 'register')
def profile_register(call):
    dbworker.set_state(call.message.chat.id, config.States.S_NAME.value)
    bot.send_message(call.message.chat.id, text=config.States.S_NAME_MESSAGE.value)


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

            send_university_list(message.chat.id)
        else:
            bot.send_message(message.chat.id, text=config.States.S_ERROR_MESSAGE.value)
            dbworker.set_state(message.chat.id, config.States.S_EMAIL.value)
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, text=config.States.S_ERROR_MESSAGE.value)
        dbworker.set_state(message.chat.id, config.States.S_EMAIL.value)


# ------- markup for universities & departments & directions  --------

def get_markup_for_obj(table, val_where, val, un_id=None):
    markup = InlineKeyboardMarkup()
    objects = user.get_data_from(table, val_where, val)
    for obj in objects:
        callback = str(obj[0]) + "_" + table
        markup.add(InlineKeyboardButton(obj[1], callback_data=callback))

    if table == 'departments':
        text = '« Назад к университетам'
        callback = 'back_from' + "_" + table + '#' + str(val)
        markup.row(InlineKeyboardButton(text, callback_data=callback),
                   InlineKeyboardButton('Нет моего факультета', callback_data='request_for_updates'))
    elif table == 'directions':
        text = '« Назад к факультетам'
        callback = 'back_from' + "_" + table
        if un_id is not None:
            callback += '#' + un_id
        markup.row(InlineKeyboardButton(text, callback_data=callback),
                   InlineKeyboardButton('Нет моего направления', callback_data='request_for_updates'))
    elif table == 'universities':
        markup.row(InlineKeyboardButton('Нет моего университета', callback_data='request_for_updates'))

    return markup


def get_user_directions_keyboard(chat_id):
    directions = user.get_all_user_directions(chat_id)
    if not len(directions) == 0:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        for direction in directions:
            text = "{}. {}. {}".format(direction[0], direction[1], direction[2])
            markup.add(types.KeyboardButton(text))
        return markup
    else:
        return None


def get_direction_data(un_name, dp_name, dr_name, chat_id):
    ans = user.get_direction(un_name, dp_name, dr_name, chat_id)
    if ans is not None:

        text = "*Направление {}, {} {}*\n" \
               "----------------------\n" \
               "Место с таблице: *{}\n*" \
               "Наличие оригинала: *{}*\n" \
               "С оригиналом будет: *{}*\n"
        text_1 = "Колличесво поступающий в списке *{}*\n" \
                 "Колличество оригиналов в списке: *{}*"
        return [text.format(dr_name, dp_name, un_name, 10, 'нет', 2), text_1.format(ans[0], ans[1]), ans[2]]
    else:
        return None


def send_university_list(chat_id):
    text = "На данный момент к системе подключены следующие университеты"
    markup = get_markup_for_obj('universities', None, None)
    bot.send_message(chat_id, text=text, reply_markup=markup)


# ------- add direction --------
@bot.message_handler(commands=['showuniversities'])
def add_university(message):
    ans = config.finished_registration(message.chat.id)
    if ans is not None:
        bot.send_message(message.chat.id, text=ans)
    else:
        send_university_list(message.chat.id)


@bot.callback_query_handler(func=lambda call: 'back_from_departments' == call.data.split('#')[0])  # !!!
def show_universities_callback(call):
    text = "На данный момент к системе подключены следующие университеты"
    bot.answer_callback_query(call.id, "Ответ получен, загружаем данные!")
    markup = get_markup_for_obj('universities', None, None)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=text, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: 'back_from_directions' == call.data.split('#')[0])  # !!!
def show_department_callback(call):
    bot.answer_callback_query(call.id, "Ответ получен, загружаем данные!")
    un_id = call.data.split('#')[1]
    objects = user.get_departments_by_un_id(int(un_id))
    markup = InlineKeyboardMarkup()
    if objects is not None:
        for obj in objects:
            callback = str(obj[0]) + "_" + 'departments'
            markup.add(InlineKeyboardButton(obj[1], callback_data=callback))

    callback = 'back_from_departments' + '#' + un_id
    markup.add(InlineKeyboardButton('« Назад к университетам', callback_data=callback),
               InlineKeyboardButton('Нет моего факультета', callback_data='request_for_updates'))
    text = "Для этого университета на данный момент *доступны следующие факультеты:*"
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode='Markdown',
                          text=text, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: re.match(r'\d{,}[1-9]_universities', call.data) is not None)
def show_departments(call):
    text = "Для этого университета на данный момент *доступны следующие факультеты:*"
    un_id = int(re.match(r'\d{,}[1-9]', call.data).group())
    bot.answer_callback_query(call.id, "Ответ получен, загружаем данные!")
    markup = get_markup_for_obj('departments', 'un_id', un_id)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode='Markdown',
                          text=text, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: re.match(r'\d{,}[1-9]_departments', call.data) is not None)
def show_directions(call):
    text = "Для этого факультета *доступны следующие направления*\nВыбирете одно из них:"
    un_id = call.message.json['reply_markup']['inline_keyboard'][-1][0]['callback_data'].split('#')[-1]
    dp_id = int(re.match(r'\d{,}[1-9]', call.data).group())
    bot.answer_callback_query(call.id, "Ответ получен, загружаем данные!")
    markup = get_markup_for_obj('directions', 'dp_id', dp_id, un_id)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode='Markdown',
                          text=text, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: re.match(r'\d{,}[1-9]_directions', call.data) is not None)
def show_direction(call):
    dr_id = int(re.match(r'\d{,}[1-9]', call.data).group())
    bot.answer_callback_query(call.id, "Ответ получен, загружаем данные!")
    if user.get_user_type(call.message.chat.id) in config.ACCESS_LEVEL_3:

        ans = user.update_directions(call.message.chat.id, dr_id)
        if ans == 2:
            bot.send_message(call.message.chat.id, text='Вы уже добавили себе это направление')
            text = 'Если вы хотите посмотреть свою позицию по этому направлению\n' \
                   '*Выбирите из выпавшего списка нужное направление*\n' \
                   'Если вы хотите добавить еще направление, просто выбирите его из *списка выше*'
            markup = get_user_directions_keyboard(call.message.chat.id)
            bot.send_message(chat_id=call.message.chat.id, text=text, parse_mode='Markdown', reply_markup=markup)
        elif ans == 1:
            bot.send_message(call.message.chat.id, text='Отлично! Направление добавлено!')
            text = 'Теперь, чтобы посмотреть свою возицию в списке в этом направлении\n' \
                   '*Выбирите из выпавшего списка нужное направление*\n' \
                   'Либо введиьте команду\n/showmydirections\n' \
                   'Если вы хотите добавить еще направление, просто выбирите его из списка выше)'
            markup = get_user_directions_keyboard(call.message.chat.id)
            bot.send_message(chat_id=call.message.chat.id, text=text, reply_markup=markup, parse_mode='Markdown')
        else:
            text = 'Что-то пошло не так....\n' \
                   'Попробуйте повторно выбрать направдение'
            bot.send_message(call.message.chat.id, text=text)
    else:
        # либо заплатить
        text = 'Для того, чтобы добавить это направления, вам необходимо автаризироваться.\n' \
               'Нажмите /register, получить доступ к этой возможности'
        bot.send_message(chat_id=call.message.chat.id, text=text)


@bot.message_handler(commands=['showmydirections'])
def add_university(message):
    if user.get_user_type(message.chat.id) in config.ACCESS_LEVEL_4:

        ans = config.finished_registration(message.chat.id)
        if ans is not None:
            bot.send_message(message.chat.id, text=ans)
        else:
            text = '*Выбирите из выпавшего списка нужное направление.*\n (откройте дополнительную клавиатуру)'
            markup = get_user_directions_keyboard(message.chat.id)
            bot.send_message(chat_id=message.chat.id, text=text, reply_markup=markup, parse_mode='Markdown')
    else:
        text = 'Для того, чтобы посмотреть направления, вам необходимо автаризироваться.\n' \
               'Нажмите /register, получить доступ к этой возможности'
        bot.send_message(chat_id=message.chat.id, text=text)


# ------- show my directions, edit list of my directions --------
def show_user_directions(message):
    ans = config.finished_registration(message.chat.id)
    if user.is_new(message.chat.id) or ans is not None:
        bot.send_message(message.chat.id, text=ans)
    else:
        markup = get_user_directions_keyboard(message.chat.id)
        if markup is not None:
            text = 'Вам доступны следующие направления\n' \
                   'Нажмите на одно из них, чтобы посмотреть свою позицую.'
            bot.send_message(message.chat.id, text=text, reply_markup=markup)
        else:
            text = 'На данный момент у вас *нету ни одного добавленного направления*.\n' \
                   'Введите /showuniversities чтобы добавить его!'
            bot.send_message(message.chat.id, text=text, parse_mode='Markdown')


def _get_choice_text(count, text_msg):
    text = text_msg
    if count == 1:
        text = text.format(str(count) + ' направление')
    elif 0 < count < 5:
        text = text.format(str(count) + ' направления')
    else:
        text = text.format(str(count) + ' направлений')

    return text


def send_directions_edit_list(chat_id, text_btn, text_msg, message_id=None,
                              notify='', clb_btn='delete_', btn1='Отмена', ckb1='not_change_'):
    if clb_btn == 'remove_notify_':
        directions = user.get_notify_directions(chat_id)
    elif clb_btn == 'add_notify_':
        directions = user.get_available_notify_directions(chat_id)
    else:
        directions = user.get_all_user_directions(chat_id)
    markup = InlineKeyboardMarkup()
    for direction in directions:
        text = "{}. {}. {}".format(direction[0], direction[1], direction[2])
        callback = notify+"{}_direction".format(direction[3])
        markup.add(InlineKeyboardButton(text=text, callback_data=callback))
    markup.add(InlineKeyboardButton(text=text_btn, callback_data=clb_btn+'directions'))
    markup.add(InlineKeyboardButton(text=btn1, callback_data=ckb1+'directions'))
    if message_id is not None:
        bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                              text=text_msg, reply_markup=markup, parse_mode='Markdown')
    else:
        bot.send_message(chat_id=chat_id, text=text_msg, reply_markup=markup, parse_mode='Markdown')


def send_marked_direction_list(call, text_msg):
    markup = InlineKeyboardMarkup()
    count = 0
    for obj in call.message.json['reply_markup']['inline_keyboard']:
        if call.data == obj[0]['callback_data']:
            text = '✔️' + obj[0]['text']
            callback = 'mark_' + obj[0]['callback_data']
            count += 1
            markup.add(InlineKeyboardButton(text=text, callback_data=callback))

        else:
            markup.add(InlineKeyboardButton(text=obj[0]['text'], callback_data=obj[0]['callback_data']))

        if 'mark' == obj[0]['callback_data'][:4]:
            count += 1

    text = _get_choice_text(count, text_msg)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=text, reply_markup=markup, parse_mode='Markdown')


def send_unmarked_direction_lis(call, text_msg):
    markup = InlineKeyboardMarkup()
    count = 0
    for obj in call.message.json['reply_markup']['inline_keyboard']:
        if call.data == obj[0]['callback_data']:
            text = obj[0]['text'][1:]
            callback = obj[0]['callback_data'][5:]
            count -= 1
            markup.add(InlineKeyboardButton(text=text, callback_data=callback))
        else:
            markup.add(InlineKeyboardButton(text=obj[0]['text'], callback_data=obj[0]['callback_data']))
        if 'mark' == obj[0]['callback_data'][:4]:
            count += 1

    text = _get_choice_text(count, text_msg)
    bot.edit_message_text(chat_id=call.message.chat.id, text=text, message_id=call.message.message_id,
                          reply_markup=markup, parse_mode='Markdown')


@bot.message_handler(func=lambda message: config.direction_filter(message.text))
def get_direction_info(message):
    if user.get_user_type(message.chat.id) in config.ACCESS_LEVEL_3:
        ans = config.finished_registration(message.chat.id)
        if user.is_new(message.chat.id) or ans is not None:
            bot.send_message(message.chat.id, text=ans)
        else:
            a, b, c = message.text.split('. ')
            info = get_direction_data(a, b, c, message.chat.id)
            if info is not None:
                bot.send_message(chat_id=message.chat.id, text=info[0], parse_mode='Markdown')
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton('Откыть сайт', url=info[2], callback_data='open_site'))
                bot.send_message(chat_id=message.chat.id, text=info[1], parse_mode='Markdown', reply_markup=markup)
            else:
                text = 'Вероятно что-то пошло не так, попробуйте повторить запрос'
                bot.send_message(message.chat.id, text=text)
    else:
        # либо заплатить
        text = 'Для того, чтобы посмотреть это направление, вам необходимо автаризироваться.\n' \
               'Нажмите /register, получить доступ к этой возможности'
        bot.send_message(chat_id=message.chat.id, text=text)


@bot.message_handler(commands=['editdirections'])
def edit_directions(message):
    if user.get_user_type(message.chat.id) in config.ACCESS_LEVEL_4:

        ans = config.finished_registration(message.chat.id)
        if user.is_new(message.chat.id) or ans is not None:
            bot.send_message(message.chat.id, text=ans)
        else:
            text_btn = 'Удалить🗑'
            text_msg = "Выбирете те направления из списка, которые хотите удалить\nЗатем нажмите *Удалить*"
            send_directions_edit_list(message.chat.id, text_btn, text_msg)
    else:
        text = 'Для того, чтобы редактировать направления, вам необходимо автаризироваться.\n' \
               'Нажмите /register, получить доступ к этой возможности'
        bot.send_message(chat_id=message.chat.id, text=text)


@bot.callback_query_handler(func=lambda call: re.match(r'\d{,}[1-9]_direction', call.data) is not None)
def mark_direction(call):
    bot.answer_callback_query(call.id, "Изменения сохранены!")
    text_msg = "*Вы выбралий {}*\nНажмите *Удалить* чтобы избавиться от них"
    send_marked_direction_list(call, text_msg)


@bot.callback_query_handler(func=lambda call: re.match(r'mark_\d{,}[1-9]_direction', call.data) is not None)
def unmark_direction(call):
    bot.answer_callback_query(call.id, "Изменения сохранены!")
    text_msg = "*Вы выбралий {}*\nНажмите *Удалить* чтобы избавиться от них"
    send_unmarked_direction_lis(call, text_msg)


@bot.callback_query_handler(func=lambda call: call.data == 'delete_directions')
def delete_directions(call):
    count = 0
    directions = []
    for obj in call.message.json['reply_markup']['inline_keyboard']:
        if 'mark' == obj[0]['callback_data'][:4]:
            dr_id = obj[0]['callback_data'].split('_')[1]
            directions.append(int(dr_id))

        if 'mark' == obj[0]['callback_data'][:4]:
            count += 1

    if user.delete_directions(call.message.chat.id, directions):
        bot.answer_callback_query(call.id, "Изменения сохранены!")
        text_msg = "*Вы удалили {}*\nВведите /showmydirections, чтобы посмотреть обновленный список"
        text = _get_choice_text(count, text_msg)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=text, parse_mode='Markdown')
    else:
        bot.answer_callback_query(call.id, "Ошибка..")
        text = 'Произошла какая-то ошибка при удалении данных...\n' \
               'Попробуйте повторить опирацию /editdirections'
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text)


@bot.callback_query_handler(func=lambda call: call.data == 'not_change_directions')
def not_change_directions(call):
    text = "Редактирование отменино"
    bot.edit_message_text(chat_id=call.message.chat.id, text=text, message_id=call.message.message_id)


# ------- add to waiting for updates--------
@bot.callback_query_handler(func=lambda call: call.data == 'request_for_updates')
def add_waiting(call):
    text = 'Напишите, пожайлуста, ваш *университет/факультет/направление*, которое вы не нашли\n' \
           'Мы приносим прощения и обещаем добаить его в течении 2-ух дней!\n' \
           '*Как только мы добавми его Вам придет уведомление!*'
    dbworker.set_state(call.message.chat.id, config.States.S_PROBLEM.value)
    bot.send_message(chat_id=call.message.chat.id, text=text, parse_mode='Markdown')


@bot.message_handler(func=lambda message: config.problem_filter(message.chat.id))
def get_direction_info(message):
    if user.save_user_problem(message.chat.id, message.text):
        text = 'Спасибо, что поделились этой проблемой!\n' \
               'Мы обязательно исправим все в ближйшее время!'
    else:
        text = 'Ooopss..\n' \
               'Возникли какие-то проблемы\n' \
               'Попробуйте ввести еще раз, или повторите попытку позже'

    dbworker.set_state(message.chat.id, config.States.S_START.value)
    bot.send_message(chat_id=message.chat.id, text=text, parse_mode='Markdown')


# ------- reviews --------
def ask_service_review(chat_id, text=None):
    text = 'Как вам сервис, раскажите?\n' \
           'Нам помогает это становиться лучше!'
    markup = InlineKeyboardMarkup()

    icons = ['0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣']
    data = ()
    for i in range(len(icons)):
        data += (InlineKeyboardButton(text=icons[i], callback_data='star_' + str(i)),)
    markup.row(*data)
    bot.send_message(chat_id, text, reply_markup=markup)


# as a begin
@bot.message_handler(commands=['addreview'])
def get_direction_info(message):
    if user.get_user_type(message.chat.id) in config.ACCESS_LEVEL_4:
        ask_service_review(message.chat.id)
    else:
        text = 'Простите, у вас нету прав доступа к этой функции\n' \
               'Пройдите идентификацию чтобы получить доступ к этой функции.\n/register'
        bot.send_message(chat_id=message.chat.id, text=text)


@bot.callback_query_handler(func=lambda call: re.match(r'star_[0-9]', call.data) is not None)
def add_mark(call):
    mark = int(call.data.split('_')[1])

    count = -1
    for obj in call.message.json['reply_markup']['inline_keyboard'][0]:
        if obj['text'] == '👍':
            count += 1

    if not mark == count:
        markup = InlineKeyboardMarkup()
        icons = ['0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣']
        data = ()
        for i in range(len(icons)):
            if i <= mark:
                data += (InlineKeyboardButton(text='👍', callback_data='star_' + str(i)),)
            else:
                data += (InlineKeyboardButton(text=icons[i], callback_data='star_' + str(i)),)

        markup.row(*data)
        markup.add(InlineKeyboardButton(text='Сохранить', callback_data='save_review'))
        markup.add(InlineKeyboardButton(text='Написать текстовый отзыв', callback_data='write_review'))

        bot.edit_message_text(chat_id=call.message.chat.id, text='Вы поставили оценку {}/7'.format(mark),
                              message_id=call.message.message_id, reply_markup=markup)

    if user.save_review(call.message.chat.id, mark=mark):
        bot.answer_callback_query(call.id, 'Данные успешно получены!')


@bot.callback_query_handler(func=lambda call: call.data == 'save_review')
def save_rev(call):
    text = 'Спасибо, что поделились!\n' \
           'Мы обязательно учтем ваше мнение!'
    bot.edit_message_text(chat_id=call.message.chat.id, text=text, message_id=call.message.message_id)


@bot.callback_query_handler(func=lambda call: call.data == 'write_review')
def add_writing(call):
    text = 'Пожайлуста, напишите а затем отправте мне ваш отзыв'
    dbworker.set_state(call.message.chat.id, config.States.S_REVIEW.value)
    bot.edit_message_text(chat_id=call.message.chat.id, text=text,
                          message_id=call.message.message_id, parse_mode='Markdown')


@bot.message_handler(func=lambda message: config.review_filter(message.chat.id))
def save_review(message):
    if user.save_review(chat_id=message.chat.id, text=message.text):
        text = 'Спасибо, что поделились!\n' \
               'Мы обязательно учтем ваше мнение!'
    else:
        text = 'Oooppss..\n' \
               'Возникли какие-то проблемы\n' \
               'Попробуйте ввести еще раз, или повторите попытку позже'

    dbworker.set_state(message.chat.id, config.States.S_START.value)
    bot.send_message(chat_id=message.chat.id, text=text)


# ------- menage subscribe --------
def get_notify_direction_text(call):
    bot.answer_callback_query(call.id, "Изменения сохранены!")
    if call.message.json['reply_markup']['inline_keyboard'][-1][0]['callback_data'] == 'add_notify_directions':
        text_msg = "*Вы выбралий {}*\nНажмите *Добавить* чтобы подписаться на обновления от них"
    else:
        text_msg = "*Вы выбралий {}*\nНажмите *Удалить* чтобы не получать больше уведомления от них"

    return text_msg


def manage_directions_notify(call, text_msg, action):
    count = 0
    names = []
    for obj in call.message.json['reply_markup']['inline_keyboard']:
        if 'mark' == obj[0]['callback_data'][:4]:
            name = obj[0]['text'][2:]
            print(name)
            names.append(name)
            count += 1

    if count == 0:
        bot.answer_callback_query(call.id, "Ошибка.. Вы не можете удалить пустоту")
    elif user.manage_directions_notify(call.message.chat.id, names, action):
        bot.answer_callback_query(call.id, "Изменения сохранены!")
        text = _get_choice_text(count, text_msg)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=text, parse_mode='Markdown')
    else:
        bot.answer_callback_query(call.id, "Ошибка..")
        text = 'Произошла какая-то ошибка при изменении данных...\n' \
               'Попробуйте повторить опирацию /managesubscribe'
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text)


@bot.message_handler(commands=['managesubscribe'])
def subscribe(message):
    if user.get_user_type(message.chat.id) in config.ACCESS_LEVEL_2:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(text='Подписаться на обнавления', callback_data='add_subscription'))
        markup.add(InlineKeyboardButton(text='Отменить подписку', callback_data='remove_subscription'))

        text = 'Я могу уведомлять вас об изменениях вашей позиции в рейтинговом списке вашего направления\n' \
               'Выберите _Подписаться на обнавления_ чтобы настроить уведомления\n' \
               'Если вам не нужны уведомления из некоторых направлений, просто удалите их, выбрав _Отменить подписку_'
        bot.send_message(chat_id=message.chat.id, text=text, reply_markup=markup, parse_mode='Markdown')

    else:
        text = 'Простите, у вас нету прав доступа для использования этой функции\n' \
               'Пройдите идентификацию (если еще нет), либо оформите подписку на сервис, для доступа к этой функции.'
        bot.send_message(chat_id=message.chat.id, text=text)


@bot.callback_query_handler(func=lambda call: call.data == 'notify_back_directions')
def notify_back_directions(call):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text='Подписаться на обнавления', callback_data='add_subscription'))
    markup.add(InlineKeyboardButton(text='Отменить подписку', callback_data='remove_subscription'))

    text = 'Я могу уведомлять вас об изменениях вашей позиции в рейтинговом списке вашего направления\n' \
            'Выберите _Подписаться на обнавления_ чтобы настроить уведомления\n' \
            'Если вам не нужны уведомления из некоторых направлений, просто удалите их, выбрав _Отменить подписку_'
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=text, reply_markup=markup, parse_mode='Markdown')


@bot.callback_query_handler(func=lambda call: call.data == 'add_subscription')
def add_subscription(call):
    text_btn = 'Добавить✍️'
    text_msg = "Выбирете те направления из списка, по которым вы хотите получать уведомления\nЗатем нажмите *Добавить*"
    send_directions_edit_list(call.message.chat.id, text_btn, text_msg, call.message.message_id,
                              'notify_', 'add_notify_', 'Назад', 'notify_back_')


@bot.callback_query_handler(func=lambda call: call.data == 'remove_subscription')
def remove_subscription(call):
    text_btn = 'Удалить🗑'
    text_msg = "Выбирете те направления из списка, по которым не хотите получать уведомления\nЗатем нажмите *Удалить*"
    send_directions_edit_list(call.message.chat.id, text_btn, text_msg, call.message.message_id,
                              'notify_', 'remove_notify_', 'Назад', 'notify_back_')


@bot.callback_query_handler(func=lambda call: re.match(r'notify_\d{,}[1-9]_direction', call.data) is not None)
def mark_direction(call):
    text_msg = get_notify_direction_text(call)
    send_marked_direction_list(call, text_msg)


@bot.callback_query_handler(func=lambda call: re.match(r'mark_notify_\d{,}[1-9]_direction', call.data) is not None)
def unmark_direction(call):
    text_msg = get_notify_direction_text(call)
    send_unmarked_direction_lis(call, text_msg)


@bot.callback_query_handler(func=lambda call: call.data == 'remove_notify_directions')
def remove_notify_directions(call):
    text_msg = "*Вы убрали из рассылки {}*\n"
    action = 'delete'
    manage_directions_notify(call, text_msg, action)


@bot.callback_query_handler(func=lambda call: call.data == 'add_notify_directions')
def add_notify_directions(call):
    text_msg = "*Вы подписались на {}*\n"
    action = 'add'
    manage_directions_notify(call, text_msg, action)



bot.infinity_polling()

