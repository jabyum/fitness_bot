from ..loader import bot
from telebot.types import Message, ReplyKeyboardMarkup, KeyboardButton


@bot.message_handler(commands=['start'])
def start_message(message: Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = KeyboardButton('Задать вопрос')
    markup.add(button1)
    bot.send_message(chat_id=message.chat.id, text='Привет! Это бот-техподдержка от курса 21 x fit!',
                     reply_markup=markup)