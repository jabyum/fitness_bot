from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import json
import re

from ...models import CourseDay, Meal


def create_calories_menu():
    markup = types.InlineKeyboardMarkup()
    button_breakfast = types.InlineKeyboardButton("Завтрак", callback_data="breakfast")
    button_lunch = types.InlineKeyboardButton("Обед", callback_data="lunch")
    button_dinner = types.InlineKeyboardButton("Ужин", callback_data="dinner")
    button_snack = types.InlineKeyboardButton("Перекус", callback_data="snack")
    button_progress = types.InlineKeyboardButton("Отчет за весь период", callback_data="progress")
    markup.row(button_breakfast, button_lunch)
    markup.row(button_dinner, button_snack)
    markup.row(button_progress)
    return markup


def create_calories_add_or_remove_menu():
    markup = types.InlineKeyboardMarkup()
    button_add_remove = types.InlineKeyboardButton("📝 Внести прием пищи вручную", callback_data="add_remove")
    button_add_product = types.InlineKeyboardButton("👋 Лиза помоги…", callback_data="add_product")
    button_redact = types.InlineKeyboardButton('Редактировать введенные продукты', callback_data='redact')
    button_back = types.InlineKeyboardButton("Назад", callback_data="back")
    markup.row(button_add_remove)
    markup.row(button_add_product)
    markup.row(button_redact)
    markup.row(button_back)
    return markup


def get_id(message=None, call=None):
    if message:
        return message.from_user.id, message.chat.id
    elif call:
        return call.from_user.id, call.message.chat.id


def return_calories_and_norm(user_model, day):
    course_day, created = CourseDay.objects.get_or_create(user=user_model, day=day)
    breakfast, _ = Meal.objects.get_or_create(course_day=course_day, meal_type='breakfast')
    lunch, _ = Meal.objects.get_or_create(course_day=course_day, meal_type='lunch')
    dinner, _ = Meal.objects.get_or_create(course_day=course_day, meal_type='dinner')
    snack, _ = Meal.objects.get_or_create(course_day=course_day, meal_type='snack')

    user_data = {
        'breakfast': {
            'calories': breakfast.calories,
            'protein': breakfast.protein,
            'fat': breakfast.fat,
            'carbs': breakfast.carbs
        },
        'lunch': {
            'calories': lunch.calories,
            'protein': lunch.protein,
            'fat': lunch.fat,
            'carbs': lunch.carbs
        },
        'dinner': {
            'calories': dinner.calories,
            'protein': dinner.protein,
            'fat': dinner.fat,
            'carbs': dinner.carbs
        },
        'snack': {
            'calories': snack.calories,
            'protein': snack.protein,
            'fat': snack.fat,
            'carbs': snack.carbs
        }
    }

    daily_norm = int(user_model.calories)
    daily_proteins_norm = int(user_model.proteins)
    total_calories = sum(meal['calories'] for meal in user_data.values())
    remaining_calories = round(daily_norm - total_calories, 1)

    total_proteins = sum(meal['protein'] for meal in user_data.values())
    remaining_proteins = round(daily_proteins_norm - total_proteins, 1)

    return user_data, remaining_calories, daily_norm, daily_proteins_norm, remaining_proteins


def create_main_editing_menu(user, current_day):
    user_calories, remaining_calories, daily_norm, daily_proteins_norm,\
        remaining_proteins = return_calories_and_norm(user, current_day)

    if remaining_calories < 0:
        remaining_calories = '0'
    if remaining_proteins < 0:
        remaining_proteins = '0'
    name = user.full_name
    text = (
        f"*Текущая норма: {daily_norm} ккал / {daily_proteins_norm} г белка*\n\n"
        f"*🍳 Завтрак:*\n"
        f"{round(user_calories['breakfast']['calories'], 1)} ккал / {round(user_calories['breakfast']['protein'], 1)} г белка\n\n"
        f"*🥗 Обед:*\n"
        f"{round(user_calories['lunch']['calories'], 1)} ккал / {round(user_calories['lunch']['protein'], 1)} г белка\n\n"
        f"*🍲 Ужин:*\n"
        f"{round(user_calories['dinner']['calories'], 1)} ккал / {round(user_calories['dinner']['protein'], 1)} г белка\n\n"
        f"*🍏 Перекусы:*\n"
        f"{round(user_calories['snack']['calories'], 1)} ккал / {round(user_calories['snack']['protein'], 1)} г белка\n\n"
        f"*🧾 Итого за день:*\n"
        f"Ккал: {round(user_calories['breakfast']['calories'] + user_calories['lunch']['calories'] + user_calories['dinner']['calories'] + user_calories['snack']['calories'], 1)} ккал\n"
        f"Белка: {round(user_calories['breakfast']['protein'] + user_calories['lunch']['protein'] + user_calories['dinner']['protein'] + user_calories['snack']['protein'], 1)} г белка\n\n"
        f"*{name}, вам еще нужно съесть:* \n{remaining_calories} ккал / {remaining_proteins}г белка"
    )

    markup = create_calories_menu()

    return text, markup


def get_meal_info_text(meal_name, meal_data, user_meals):
    if user_meals:
        meals_text = ''
        for i in user_meals:
            meals_text += f'- {i} - {user_meals[i]}\n'
    else:
        meals_text = 'Кажется, вы еще ничего не добавили!'
    text = (f"🧾Вы съели на *{meal_name}*\n\n"
            f"*Ккал:* {round(meal_data['calories'], 1)}\n"
            f"*Белка:* {round(meal_data['protein'], 1)} г\n\n"
            f"📍Ранее вы добавили следующие продукты:\n\n{meals_text}")
    return text, meals_text


def create_keyboard_markup(*args):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in args:
        button = types.KeyboardButton(i)
        markup.add(button)
    return markup


def meal_info(user, current_day, user_data, user_id, meal):
    user_calories, remaining_calories, daily_norm, daily_proteins_norm, remaining_proteins\
        = return_calories_and_norm(user, current_day)

    if meal == "breakfast":
        text, meals_text = get_meal_info_text("завтрак", user_calories['breakfast'], user_data[user_id][current_day]['breakfast'])
        markup = create_calories_add_or_remove_menu()
    elif meal == "lunch":
        text, meals_text = get_meal_info_text("обед", user_calories['lunch'], user_data[user_id][current_day]['lunch'])
        markup = create_calories_add_or_remove_menu()
    elif meal == "dinner":
        text, meals_text = get_meal_info_text("ужин", user_calories['dinner'], user_data[user_id][current_day]['dinner'])
        markup = create_calories_add_or_remove_menu()
    elif meal == 'snack':
        text, meals_text = get_meal_info_text("перекусы", user_calories['snack'], user_data[user_id][current_day]['snack'])
        markup = create_calories_add_or_remove_menu()
    else:
        course_days = CourseDay.objects.filter(user=user).order_by('day')
        progress_text = ''
        for course_day in course_days:
            day_calories = course_day.total_calories
            day_proteins = course_day.total_protein
            progress_text += f'День {course_day.day}: {day_calories} калорий / {day_proteins}г белка\n'
        text = f'🧾 Тут отчет о том, сколько калорий ты употреблял каждый день за весь период:' \
               f'\n\n#21FIT\n\n{progress_text}'
        markup = types.InlineKeyboardMarkup()
        button_back = types.InlineKeyboardButton("Назад", callback_data="back")
        markup.add(button_back)

    return text, markup


def check_correctness(text_from_user):
    text_from_user = text_from_user.split(', ')
    flag = True
    if len(text_from_user) == 4:
        for i in text_from_user:
            if i.isdigit():
                if not -1 < int(i) < 4000:
                    flag = False
            else:
                flag = False
    else:
        flag = False
    return flag


def update_courseday_calories(courseday):
    meals = Meal.objects.filter(course_day=courseday)
    total_calories = sum(meal.calories for meal in meals)
    total_protein = sum(meal.protein for meal in meals)
    total_fat = sum(meal.fat for meal in meals)
    total_carbs = sum(meal.carbs for meal in meals)

    courseday.total_calories = total_calories
    courseday.total_protein = total_protein
    courseday.total_fat = total_fat
    courseday.total_carbs = total_carbs

    courseday.save()


def update_meal(meal, calories, protein):
    meal.calories += calories
    meal.protein += protein

    meal.save()


def clean_query(query):
    return re.sub(r'[^a-zA-Z0-9\sа-яА-Я]', '', query)


def search_food(query):
    url = "https://fs2.tvoydnevnik.com/api2/food_search/search"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }

    cleaned_query = clean_query(query)

    data = {
        "jwt": "false",
        "DeviceSize": "XSmall",
        "DeviceSizeDiary": "XSmall",
        "query[count_on_page]": 5,
        "query[page]": 1,
        "query[name]": cleaned_query,
        "platformId": 101,
    }

    response = requests.post(url, headers=headers, data=data)

    response_dict = json.loads(response.text)

    nutrients_list = []
    nutrients_list_for_me = []
    text = ''
    for i, food_item in enumerate(response_dict["result"]["list"]):
        name = food_item['food']['name']
        nutrients = food_item['food']['nutrientsShort']
        nutrients_list.append(nutrients)
        text += f'{i + 1}: {name}\n'
        nutrients_list_for_me.append(name)

    return text, nutrients_list, nutrients_list_for_me


def get_dish_by_number(dish_list, number):
    if 0 <= number < len(dish_list):
        return dish_list[number]
    else:
        return None


def calculate_nutrients(top5_dishes, right_dish_index, grams):
    chosen_dish_name = top5_dishes[right_dish_index - 1]
    dishes_data = []
    chosen_dish_data = next(dish for dish in dishes_data if dish['Title'] == chosen_dish_name)

    calories = float(chosen_dish_data['Calories']) * grams / 100
    proteins = float(chosen_dish_data['Proteins']) * grams / 100
    fats = float(chosen_dish_data['Fats']) * grams / 100
    carbohydrates = float(chosen_dish_data['Carbohydrates']) * grams / 100

    return {
        'Title': chosen_dish_name,
        'Calories': calories,
        'Proteins': proteins,
        'Fats': fats,
        'Carbohydrates': carbohydrates
    }


def food_choosing_menu(answer, user_id):
    text_answer, data, list_for_me = search_food(answer)
    one_five = InlineKeyboardMarkup()
    button1 = InlineKeyboardButton(text='1', callback_data='1')
    button2 = InlineKeyboardButton(text='2', callback_data='2')
    button3 = InlineKeyboardButton(text='3', callback_data='3')
    button4 = InlineKeyboardButton(text='4', callback_data='4')
    button5 = InlineKeyboardButton(text='5', callback_data='5')

    button6 = InlineKeyboardButton(text='Повторить ввод', callback_data='try_again')
    button7 = InlineKeyboardButton(text='Ввести вручную', callback_data='enter_manually')

    button8 = InlineKeyboardButton(text='Отмена', callback_data='cancel_product')
    one_five.row(button1, button2, button3, button4, button5)
    one_five.add(button6)
    one_five.add(button7)
    one_five.add(button8)
    return text_answer, data, list_for_me, one_five


def one_five_markup(second=False):
    one_five = InlineKeyboardMarkup()
    button1 = InlineKeyboardButton(text='1', callback_data='1')
    button2 = InlineKeyboardButton(text='2', callback_data='2')
    button3 = InlineKeyboardButton(text='3', callback_data='3')
    button4 = InlineKeyboardButton(text='4', callback_data='4')
    button5 = InlineKeyboardButton(text='5', callback_data='5')
    button6 = InlineKeyboardButton(text='Назад', callback_data='cancelamount')
    if second:
        button6 = InlineKeyboardButton(text='Назад к продукту', callback_data='cancelamount1')
    one_five.row(button1, button2, button3, button4, button5)
    one_five.add(button6)
    return one_five


def redact_menu_markup(num):
    markup = InlineKeyboardMarkup()
    lst = [InlineKeyboardButton(text=f'{i}', callback_data=f'{i}') for i in range(1, num + 1)]
    # markup.add(*lst, row_width=3)
    markup.row(*lst)
    button6 = InlineKeyboardButton(text='Назад', callback_data='back')
    markup.add(button6)

    return markup
