from ..loader import bot
from telebot.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, \
    InlineKeyboardButton
from telebot.handler_backends import State, StatesGroup
from telebot.storage import memory_storage
from telebot.types import CallbackQuery
from telebot import custom_filters
import sqlite3
from datetime import datetime
import os


class States(StatesGroup):
    START = State()
    enter_name = State()
    confirm_name = State()
    enter_phone = State()
    enter_age = State()
    enter_gender = State()
    enter_weight = State()
    enter_height = State()
    enter_activity_level = State()
    describe_problem = State()
    ask_place = State()


def get_id(message):
    return message.from_user.id, message.chat.id


def get_cursor():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    return conn, cursor


ADMINS = [305896408, 58790442]


@bot.message_handler(commands=['start'])
def start_message(message: Message):
    try:
        conn, cursor = get_cursor()
        user_id, chat_id = get_id(message)
        cursor.execute('INSERT OR IGNORE INTO Users (user_id, username, last_interaction_time)'
                       ' VALUES (?, ?, ?)',
                       [user_id, message.from_user.username, datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        conn.commit()
        bot.set_state(user_id, States.enter_name, chat_id)

        official_photo = 'AgACAgIAAxkBAAMbZIICG7vmPW-HF4upkh_vcE8ow-EAAjHLMRu1rxFIeBaekTZNgEABAAMCAAN5AAMvBA'

        test_photo = 'AgACAgIAAxkBAAIGR2Sv1Uk93knxY0H7wKfepuWuqQYHAAIcyjEbIj6ASRetg2wa3ugqAQADAgADeQADLwQ'

        sent_message = bot.send_photo(user_id,
                                      photo=official_photo,
                                      caption=f'👋 Привет, меня зовут Лиза\n\n'
                                              f'Я - виртуальный ассистент Ибрата, '
                                              f'готова принять вашу заявку на личную диагностику!\n\n'
                                              f'👀 *Кстати, как к вам обращаться?*\n\n'
                                              f'(Введите свое имя)', reply_markup=ReplyKeyboardRemove(),
                                      parse_mode='Markdown')
        cursor.execute('UPDATE Users SET last_bot_message_id = ?, last_bot_message_type = ? WHERE user_id = ?',
                       [sent_message.message_id, 'photo', user_id])
        conn.commit()
    except Exception as E:
        bot.send_message(305896408, f'Ошибка! {E}')


@bot.message_handler(state=States.enter_name)
def get_name(message: Message):
    try:
        user_id, chat_id = get_id(message)
        conn, cursor = get_cursor()
        name = message.text
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('UPDATE Users SET last_interaction_time = ?, name = ? WHERE user_id = ?',
                       [now, name, user_id])
        conn.commit()
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = KeyboardButton('Отправить телефон', request_contact=True)
        markup.row(button1)
        text = f'*Приятно познакомиться, {name} ❣️*\n\n' \
               'А теперь поделитесь, пожалуйста, *своим номером телефона*, чтобы Ибрат мог лично с вами связаться!\n\n' \
               '(Жмите на кнопку в меню)'

        official_photo = 'AgACAgIAAxkBAAMeZIICMjDIy9mEldb9Joai0xPTt9sAAjLLMRu1rxFIjQX2LKMoskkBAAMCAAN5AAMvBA'
        test_photo = 'AgACAgIAAxkBAAIGVWSv1cFu58hHJdZl8cjMjH9da9SDAAIeyjEbIj6ASVLJQRLgg1q5AQADAgADeQADLwQ'

        sent_message = bot.send_photo(user_id,
                                      photo=official_photo,
                                      caption=text,
                                      reply_markup=markup, parse_mode='Markdown')
        cursor.execute('UPDATE Users SET last_bot_message_id = ?, last_bot_message_type = ? WHERE user_id = ?',
                       [sent_message.message_id, 'photo', user_id])
        conn.commit()
        bot.set_state(user_id, States.enter_phone, chat_id)
    except Exception as E:
        bot.send_message(305896408, f'Ошибка! {E}')


@bot.message_handler(state=States.enter_phone, content_types=['contact'])
def get_age(message: Message):
    try:
        markup = ReplyKeyboardMarkup()
        ReplyKeyboardRemove()
        user_id, chat_id = get_id(message)
        conn, cursor = get_cursor()
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if message.contact is not None:
            number = message.contact.phone_number
            cursor.execute('UPDATE Users SET last_interaction_time = ?, phone = ? WHERE user_id = ?',
                           [now, number, user_id])
            conn.commit()
            sent_message = bot.send_message(text='📞🔥 Ибрат на связи, скорее слушайте аудио!', chat_id=chat_id,
                                            reply_markup=ReplyKeyboardRemove())
            cursor.execute('UPDATE Users SET last_bot_message_id = ? WHERE user_id = ?', [sent_message.message_id, user_id])
            conn.commit()
            markup = InlineKeyboardMarkup()
            button1 = InlineKeyboardButton(text='Погнали!', callback_data='Go!')
            markup.add(button1)

            official_voice = 'AwACAgIAAxkBAAMxZIIFR-7JoIy9uE1RX4AYTdcsEYUAAkMsAALdyQABSEj14zqmpCufLwQ'
            test_voice = 'AwACAgIAAxkBAAIGX2Sv1v9RRi84ysKVeLX4MZ5GvvngAAJDLAAC3ckAAUg2ON27vliZXC8E'

            sent_message = bot.send_voice(chat_id,
                                          voice=official_voice,
                                          reply_markup=markup)
            cursor.execute('UPDATE Users SET last_bot_message_id = ?, last_bot_message_type = ? WHERE user_id = ?',
                           [sent_message.message_id, 'voice', user_id])
            conn.commit()

        else:
            sent_message = bot.send_message(user_id, 'Кажется, что-то пошло не так. Попробуйте нажать на кнопку ниже')
            cursor.execute('UPDATE Users SET last_bot_message_id = ?, last_bot_message_type = ? WHERE user_id = ?',
                           [sent_message.message_id, 'text', user_id])
            conn.commit()
    except Exception as E:
        bot.send_message(305896408, f'Ошибка! {E}')


@bot.callback_query_handler(state=States.enter_phone, func=lambda call: call.data == 'Go!')
def start_test(call: CallbackQuery):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    conn, cursor = get_cursor()
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = KeyboardButton('М')
    button2 = KeyboardButton('Ж')
    markup.row(button1, button2)
    sent_message = bot.send_message(user_id, '📌 *Укажите ваш пол:*\n\nМ/Ж:', reply_markup=markup, parse_mode='Markdown')
    cursor.execute('UPDATE Users SET last_bot_message_id = ?, last_bot_message_type = ? WHERE user_id = ?',
                   [sent_message.message_id, 'text', user_id])
    conn.commit()
    bot.set_state(user_id, States.enter_gender, chat_id)


@bot.message_handler(state=States.enter_gender)
def get_gender(message: Message):
    try:
        user_id, chat_id = get_id(message)
        conn, cursor = get_cursor()
        text = message.text.lower()
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if text in ['м', 'ж']:
            gender = text
            cursor.execute('UPDATE Users SET last_interaction_time = ?, gender = ? WHERE user_id = ?',
                           [now, gender, user_id])
            conn.commit()
            sent_message = bot.send_message(user_id, '📌 *Укажите ваш возраст:*\n\n'
                                                     '(Только цифру):', reply_markup=ReplyKeyboardRemove(),
                                            parse_mode='Markdown')
            cursor.execute('UPDATE Users SET last_bot_message_id = ?, last_bot_message_type = ? WHERE user_id = ?',
                           [sent_message.message_id, 'text', user_id])
            conn.commit()

            bot.set_state(user_id, States.enter_age, chat_id)
        else:
            sent_message = bot.send_message(user_id, 'Пожалуйста, введите корректный пол (М/Ж).')
            cursor.execute('UPDATE Users SET last_bot_message_id = ?, last_bot_message_type = ? WHERE user_id = ?',
                           [sent_message.message_id, 'text', user_id])
            conn.commit()
    except Exception as E:
        bot.send_message(305896408, f'Ошибка! {E}')


@bot.message_handler(state=States.enter_age)
def get_gender(message: Message):
    try:
        conn, cursor = get_cursor()
        user_id, chat_id = get_id(message)
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        age = message.text

        if age.isdigit() and 13 < int(age) < 71:
            cursor.execute('UPDATE Users SET last_interaction_time = ?, age = ? WHERE user_id = ?',
                           [now, int(age), user_id])
            conn.commit()
            sent_message = bot.send_message(user_id, '📌 *Укажите ваш вес:*\n\n(Только цифру в кг):',
                                            reply_markup=ReplyKeyboardRemove(), parse_mode='Markdown')
            cursor.execute('UPDATE Users SET last_bot_message_id = ?, last_bot_message_type = ? WHERE user_id = ?',
                           [sent_message.message_id, 'text', user_id])
            conn.commit()

            bot.set_state(user_id, States.enter_weight, chat_id)
        else:
            sent_message = bot.send_message(user_id, 'Пожалуйста, введите корректный возраст '
                                                     '(только цифру от 14 до 70).')
            cursor.execute('UPDATE Users SET last_bot_message_id = ?, last_bot_message_type = ? WHERE user_id = ?',
                           [sent_message.message_id, 'text', user_id])
            conn.commit()
    except Exception as E:
        bot.send_message(305896408, f'Ошибка! {E}')


@bot.message_handler(state=States.enter_weight)
def get_weight(message: Message):
    try:
        conn, cursor = get_cursor()
        user_id, chat_id = get_id(message)
        text = message.text
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if text.isdigit() and 29 < int(text) < 251:
            weight = int(text)
            cursor.execute('UPDATE Users SET last_interaction_time = ?, weight = ? WHERE user_id = ?',
                           [now, weight, user_id])
            conn.commit()
            sent_message = bot.send_message(user_id, '📌 *Укажите ваш рост:*\n\n(Только цифру в см):',
                                            reply_markup=ReplyKeyboardRemove(), parse_mode='Markdown')
            cursor.execute('UPDATE Users SET last_bot_message_id = ?, last_bot_message_type = ? WHERE user_id = ?',
                           [sent_message.message_id, 'text', user_id])
            conn.commit()

            bot.set_state(user_id, States.enter_height, chat_id)
        else:
            sent_message = bot.send_message(user_id, 'Пожалуйста, введите корректный вес от 30 до 250 (целое число).')
            cursor.execute('UPDATE Users SET last_bot_message_id = ?, last_bot_message_type = ? WHERE user_id = ?',
                           [sent_message.message_id, 'text', user_id])
            conn.commit()
    except Exception as E:
        bot.send_message(305896408, f'Ошибка! {E}')


activity_levels = {1: 'Малоподвижный образ жизни (тренировок нет / тренируюсь очень редко)',
                   2: 'Небольшая активность (1-3 тренировки в неделю)',
                   3: 'Умеренная активность (3-5 тренировок в неделю)',
                   4: 'Высокая активность (6-7 тренировок в неделю)',
                   5: 'Очень высокая активность (тяжелые тренировки 6-7 дней в неделю)'}


@bot.message_handler(state=States.enter_height)
def get_height(message: Message):
    try:
        user_id, chat_id = get_id(message)
        conn, cursor = get_cursor()
        text = message.text
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if text.isdigit() and 99 < int(text) < 221:
            height = int(text)
            cursor.execute('UPDATE Users SET last_interaction_time = ?, height = ? WHERE user_id = ?',
                           [now, height, user_id])
            conn.commit()
            message_text = '📌*Укажите ваш уровень физической активности:*\n\n' \
                           '1: Малоподвижный образ жизни (тренировок нет / тренируюсь очень редко)\n' \
                           '2: Небольшая активность (1-3 тренировки в неделю)\n' \
                           '3: Умеренная активность (3-5 тренировок в неделю)\n' \
                           '4: Высокая активность (6-7 тренировок в неделю)\n' \
                           '5: Очень высокая активность (тяжелые тренировки 6-7 дней в неделю)'
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            button1 = KeyboardButton('1')
            button2 = KeyboardButton('2')
            button3 = KeyboardButton('3')
            button4 = KeyboardButton('4')
            button5 = KeyboardButton('5')
            markup.row(button1, button2, button3, button4, button5)
            sent_message = bot.send_message(user_id, message_text, reply_markup=markup, parse_mode='Markdown')
            cursor.execute('UPDATE Users SET last_bot_message_id = ?, last_bot_message_type = ? WHERE user_id = ?',
                           [sent_message.message_id, 'text', user_id])
            conn.commit()
            bot.set_state(user_id, States.enter_activity_level, chat_id)
        else:
            sent_message = bot.send_message(user_id, 'Пожалуйста, введите корректный рост в см от 100 до 220 (целое число).')
            cursor.execute('UPDATE Users SET last_bot_message_id = ?, last_bot_message_type = ? WHERE user_id = ?',
                           [sent_message.message_id, 'text', user_id])
            conn.commit()
    except Exception as E:
        bot.send_message(305896408, f'Ошибка! {E}')


@bot.message_handler(state=States.enter_activity_level)
def get_activity_level(message: Message):
    try:
        user_id, chat_id = get_id(message)
        conn, cursor = get_cursor()
        text = message.text
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if text.isdigit() and int(text) in [1, 2, 3, 4, 5]:
            activity_level = int(text)
            cursor.execute(
                'UPDATE Users SET last_interaction_time = ?, activity_level = ? WHERE user_id = ?',
                [now, activity_level, user_id])
            conn.commit()
            sent_message = bot.send_message(user_id, '*И самое важное...*\n\n📝 Опишите вкратце, что вас '
                                                     '*беспокоит и какой результат* вы бы хотели получить '
                                                     'от совместной работы с Ибратом?\n\n'
                                                     '(Напишите короткий текст с ответом на вопрос):',
                                            reply_markup=ReplyKeyboardRemove(), parse_mode='Markdown')
            cursor.execute('UPDATE Users SET last_bot_message_id = ?, last_bot_message_type = ? WHERE user_id = ?',
                           [sent_message.message_id, 'text', user_id])
            conn.commit()
            bot.set_state(user_id, States.describe_problem, chat_id)
        else:
            sent_message = bot.send_message(user_id, 'Пожалуйста, введите корректный уровень активности (число от 1 до 5).')
            cursor.execute('UPDATE Users SET last_bot_message_id = ?, last_bot_message_type = ? WHERE user_id = ?',
                           [sent_message.message_id, 'text', user_id])
            conn.commit()
    except Exception as E:
        bot.send_message(305896408, f'Ошибка! {E}')


@bot.message_handler(state=States.describe_problem)
def describe_problem(message: Message):
    try:
        user_id, chat_id = get_id(message)
        conn = sqlite3.connect('users.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        text = message.text

        cursor.execute('UPDATE Users SET problem = ? WHERE user_id = ?', [text, user_id])
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('UPDATE Users SET notified = ? WHERE user_id = ?', [2, user_id])
        conn.commit()

        official_photo = 'AgACAgIAAxkBAAMhZIICQ7oDNVB64dzT_URs8HLO96IAAjPLMRu1rxFIwmwTchHLlJMBAAMCAAN5AAMvBA'
        test_photo = 'AgACAgIAAxkBAAIGW2Sv1qiouuWd327DKFUt9NLwHp0RAAIlyjEbIj6ASWDi6EmRg_ZgAQADAgADeQADLwQ'

        bot.send_photo(user_id,
                       photo=official_photo,
                       caption='Спасибо за предоставленную информацию!\n\n'
                               '*Ибрат свяжется с вами в течение 24 часов.*\n\n'
                               'Добро пожаловать в 21FIT! ❣️\nЕще увидимся!', parse_mode='Markdown')

        cursor.execute('SELECT * FROM Users WHERE user_id = ?', (user_id,))
        user_info = cursor.fetchone()

        username = user_info['username'] if user_info['username'] is not None else "Отсутствует"
        text = f"🧾 Новая заявка, Босс!\n\n" \
               f"*Имя:* {user_info['name']}\n" \
               f"*Пол:* {user_info['gender']}\n" \
               f"*Телефон:* {user_info['phone']}\n" \
               f"*Возраст:* {user_info['age']}\n" \
               f"*Вес:* {user_info['weight']}\n" \
               f"*Рост:* {user_info['height']}\n" \
               f"*Физ активность:* {activity_levels[user_info['activity_level']]}\n" \
               f"*Проблема:* {user_info['problem']}\n" \
               f"*Username:* @{username}" \
               f"\n\nРада была помочь!\nС любовью, Лиза❣️"
        bot.send_message(305896408, text=text, parse_mode='Markdown')
        bot.send_message(58790442, text=text, parse_mode='Markdown')
        bot.send_message(6553857524, text=text, parse_mode='Markdown')
        bot.send_message(96595636, text=text, parse_mode='Markdown')

        bot.set_state(user_id, States.START, chat_id)
    except Exception as E:
        bot.send_message(305896408, f'Ошибка! {E}')


# @bot.message_handler(content_types=['voice'])
# def handle_voice(message):
#     file_id = message.voice.file_id
#     print(f"Received voice with id: {file_id}", )
#     bot.send_voice(message.chat.id, file_id)
#     bot.send_message(message.from_user.id, f"Received voice with id: {file_id}")


# @bot.message_handler(content_types=['photo'])
# def handle_photo(message):
#     file_id = message.photo[-1].file_id
#     bot.send_message(message.from_user.id, f"Received photo with id: {file_id}")
#     print(f"Received photo with id: {file_id}")
#     bot.send_photo(message.chat.id, file_id)


bot.add_custom_filter(custom_filters.StateFilter(bot))
