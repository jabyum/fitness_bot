import threading
from datetime import datetime, timedelta
import pytz
import sqlite3
from telebot.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from telebot import apihelper

import schedule
import time
from ..loader import bot


def get_cursor():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    return conn, cursor


@bot.callback_query_handler(func=lambda call: call.data == 'continueafteremiind')
def test_state(call: CallbackQuery):
    try:
        user_id = call.from_user.id
        chat_id = call.message.chat.id
        conn, cursor = get_cursor()
        cursor.execute("SELECT last_bot_message_id, last_bot_message_type FROM Users WHERE user_id = ?", [user_id])
        result = cursor.fetchone()
        mess_id = result[0]
        message_type = result[1]

        if mess_id:
            if message_type == 'voice':
                markup = InlineKeyboardMarkup()
                button1 = InlineKeyboardButton(text='Погнали!', callback_data='Go!')
                markup.add(button1)
                bot.copy_message(chat_id, chat_id, mess_id, reply_markup=markup)
            else:
                bot.copy_message(chat_id, chat_id, mess_id)
        else:
            bot.send_message(chat_id, f"Нет последнего сообщения")
    except Exception as E:
        bot.send_message(305896408, f'Ошибка: {E}')


def check_unfinished_users():
    conn, cursor = get_cursor()
    now = datetime.now()
    try:
        cursor.execute('SELECT user_id, last_interaction_time, notified FROM Users WHERE phone IS NULL')
        for user_id, last_interaction_time, notified in cursor.fetchall():
            if last_interaction_time is not None:
                last_interaction_time = datetime.strptime(last_interaction_time, '%Y-%m-%d %H:%M:%S')
                if (now - last_interaction_time > timedelta(minutes=3) and notified == 0) or \
                    (now - last_interaction_time > timedelta(minutes=15) and notified == 1):
                    markup = InlineKeyboardMarkup()
                    button1 = InlineKeyboardButton(text='Продолжить!', callback_data='continueafteremiind')
                    markup.add(button1)
                    if now - last_interaction_time > timedelta(minutes=3) and notified == 0:
                        official_photo0 = 'AgACAgIAAxkBAAICV2SIgoutZLFnVveTMW74rf1Cq1RwAAIUxzEbHdtBSMUWHDZ--IkjAQADAgADeQADLwQ'
                        bot.send_photo(chat_id=user_id,
                                       photo=official_photo0,
                                       caption="*Упс, кажется вы отвлеклись...*\n\n"
                                               "Чтобы продолжить, нажмите на кнопку снизу👇",
                                       reply_markup=markup, parse_mode='Markdown')
                    elif now - last_interaction_time > timedelta(minutes=15) and notified == 1:
                        official_photo = 'AgACAgIAAxkBAAICb2SIjMrh9wd3YwSuMvcBI0_bfW-MAAJwxzEbHdtBSAPISViAFsjUAQADAgADeQADLwQ'

                        bot.send_photo(chat_id=user_id,
                                       photo=official_photo,
                                       caption="📞 *Вы здесь?* Не стала вас отвлекать, подумала что вы заняты...\n\n"
                                               "Вы не заполнили форму до конца, а заявки Ибрат получит "
                                               "*после прохождения всех этапов.*\n\nЧтобы заполнить форму до конца, "
                                               "нажмите на кнопку 👇",
                                       reply_markup=markup, parse_mode='Markdown')
                    cursor.execute('UPDATE Users SET last_interaction_time = ?, '
                                   'notified = ? WHERE user_id = ?',
                                   [now.strftime('%Y-%m-%d %H:%M:%S'), notified + 1, user_id])

        cursor.execute('SELECT user_id, last_interaction_time, notified FROM Users WHERE phone IS NOT NULL')
        for user_id, last_interaction_time, notified in cursor.fetchall():
            if last_interaction_time is not None:
                last_interaction_time = datetime.strptime(last_interaction_time, '%Y-%m-%d %H:%M:%S')
                if (now - last_interaction_time > timedelta(minutes=3) and notified == 0) or \
                    (now - last_interaction_time > timedelta(minutes=15) and notified == 1):
                    markup = InlineKeyboardMarkup()
                    button1 = InlineKeyboardButton(text='Продолжить!', callback_data='continueafteremiind')
                    markup.add(button1)
                    if now - last_interaction_time > timedelta(minutes=3) and notified == 0:
                        bot.send_photo(chat_id=user_id,
                                       photo='AgACAgIAAxkBAAICV2SIgoutZLFnVveTM'
                                             'W74rf1Cq1RwAAIUxzEbHdtBSMUWHDZ--IkjAQADAgADeQADLwQ',
                                       caption="*Упс, кажется вы отвлеклись...*\n\n"
                                               "Чтобы продолжить, нажмите на кнопку снизу👇",
                                       reply_markup=markup, parse_mode='Markdown')
                    elif now - last_interaction_time > timedelta(minutes=15) and notified == 1:
                        cursor.execute('SELECT username, name, phone FROM Users WHERE user_id = ?', [user_id,])
                        user_data = cursor.fetchone()
                        print(user_data)
                        '''('Grasmurr', 'хелоу', '79670282821')
                        (None, 'хелоу', '79774563501')'''
                        username = user_data[0] if user_data[0] is not None else "Отсутствует"
                        text = f"🧾 Босс! Пользователь не дошел до конца:\n\n" \
                               f"*Имя:* {user_data[1]}\n" \
                               f"*Телефон:* +{user_data[2]}\n" \
                               f"*Username:* @{username}" \
                               f"\n\nРада была помочь!\nС любовью, Лиза❣️"
                        bot.send_message(chat_id=58790442, text=text, parse_mode='Markdown')
                    cursor.execute('UPDATE Users SET last_interaction_time = ?, '
                                   'notified = ? WHERE user_id = ?',
                                   [now.strftime('%Y-%m-%d %H:%M:%S'), notified + 1, user_id])

    except apihelper.ApiException as e:
        error_code = e.result.status_code
        if error_code == 403:
            bot.send_message(305896408, f"User {user_id} blocked the bot. Removing from the database.")
            cursor.execute('DELETE FROM Users WHERE user_id = ?', [user_id])
        else:
            bot.send_message(305896408, f"Error {error_code}: {e.result.reason}")

    except Exception as E:
        bot.send_message(305896408, f'Ошибка: {E}')
    conn.commit()


# def check_phoneless_users():
#     conn, cursor = get_cursor()
#     if datetime.now().weekday() == 0:
#         cursor.execute('SELECT user_id FROM Users WHERE phone IS NULL')
#         for user_id in cursor.fetchall():
#             bot.send_message(user_id[0],
#                              "Вы не указали свой телефон при регистрации. "
#                              "Пожалуйста, дополните информацию в анкете.")



