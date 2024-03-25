import threading
from datetime import datetime, timedelta
import pytz
import sqlite3
from telebot.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message
from telebot import apihelper
import os

import schedule
import time
from ..loader import bot
from .models import export_data_to_xlsx

ADMINS = [305896408, 58790442]


@bot.message_handler(commands=['export'], func=lambda message: message.from_user.id in ADMINS)
def export(message: Message):
    filename = export_data_to_xlsx()
    with open(filename, 'rb') as file:
        bot.send_document(message.chat.id, file)
    os.remove(filename)
