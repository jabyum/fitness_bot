from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from telebot import types, custom_filters
import pytz
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
from ...loader import bot
from ..mainmenu import just_main_menu, paid_user_main_menu, create_keyboard_markup, get_id
from ...models import PaidUser
from ...states import GeopositionStates, CourseInteraction


def start_timezone_check(message):
    user_id, chat_id = get_id(message=message)
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    location_button = types.KeyboardButton(text="Отправить местоположение",
                                           request_location=True)
    skip_button = types.KeyboardButton(text="Пропустить")
    markup.add(location_button, skip_button)

    pht = 'AgACAgIAAxkBAAEBKgNk4LHizLxJTIHWapQLr7yovpEDuAAC8tIxGyH1AAFL2mf0ocdGuqcBAAMCAAN5AAMwBA'

    bot.send_message(chat_id=user_id,
                   text="*Гео…*\n\nПоделитесь, пожалуйста, своим местоположением для определения часового "
                           "пояса ⏱\n\nТак, мы сможем максимально вовремя отправлять вам *важные напоминалки*",
                   reply_markup=markup,
                   parse_mode='Markdown')
    bot.set_state(user_id, GeopositionStates.initial, chat_id)


def final_message(user_id, chat_id):
    txt = '🔥 *Ура! Вы прошли все этапы*\n\nТеперь мы сможем подобрать стратегию питания и ' \
          'активности лично под вас!\n\n- Что дальше?\n- Узнаете на первом эфире'
    pht = 'AgACAgIAAxkBAAEBKgABZOCxOvu_bwABhiQ3LmwCtQPAC9GJAALv0jEbIfUAAUulCGJFtIWWAgEAAwIAA3kAAzAE'

    markup = create_keyboard_markup('Мой дневник калорий 📆',
                                    'Сколько еще можно ккал?👀', 'Карта программы 🗺', 'Появились вопросики...')
    bot.set_state(user_id, CourseInteraction.initial, chat_id)

    bot.send_photo(chat_id=user_id,
                   caption=txt,
                   photo=pht,
                   parse_mode='Markdown',
                   reply_markup=markup)


@bot.message_handler(state=GeopositionStates.initial, content_types=['location'])
def handle_location(message):
    user_id, chat_id = get_id(message=message)
    latitude = message.location.latitude
    longitude = message.location.longitude
    timezone_finder = TimezoneFinder()
    timezone_name = timezone_finder.timezone_at(lng=longitude, lat=latitude)
    timezone = pytz.timezone(timezone_name)
    PaidUser.objects.filter(user=user_id).update(timezone=timezone)
    bot.send_message(user_id, f"Ваш часовой пояс: {timezone}")
    final_message(chat_id)


@bot.message_handler(func=lambda message: message.text == 'Пропустить')
def skip_location(message):
    user_id, chat_id = get_id(message=message)
    default_timezone = pytz.timezone("Europe/Moscow")
    bot.send_message(message.chat.id, f"Ваш часовой пояс: {default_timezone}")
    PaidUser.objects.filter(user=user_id).update(timezone=default_timezone)
    final_message(user_id, chat_id)


bot.add_custom_filter(custom_filters.StateFilter(bot))
