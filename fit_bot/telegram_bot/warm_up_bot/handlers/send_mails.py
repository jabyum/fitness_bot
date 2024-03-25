from ..loader import bot
from telebot.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup,\
    InlineKeyboardButton
from telebot.handler_backends import State, StatesGroup
from telebot.storage import memory_storage
from telebot.types import CallbackQuery
from telebot import custom_filters
import sqlite3
from datetime import datetime
import os

ADMINS = [305896408, 58790442]


mailing_content = {}


class MailingStates(StatesGroup):
    choose_type = State()
    continue_sending = State()
    initial = State()


def get_id(message):
    return message.from_user.id, message.chat.id


def error_message(message: Message):
    bot.send_message(message.from_user.id, 'Кажется, вы ввели что-то не то, нажмите /mail')


def get_cursor():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    return conn, cursor


def send_mailing(telegram_bot, content, is_photo=False):
    conn, cursor = get_cursor()
    cursor.execute('SELECT user_id FROM Users')
    for user_id, in cursor.fetchall():
        if is_photo:
            bot.send_photo(chat_id=user_id, photo=mailing_content['photo'], caption=mailing_content['caption'])
        else:
            bot.send_message(chat_id=user_id, text=mailing_content['text'])
    conn.commit()


@bot.message_handler(commands=['mail'], func=lambda message: message.from_user.id in ADMINS)
def mail_users(message: Message):
    user_id, chat_id = get_id(message)

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = KeyboardButton('Фото')
    button2 = KeyboardButton('Текст')

    markup.add(button1)
    markup.add(button2)

    bot.send_message(user_id, text='Хорошо, выберите вид сообщения для пользователей:', reply_markup=markup)
    bot.set_state(user_id, MailingStates.choose_type, chat_id)


@bot.message_handler(state=MailingStates.choose_type)
def types_of_mailings(message: Message):
    user_id, chat_id = get_id(message)

    mailing_type = message.text

    if mailing_type == 'Фото':
        bot.send_message(user_id, 'Хорошо! пришлите фото, которое вы собираетесь разослать по пользователям:'
                                  ' (Если хотите чтобы фото было с подписью, подпишите фото при отправке)')
        bot.set_state(user_id, MailingStates.continue_sending, chat_id)
    elif mailing_type == 'Текст':
        bot.send_message(user_id, 'Хорошо! пришлите текст, которое вы собираетесь разослать по пользователям:')
        bot.set_state(user_id, MailingStates.continue_sending, chat_id)
    else:
        error_message(message)


@bot.message_handler(state=MailingStates.continue_sending, content_types=['photo'])
def handle_photo_mail(message: Message):
    file_id = message.photo[-1].file_id
    caption = message.caption
    mailing_content['photo'] = file_id
    mailing_content['caption'] = caption

    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("Продолжить", callback_data="continue"),
               InlineKeyboardButton("Отмена", callback_data="cancel"))

    bot.send_photo(chat_id=message.chat.id, photo=file_id, reply_markup=markup,
                   caption=f"Хорошо, я сохранил фото в облако. Подпись к нему: {caption if caption else 'без подписи'}")


@bot.message_handler(state=MailingStates.continue_sending, content_types=['text'])
def handle_text_mail(message: Message):
    text = message.text
    mailing_content['text'] = text

    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("Продолжить", callback_data="continue"),
               InlineKeyboardButton("Отмена", callback_data="cancel"))

    bot.send_message(chat_id=message.chat.id, reply_markup=markup,
                     text=f"Хорошо, я сохранил ваше сообщение: {text}")


@bot.callback_query_handler(func=lambda call: True, state=MailingStates.continue_sending)
def callback_query(call):
    if call.data == "continue":
        user_id, chat_id = get_id(call.message)
        conn, cursor = get_cursor()
        cursor.execute('SELECT user_id FROM Users')
        users = cursor.fetchall()
        for user in users:
            if 'photo' in mailing_content:
                bot.send_photo(chat_id=user[0], photo=mailing_content['photo'],
                               caption=mailing_content['caption'])
            elif 'text' in mailing_content:
                bot.send_message(chat_id=user[0], text=mailing_content['text'])
        mailing_content.clear()
        bot.delete_message(chat_id=chat_id, message_id=call.message.message_id)
        bot.send_message(chat_id=chat_id, text='Рассылка выполнена. Для того, чтобы сделать еще одну, нажмите /mail',
                         reply_markup=ReplyKeyboardRemove())
        bot.set_state(user_id, MailingStates.initial, chat_id)
    elif call.data == "cancel":
        user_id, chat_id = get_id(call.message)
        bot.delete_message(chat_id=chat_id, message_id=call.message.message_id)
        bot.send_message(chat_id=chat_id, text='Операция отменена. Для того, чтобы сделать рассылку, нажмите /mail',
                         reply_markup=ReplyKeyboardRemove())
        bot.set_state(user_id, MailingStates.initial, chat_id)


