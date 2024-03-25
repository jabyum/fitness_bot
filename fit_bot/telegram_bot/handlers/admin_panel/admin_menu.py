from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, \
    CallbackQuery, ReplyKeyboardRemove
from telebot import custom_filters
from ...loader import bot
from ...filters.is_admin import IsAdminFilter
from ...states import States, AdminStates
from ...models import PaidUser, UnpaidUser, FinishedUser
from ...handlers.mainmenu import paid_user_main_menu
from ..courses_interaction.edit_calories_backends import create_keyboard_markup, get_id

from courses.models import Категории, Video

admin_data = {}


def create_categories_keyboard(for_unpaid=False):
    if not for_unpaid:
        markup = InlineKeyboardMarkup()
        categories = Категории.objects.all()

        for index, category in enumerate(categories, start=1):
            button = InlineKeyboardButton(str(index), callback_data=f'category_{index}')
            markup.add(button)
    else:
        markup = InlineKeyboardMarkup()

    return markup


def get_users_by_category_name(model_class, category_name=False):
    if category_name:
        category = Категории.objects.get(название=category_name)
        users = model_class.objects.filter(
            пол=category.пол,
            цель=category.цель,
            место=category.место,
            уровень=category.уровень
        )
    else:
        if not model_class == UnpaidUser:
            users = model_class.objects.all()
        else:
            users = model_class.objects.filter(
                has_paid=False
            )
    return users


def send_message_to_users(users, message_text=None, photo_file_id=None, caption=None):
    for user in users:
        try:
            chat_id = user.user
        except AttributeError:
            chat_id = user.user_id
        if photo_file_id:
            bot.send_photo(chat_id, photo_file_id, caption=caption)
        elif message_text:
            bot.send_message(chat_id, message_text)


@bot.message_handler(commands=['admin'], is_admin=True)
def what(message: Message):
    user_id, chat_id = get_id(message=message)
    if user_id not in admin_data:
        admin_data[user_id] = {'state': None}
    bot.set_state(user_id, AdminStates.initial, chat_id)
    markup = create_keyboard_markup('Рассылка', 'Загрузить видео', 'Вернуться назад')
    bot.send_message(user_id, 'Это админ-панель! Пожалуйста, выберите что вы хотите сделать нажав на кнопку ниже',
                     reply_markup=markup)


@bot.message_handler(state=AdminStates.initial, content_types=['text'])
def mailing(message: Message):
    user_id, chat_id = get_id(message=message)
    answer = message.text
    if answer == 'Рассылка':
        markup = create_keyboard_markup('Рассылка по PaidUsers', 'Рассылка по FinishedUsers',
                                        'Рассылка по Unpaid', 'Вернуться назад')
        bot.send_message(user_id, 'Пожалуйста, уточните категорию рассылки', reply_markup=markup)
        bot.set_state(user_id, AdminStates.choosing_mailing_category, chat_id)
    elif answer == 'Вернуться назад':
        paid_user_main_menu(message)
    else:
        markup = create_keyboard_markup('Назад!')
        bot.send_message(user_id, text="Пожалуйста, загрузите видео:", reply_markup=markup)
        bot.set_state(user_id, AdminStates.upload_video, chat_id)


@bot.message_handler(state=AdminStates.upload_video, content_types=['text', 'video'])
def handle_video_upload(message: Message):
    user_id, chat_id = get_id(message=message)
    if message.video:
        video = message.video
        video_file_id = video.file_id
        video_name = message.video.file_name
        new_video = Video(name=video_name, video_file_id=video_file_id)
        new_video.save()
        bot.send_message(user_id, "Видео успешно загружено и сохранено")
        what(message)
    else:
        what(message)


@bot.message_handler(state=AdminStates.choosing_mailing_category, content_types=['text'])
def handle_mailing(message: Message):
    user_id, chat_id = get_id(message=message)
    answer = message.text

    if answer in ['Рассылка по PaidUsers', 'Рассылка по FinishedUsers', 'Рассылка по Unpaid']:
        if answer in ['Рассылка по PaidUsers', 'Рассылка по FinishedUsers']:
            if answer == 'Рассылка по PaidUsers':
                admin_data[user_id]['category_of_mailing'] = 'PaidUser'
            else:
                admin_data[user_id]['category_of_mailing'] = 'FinishedUser'
            markup = create_categories_keyboard()
            text = 'Пожалуйста, выберите категорию для рассылки сообщений:\n'
            text += '\n'.join(
                [f'{index} - {category.название}' for index, category in enumerate(Категории.objects.all(), start=1)])
        else:
            admin_data[user_id]['category_of_mailing'] = 'UnpaidUser'
            markup = create_categories_keyboard(for_unpaid=True)
            text = 'Пожалуйста, выберите категорию для рассылки сообщений:'

        markup.add(InlineKeyboardButton(text='По всем пользователям', callback_data='category_all'))
        bot.send_message(chat_id=message.chat.id,
                         text=text,
                         reply_markup=markup)
    else:
        what(message)


@bot.callback_query_handler(state=AdminStates.choosing_mailing_category, func=lambda call: call.data.startswith('category_'))
def category_callback(call: CallbackQuery):
    if not call.data.split('_')[1] == 'all':
        category_index = int(call.data.split('_')[1])
        selected_category = Категории.objects.all()[category_index - 1]
    else:
        selected_category = 'all'

    # Сохранение выбранной категории в admin_data
    admin_data[call.from_user.id]['category'] = selected_category
    markup = InlineKeyboardMarkup()
    button1 = InlineKeyboardButton('Текст', callback_data='message_type_text')
    button2 = InlineKeyboardButton('Фото', callback_data='message_type_photo')
    markup.add(button1, button2)
    if selected_category == 'all':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=f'Выберите тип сообщения для рассылки по всем пользователям:',
                              reply_markup=markup)
    else:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                         text=f'Выберите тип сообщения для рассылки в категории "{selected_category.название}":',
                         reply_markup=markup)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(state=AdminStates.choosing_mailing_category, func=lambda call: call.data == 'message_type_text')
def message_type_text_callback(call: CallbackQuery):
    user_id, chat_id = get_id(call=call)
    admin_data[call.from_user.id]['message_type'] = 'text'
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id, text='Пожалуйста, отправьте текст сообщения для рассылки.')
    bot.set_state(user_id, AdminStates.enter_mailing_text, chat_id)


@bot.callback_query_handler(state=AdminStates.choosing_mailing_category, func=lambda call: call.data == 'message_type_photo')
def message_type_photo_callback(call: CallbackQuery):
    admin_data[call.from_user.id]['message_type'] = 'photo'

    markup = InlineKeyboardMarkup()
    button_yes = InlineKeyboardButton('Да', callback_data='add_caption_yes')
    button_no = InlineKeyboardButton('Нет', callback_data='add_caption_no')
    markup.add(button_yes, button_no)

    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text='Хотите добавить заголовок к фотографии?', reply_markup=markup)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(state=AdminStates.choosing_mailing_category, func=lambda call: call.data in ('add_caption_yes', 'add_caption_no'))
def add_caption_callback(call: CallbackQuery):
    user_id, chat_id = get_id(call=call)
    if call.data == 'add_caption_yes':
        admin_data[call.from_user.id]['add_caption'] = True
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Пожалуйста, отправьте фотографию с заголовком, '
                              'которую вы хотите разослать (бот получит file_id фотографии).')
    else:
        admin_data[call.from_user.id]['add_caption'] = False
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Пожалуйста, отправьте фотографию без заголовка, '
                              'которую вы хотите разослать (бот получит file_id фотографии).')
    bot.set_state(user_id, AdminStates.upload_photo, chat_id)

    bot.answer_callback_query(call.id)


@bot.message_handler(state=AdminStates.enter_mailing_text, content_types=['text'], is_admin=True)
def text_handler(message: Message):
    text = message.text
    markup = InlineKeyboardMarkup()
    button_yes = InlineKeyboardButton('Да', callback_data='send_text_yes')
    button_no = InlineKeyboardButton('Нет', callback_data='send_text_no')
    markup.add(button_yes, button_no)
    bot.send_message(chat_id=message.chat.id,
                     text=f'Вы уверены, что хотите отправить данное текстовое сообщение?\n\n{text}',
                     reply_markup=markup)


@bot.message_handler(state=AdminStates.upload_photo, content_types=['photo'], is_admin=True)
def photo_handler(message: Message):
    photo = message.photo[-1]  # Получение самой большой версии фотографии
    file_id = photo.file_id

    caption = message.caption if admin_data[message.from_user.id]['add_caption'] else None

    # Спрашиваем у пользователя, отправлять или нет
    markup = InlineKeyboardMarkup()
    button_yes = InlineKeyboardButton('Да', callback_data='send_photo_yes')
    button_no = InlineKeyboardButton('Нет', callback_data='send_photo_no')
    markup.add(button_yes, button_no)

    if caption:
        bot.send_photo(chat_id=message.chat.id, photo=file_id,
                       caption=f'Вы уверены, что хотите отправить данную фотографию с заголовком: "{caption}"?',
                       reply_markup=markup)
    else:
        bot.send_photo(chat_id=message.chat.id, photo=file_id,
                       caption='Вы уверены, что хотите отправить данную фотографию без заголовка?',
                       reply_markup=markup)


@bot.callback_query_handler(state=AdminStates.enter_mailing_text, func=lambda call: call.data in ('send_text_yes', 'send_text_no'))
def send_text_callback(call: CallbackQuery):
    user_id, chat_id = get_id(call=call)
    if call.data == 'send_text_yes':
        text = call.message.text
        model_class = PaidUser if admin_data[call.from_user.id]['category_of_mailing'] == 'PaidUser' \
            else FinishedUser if admin_data[call.from_user.id]['category_of_mailing'] == 'FinishedUser' else UnpaidUser

        if admin_data[call.from_user.id]['category'] == 'all':
            users_to_send = get_users_by_category_name(
                model_class=model_class)
        else:
            users_to_send = get_users_by_category_name(
                model_class=model_class,
                category_name=admin_data[call.from_user.id]['category'])

        send_message_to_users(users_to_send, message_text=' '.join(text.split()[8:]))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Отправлено!')
    else:
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id, text='Отправка текстового сообщения отменена.')
    bot.set_state(user_id, AdminStates.choosing_mailing_category, chat_id)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(state=AdminStates.upload_photo, func=lambda call: call.data in ('send_photo_yes', 'send_photo_no'))
def send_photo_callback(call: CallbackQuery):
    user_id, chat_id = get_id(call=call)
    if call.data == 'send_photo_yes':
        photo = call.message.photo[-1]  # Получение самой большой версии фотографии
        file_id = photo.file_id

        caption = call.message.caption
        model_class = PaidUser if admin_data[call.from_user.id]['category_of_mailing'] == 'PaidUser' \
            else FinishedUser if admin_data[call.from_user.id]['category_of_mailing'] == 'FinishedUser' else UnpaidUser

        if admin_data[call.from_user.id]['category'] == 'all':
            users_to_send = get_users_by_category_name(
                model_class=model_class)
        else:
            users_to_send = get_users_by_category_name(
                model_class=model_class,
                category_name=admin_data[call.from_user.id]['category'])
        send_message_to_users(users_to_send, photo_file_id=file_id, caption=' '.join(caption.split()[9:])[1:-2])
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(chat_id=call.message.chat.id, text='Отправлено!')


        # admin_data[call.from_user.id]['category'] - это сама категория (может быть all)
        # admin_data[call.from_user.id]['category_of_mailing'] - PaidUsers etc.
    else:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Отправка фотографии отменена.')
    bot.set_state(user_id, AdminStates.choosing_mailing_category, chat_id)
    bot.answer_callback_query(call.id)


bot.add_custom_filter(custom_filters.StateFilter(bot))