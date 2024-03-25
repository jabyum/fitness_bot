from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove, CallbackQuery
from telebot import custom_filters
from django.utils import timezone

from .edit_calories_backends import get_id, create_keyboard_markup, meal_info, \
    update_courseday_calories, update_meal, one_five_markup, food_choosing_menu
from ...loader import bot
from ...states import CourseInteraction
from ...models import PaidUser, CourseDay, Meal
from ..mainmenu import paid_user_main_menu
from .edit_calories import user_data

calories_data = {}


@bot.callback_query_handler(state=CourseInteraction.initial, func=lambda call: call.data == 'add_product')
def add_new_product(call: CallbackQuery):
    user_id, chat_id = get_id(call=call)
    if user_id not in calories_data:
        calories_data[user_id] = {}

    bot.delete_message(chat_id=chat_id, message_id=call.message.message_id)
    text = "⚡️Я тут, готова помочь!\n\n" \
           "- Введите текстом название продукта/блюда"
    markup = create_keyboard_markup('Отмена!')
    bot.set_state(user_id, CourseInteraction.enter_new_product, chat_id)
    # bot.send_photo(photo='AgACAgIAAxkBAAIlvGSZZSve3u6eHwdvffFT25_CmUgxAALfyzEbqbHRSCITmUvvInNJAQADAgADeQADLwQ',
    #                caption=text, chat_id=chat_id, reply_markup=markup)
    bot.send_photo(photo='AgACAgIAAxkBAAL6LGSZk6v6A55yfB8rGn2U_K-VyiRtAALfyzEbqbHRSCOlCtFXAAHOJgEAAwIAA3kAAy8E',
                   caption=text, chat_id=chat_id, reply_markup=markup)


@bot.message_handler(state=CourseInteraction.enter_new_product, content_types=['text'])
def handle_new_product(message: Message):
    user_id, chat_id = get_id(message=message)
    answer = message.text
    user = PaidUser.objects.get(user=user_id)
    current_day = (timezone.now().date() - user.paid_day).days
    meal = user_data[user_id][current_day]['selected_meal']
    course_day = CourseDay.objects.get(user=user, day=current_day)
    text, markup = meal_info(user, current_day, user_data, user_id, meal)
    if answer == 'Отмена!':

        keyboard_markup = create_keyboard_markup('Мой дневник калорий 📆',
                                                 'Сколько еще можно ккал?👀', 'Карта программы 🗺',
                                                 'Появились вопросики...')
        bot.send_message(chat_id=user_id, text='Отменено!', reply_markup=keyboard_markup)
        bot.send_message(text=text, chat_id=chat_id, reply_markup=markup, parse_mode='Markdown')
        bot.set_state(user_id, CourseInteraction.initial, chat_id)
    else:
        calories_data[user_id]['chosen_dish'] = answer

        text_answer, data, list_for_me, one_five = food_choosing_menu(answer, user_id)
        if text_answer:
            bot.send_message(user_id, 'Выберите один из предложенных вариантов:', reply_markup=ReplyKeyboardRemove())
            calories_data[user_id]['needed_data'] = [data, list_for_me]
            calories_data[user_id]['variants'] = text_answer
            calories_data[user_id]['needed_data_keyboard'] = one_five

            bot.send_message(user_id, text=f'{text_answer}', reply_markup=one_five)

            calories_data[user_id]['needed_data'] = [data, list_for_me]
            bot.set_state(user_id, CourseInteraction.choose_product, chat_id)
        else:
            markup = InlineKeyboardMarkup()
            button1 = InlineKeyboardButton(text='Попробовать снова', callback_data='try_again')
            button2 = InlineKeyboardButton(text='Ввести вручную', callback_data='by_hand')
            markup.add(button1)
            markup.add(button2)

            bot.send_message(user_id, text=f'Кажется, в нашей базе нет такого продукта.\n\n'
                                           f'Попробуйте запустить процесс поиска снова или введите продукт '
                                           f'вручную', reply_markup=markup)

            #
            # markup = create_keyboard_markup('Получить тренировки 🎾', 'Мой дневник калорий 📆',
            #                                 'Сколько еще можно ккал?👀', 'Появились вопросики...')
            # bot.set_state(user_id, CourseInteraction.initial, chat_id)

            # user = PaidUser.objects.get(user=user_id)
            # current_day = (timezone.now().date() - user.paid_day).days
            # text, markup = meal_info(user, current_day, user_data, user_id, meal)
            #
            # bot.send_message(text=text, chat_id=chat_id, reply_markup=markup, parse_mode='Markdown')


@bot.callback_query_handler(state=CourseInteraction.enter_new_product, func=lambda call: call.data)
def handle_new_product(call: CallbackQuery):
    user_id, chat_id = get_id(call=call)
    answer = call.data

    if answer == 'try_again':
        bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id,
                              text='Введите название продукта снова:', reply_markup=None)
    else:
        text = "В таком случае введите название блюда:"
        bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=text, reply_markup=None)
        bot.set_state(user_id, CourseInteraction.enter_meal_name, chat_id)


@bot.callback_query_handler(state=CourseInteraction.choose_product, func=lambda call: call.data)
def handle_choosen_product(call: CallbackQuery):
    user_id, chat_id = get_id(call=call)

    answer = call.data

    user = PaidUser.objects.get(user=user_id)
    current_day = (timezone.now().date() - user.paid_day).days

    if answer == 'cancel_product':
        bot.delete_message(chat_id, message_id=call.message.message_id)
        markup = create_keyboard_markup('Мой дневник калорий 📆',
                                        'Сколько еще можно ккал?👀', 'Карта программы 🗺', 'Появились вопросики...')
        bot.send_message(chat_id=chat_id, text='Главное меню', reply_markup=markup)

        text, markup = meal_info(user, current_day, user_data, user_id,
                                 user_data[user_id][current_day]['selected_meal'])
        bot.send_message(text=text, chat_id=chat_id, reply_markup=markup, parse_mode='Markdown')
        bot.set_state(user_id, CourseInteraction.initial, chat_id)

    elif answer == 'try_again':
        bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id,
                              text='Хорошо, введите ваш запрос еще раз:')
        bot.set_state(user_id, CourseInteraction.enter_new_product, chat_id)
    elif answer == 'enter_manually':
        bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id,
                              text='Хорошо, в таком случае введите название продукта:')
        bot.set_state(user_id, CourseInteraction.enter_meal_name, chat_id)

    else:
        nutrient_dict = {"11": "Калорий", "13": "Белков"}
        nutrients_list = calories_data[user_id]['needed_data'][0]
        choice = answer
        markup = InlineKeyboardMarkup()
        button1 = InlineKeyboardButton(text='Продолжить', callback_data='continue')
        button2 = InlineKeyboardButton(text='Назад', callback_data='back')
        markup.add(button1)
        markup.add(button2)
        if answer != 'cancelamount1':
            answer_text = f'📍Итак, вы добавляете: \n\n{calories_data[user_id]["needed_data"][1][int(choice) - 1]}\n\n'
            calories_data[user_id]['chosen_number'] = int(choice) - 1
        else:
            answer_text = f'📍Итак, вы добавляете: \n\n' \
                          f'{calories_data[user_id]["needed_data"][1][calories_data[user_id]["chosen_number"]]}\n\n'

        calories_data[user_id]['KBJU_data'] = []

        for nutrient, value in nutrients_list[calories_data[user_id]["chosen_number"]].items():
            if nutrient in nutrient_dict:  # Проверяем, есть ли питательное вещество в нашем фильтрованном словаре
                nutrient_name = nutrient_dict.get(str(nutrient), nutrient)
                value = value if value is not None else 0
                answer_text += f"{nutrient_name}: {value}\n"
                calories_data[user_id]['KBJU_data'].append(round(float(value), 1))

        calories_data[user_id]['chosen_dish'] = \
            [calories_data[user_id]["needed_data"][1][calories_data[user_id]["chosen_number"]],
             calories_data[user_id]['KBJU_data']]

        bot.edit_message_text(chat_id=user_id, text=answer_text,
                              message_id=call.message.message_id, reply_markup=markup)
        bot.set_state(user_id, CourseInteraction.continue_choosing_product, chat_id)


@bot.callback_query_handler(state=CourseInteraction.continue_choosing_product, func=lambda call: call.data)
def continue_handle_choose_product(call: CallbackQuery):
    answer = call.data
    user_id, chat_id = get_id(call=call)
    if answer == 'back':
        text_answer = calories_data[user_id]['variants']
        bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id,
                              text=f'{text_answer}', reply_markup=calories_data[user_id]['needed_data_keyboard'])
        bot.set_state(user_id, CourseInteraction.choose_product, chat_id)
    else:
        dish = calories_data[user_id]['chosen_dish'][0]
        if 'штука' in dish.lower() or 'порция' in dish.lower():
            if 'штука' in dish.lower():
                text = f"Выберите количество штук для продукта {dish}"
            else:
                text = f"Выберите количество порций для продукта {dish}"
            one_five = one_five_markup(second=True)
            bot.edit_message_text(chat_id=chat_id, text=text, message_id=call.message.message_id,
                                  reply_markup=one_five)
            bot.set_state(user_id, CourseInteraction.choose_amount, chat_id)
        else:
            text = 'Хорошо, введите количество грамм для данного продукта:'
            bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id,
                                  text=text, reply_markup=None)
            bot.set_state(user_id, CourseInteraction.enter_grams, chat_id)


@bot.message_handler(state=CourseInteraction.enter_grams, content_types=['text'])
def handle_grams_count(message: Message):
    user_id, chat_id = get_id(message=message)
    answer = message.text
    try:
        answer = answer.replace(',', '.')
        amount = float(answer)
        if -1 < float(answer) < 5001:
            markup = create_keyboard_markup('Мой дневник калорий 📆',
                                            'Сколько еще можно ккал?👀', 'Карта программы 🗺', 'Появились вопросики...')
            bot.send_message(chat_id=chat_id, text='Добавлено!', reply_markup=markup)
            user = PaidUser.objects.get(user=user_id)
            current_day = (timezone.now().date() - user.paid_day).days
            selected_meal = user_data[user_id][current_day]['selected_meal']
            product = f"{calories_data[user_id]['needed_data'][1][calories_data[user_id]['chosen_number']]}"

            if product in user_data[user_id][current_day][selected_meal]:
                old_calories, _, old_proteins, _ = user_data[user_id][current_day][selected_meal][product].split()
                old_calories = float(old_calories)
                old_proteins = float(old_proteins.rstrip('г'))

                new_calories = round(float(calories_data[user_id]['KBJU_data'][0]) * (amount / 100), 1) + old_calories
                new_proteins = round(float(calories_data[user_id]['KBJU_data'][1]) * (amount / 100), 1) + old_proteins

                user_data[user_id][current_day][selected_meal][product] = f"{new_calories} ккал {new_proteins}г белков"
            else:
                user_data[user_id][current_day][selected_meal][product] = \
                    f"{round(float(calories_data[user_id]['KBJU_data'][0]) * (amount / 100), 1)} ккал " \
                    f"{round(float(calories_data[user_id]['KBJU_data'][1]) * (amount / 100), 1)}г белков"

            course_day, created = CourseDay.objects.get_or_create(user=user, day=current_day)
            meal, _ = Meal.objects.get_or_create(course_day=course_day,
                                                 meal_type=user_data[user_id][current_day]['selected_meal'])
            update_meal(meal,
                        round(float(calories_data[user_id]['KBJU_data'][0]) * (amount / 100), 1),  # калории
                        round(float(calories_data[user_id]['KBJU_data'][1]) * (amount / 100), 1))
            update_courseday_calories(course_day)

            text, markup = meal_info(user, current_day, user_data, user_id,
                                     meal=user_data[user_id][current_day]['selected_meal'])
            bot.send_message(text=text, chat_id=chat_id, reply_markup=markup, parse_mode='Markdown')
            bot.set_state(user_id, CourseInteraction.initial, chat_id)
    except:
        bot.send_message(text='Кажется, вы ввели что-то не так, попробуйте еще раз. Например, 150:', chat_id=chat_id)


@bot.callback_query_handler(state=CourseInteraction.choose_amount, func=lambda call: call.data)
def handle_amount(call: CallbackQuery):
    user_id, chat_id = get_id(call=call)
    answer = call.data
    if answer == 'cancelamount1':
        handle_choosen_product(call)
    else:
        amount = int(answer)
        bot.delete_message(chat_id, message_id=call.message.message_id)
        markup = create_keyboard_markup('Мой дневник калорий 📆',
                                        'Сколько еще можно ккал?👀', 'Карта программы 🗺', 'Появились вопросики...')
        bot.send_message(chat_id=chat_id, text='Добавлено!', reply_markup=markup)
        user = PaidUser.objects.get(user=user_id)
        current_day = (timezone.now().date() - user.paid_day).days
        user_data[user_id][current_day][user_data[user_id][current_day]['selected_meal']][
            f"{calories_data[user_id]['needed_data'][1][calories_data[user_id]['chosen_number']]}"] \
            = f"{round(float(calories_data[user_id]['KBJU_data'][0]) * amount, 1)} ккал " \
              f"{round(float(calories_data[user_id]['KBJU_data'][1]) * amount, 1)}г белков"
        # bot.send_message(user_id, text=f"{user_data[user_id][current_day][user_data[user_id]
        # [current_day]['selected_meal']]}")
        course_day, created = CourseDay.objects.get_or_create(user=user, day=current_day)
        meal, _ = Meal.objects.get_or_create(course_day=course_day,
                                             meal_type=user_data[user_id][current_day]['selected_meal'])
        update_meal(meal,
                    round(float(calories_data[user_id]['KBJU_data'][0]) * amount, 1),  # калории
                    round(float(calories_data[user_id]['KBJU_data'][1]) * amount, 1))

        update_courseday_calories(course_day)

        text, markup = meal_info(user, current_day, user_data, user_id,
                                 meal=user_data[user_id][current_day]['selected_meal'])
        bot.send_message(text=text, chat_id=chat_id, reply_markup=markup, parse_mode='Markdown')
        bot.set_state(user_id, CourseInteraction.initial, chat_id)


bot.add_custom_filter(custom_filters.StateFilter(bot))
