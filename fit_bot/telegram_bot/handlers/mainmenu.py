import time

from telebot.types import Message, ReplyKeyboardMarkup, KeyboardButton,\
    InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from telebot import custom_filters

from ..loader import bot
from ..models import UnpaidUser, PaidUser
from ..states import CourseInteraction, AfterPurchaseStates
from courses.models import Mailing


@bot.message_handler(content_types=['photo'])
def return_photo_id(message: Message):
    file_id = message.photo[-1].file_id
    bot.send_message(message.from_user.id, f"Received photo with id: {file_id}")
    print(f"Received photo with id: {file_id}")
    bot.send_photo(message.chat.id, file_id)



def get_id(message=None, call=None):
    if message:
        return message.from_user.id, message.chat.id
    elif call:
        return call.from_user.id, call.message.chat.id


def create_inline_markup(*args):
    markup = InlineKeyboardMarkup()
    for b, callback_data in args:
        button = InlineKeyboardButton(text=b, callback_data=callback_data)
        markup.add(button)
    return markup


def create_keyboard_markup(*args, row=False):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    if row:
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=len(args))
        buttons = [KeyboardButton(i) for i in args]
        markup.add(*buttons)
        return markup
    else:
        for i in args:
            button = KeyboardButton(i)
            markup.add(button)
        return markup


@bot.message_handler(commands=['start'])
def start_message(message: Message):
    user_id, chat_id = get_id(message=message)
    user, created = UnpaidUser.objects.get_or_create(user_id=user_id)
    if created:
        user.save()
    try:
        paid_user = PaidUser.objects.get(user=user_id)
        if paid_user:
            paid_user_main_menu(message)
        elif not paid_user and user.has_paid:
            bot.set_state(user_id, AfterPurchaseStates.initial, chat_id)
        return
    except PaidUser.DoesNotExist:
        pass

    username, full_name = message.from_user.username, message.from_user.full_name

    user = UnpaidUser(user_id=message.from_user.id, username=username, full_name=full_name)
    user.save()
    # markup = create_inline_markup(('Погнали!', 'Go_for_it'))
    # # markup = create_keyboard_markup('Приобрести подписку на курс', 'Появились вопросики...')
    # # test = 'BAACAgIAAxkBAAIxYGTWh_wDmD32nJlzJLLGOArhY3W6AAI8MwACs4axSvCiT5O4osErMAQ'
    # official = 'BAACAgIAAxkBAAEBICtk1ohR32s4sZirw2ksKvRvwSq6rAACPDMAArOGsUrqNisitMXu0TAE'
    # bot.send_video(user_id, video=official, reply_markup=markup)

    # daily_contents = Mailing.objects.filter(day=0)
    #
    # for content in daily_contents:
    #     if content.content_type == 'V':
    #         bot.send_video(chat_id=user.user_id, video=content.video_file_id,
    #                        caption=content.caption, reply_markup=markup)
    #     elif content.content_type == 'T':
    #         bot.send_message(chat_id=user.user_id, text=content.caption,
    #                          reply_markup=markup)
    #     elif content.content_type == 'P':
    #         bot.send_photo(chat_id=user.user_id, photo=content.photo_file_id,
    #                        caption=content.caption, reply_markup=markup)
    #     elif content.content_type == 'G':
    #         bot.send_document(chat_id=user.user_id, document=content.gif_file_id,
    #                           caption=content.caption, reply_markup=markup)
    #     time.sleep(3)

    markup = create_keyboard_markup('Появились вопросики...')

    test = 'AgACAgIAAxkBAAIxZmTWibqN_mHYK-1uJs08CdoexIw0AAI4zDEb8Jm5SqYMWroMFb56AQADAgADeQADMAQ'
    official = 'AgACAgIAAxkBAAEBJA9k2rj2-rChgpOYjuzj5M0XhhxWVwAC4coxG3dI2EqAfXmGAAHDqlABAAMCAAN5AAMwBA'
    text = '*👋 Привет, меня зовут Лиза*\n\n' \
           'Я – виртуальный ассистент Ибрата и буду помогать вам на всем ' \
           'пути взаимодействия с ботом ☺️'

    bot.send_message(chat_id, text=text, reply_markup=markup, parse_mode='Markdown')

    # markup = create_inline_markup(('Тинькофф (Россия)', 'tinkoff'), ('Click/Payme (Узбекистан)', 'click'),
    #                               ('Другое', 'other'))
    markup = create_inline_markup(('Пройти регистрацию', 'registration'))

    # bot.send_message(chat_id, text='Чтобы получить доступ к программе, выберите удобный для вас способ оплаты:',
    #                  reply_markup=markup)
    bot.send_message(chat_id, text='Чтобы получить доступ к программе, пройдите регистрацию 📝',
                     reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Появились вопросики...')
def info(message: Message):
    bot.send_message(chat_id=message.chat.id,
                     text='Наш бот техподдержки - @help_fit_bot')


def just_main_menu(message: Message):
    markup = create_keyboard_markup('Контакт оператора')
    bot.send_message(chat_id=message.chat.id, text='Главное меню', reply_markup=markup)


def paid_user_main_menu(message: Message):
    user_id, chat_id = get_id(message=message)
    markup = create_keyboard_markup('Мой дневник калорий 📆',
                                    'Сколько еще можно ккал?👀', 'Карта программы 🗺', 'Появились вопросики...')
    bot.set_state(user_id, CourseInteraction.initial, chat_id)
    bot.send_message(user_id, text='Главное меню', reply_markup=markup)



bot.add_custom_filter(custom_filters.StateFilter(bot))

