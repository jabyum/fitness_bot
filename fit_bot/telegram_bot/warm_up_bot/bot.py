from .loader import bot
from telebot.types import Message
from .handlers import main_menu, send_mails, mailings, export_db
from .handlers.models import create_table


def start_warmup_bot():
    try:
        create_table()
        bot.send_message(305896408, f'Бот запущен! Можете нажать /start')
        bot.infinity_polling()
        # bot.infinity_polling(restart_on_change=True)
        bot.send_message(305896408, f'Бот Выключен!')
    except Exception as E:
        bot.send_message(305896408, f'Ошибка! {E}')



