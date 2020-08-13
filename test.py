import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
TOKEN = '1232696304:AAHjcTwO3oelfj6fWAmg1pcADKG081jlqpY'

bot = telebot.TeleBot(TOKEN)



@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "cb_yes":
        bot.answer_callback_query(call.id, "Answer is Yes")
    elif call.data == "cb_no":
        bot.answer_callback_query(call.id, "Answer is No")


@bot.message_handler(func=lambda message: True)
def message_handler(message):
    # or add KeyboardButton one row at a time:
    markup = types.ReplyKeyboardMarkup()
    objs = []
    for i in range(1, 10):
        markup.add(types.KeyboardButton('a'*i))

    # markup.add(objs)
    bot.send_message(message.chat.id, "Choose one letter:", reply_markup=markup)


bot.infinity_polling()
