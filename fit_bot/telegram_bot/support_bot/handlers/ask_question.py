from ..loader import bot
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton
from ..states import States
from ..data.config import ADMIN
from ...models import SupportTicket

user_data = {}
admin_data = {ADMIN: []}
admin_state = {}


@bot.message_handler(func=lambda message: message.text == 'Задать вопрос')
def ask_a_question(message: Message):
    user_id = message.from_user.id
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = KeyboardButton('Отмена')
    markup.add(button1)
    bot.send_message(user_id, 'Хорошо! напишите ваш вопрос сюда. '
                              'Мы постараемся ответить на него как можно скорее', reply_markup=markup)
    if user_id not in user_data:
        user_data[user_id] = {}
    user_data[user_id]['state'] = States.ASK_QUESTION


@bot.message_handler(func=lambda message: message.from_user.id in user_data and user_data[message.from_user.id]['state'] == States.ASK_QUESTION and message.text == 'Отмена')
def ask_a_question(message: Message):
    user_id = message.from_user.id
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = KeyboardButton('Задать вопрос')
    markup.add(button1)
    bot.send_message(chat_id=message.chat.id, text='Главное меню!',
                     reply_markup=markup)
    user_data[user_id]['state'] = States.START


@bot.message_handler(func=lambda message: message.from_user.id in user_data and user_data[message.from_user.id]['state'] == States.ASK_QUESTION)
def send_question_to_admin(message: Message):
    user_id = message.from_user.id
    question = message.text
    markup = InlineKeyboardMarkup()
    button1 = InlineKeyboardButton(text='Ответить', callback_data=f'reply_question_{user_id}')
    markup.add(button1)

    user_data[user_id]['question'] = question

    username = f'@{message.from_user.username}' if message.from_user.username else "username отсутствует"
    text = f'От пользователя {message.from_user.full_name}, id:{user_id}, {username}: {question}'
    sent_message = bot.send_message(chat_id=ADMIN, text=text, reply_markup=markup)
    bot.send_message(chat_id=message.from_user.id, text='Хорошо! Мы постараемся ответить как можно скорее!!')
    ask_a_question(message)

    admin_data[ADMIN].append({
        'user_id': user_id,
        'admin_message_id': sent_message.message_id,
        'query_message_id': sent_message.message_id,
        'answered': False,
    })


@bot.callback_query_handler(func=lambda call: call.data.startswith('reply_question_'))
def admin_reply_question(call: CallbackQuery):
    user_id = int(call.data.split('_')[2])
    query_message_id = call.message.message_id

    admin_message_id = None
    for pair in admin_data[ADMIN]:
        if pair['user_id'] == user_id and pair['query_message_id'] == query_message_id:
            admin_message_id = pair['admin_message_id']
            break

    if admin_message_id is None:
        return

    bot.answer_callback_query(call.id)
    bot.send_message(chat_id=call.from_user.id, text="Введите ваш ответ:")
    admin_state[ADMIN] = {'user_id': user_id, 'query_message_id': query_message_id}


@bot.message_handler(func=lambda message: message.from_user.id == ADMIN and admin_state.get(ADMIN) is not None)
def send_admin_reply_to_user(message: Message):
    user_id = admin_state[ADMIN]['user_id']
    query_message_id = admin_state[ADMIN]['query_message_id']
    admin_message_id = None

    for pair in admin_data[ADMIN]:
        if pair['user_id'] == user_id and pair['query_message_id'] == query_message_id and not pair['answered']:
            admin_message_id = pair['admin_message_id']
            pair['answered'] = True
            break

    if admin_message_id is None:
        return

    bot.send_message(chat_id=user_id, text=f'Ответ от оператора: \n{message.text}')
    bot.delete_message(chat_id=ADMIN, message_id=admin_message_id)

    admin_data[ADMIN] = [pair for pair in admin_data[ADMIN] if not pair['answered']]
    admin_state[ADMIN] = None

