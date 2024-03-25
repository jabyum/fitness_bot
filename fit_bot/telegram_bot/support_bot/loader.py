from telebot import TeleBot
import telebot.apihelper as apihelper
from .data.config import support_token

apihelper.TIMEOUT = 45
bot = TeleBot(support_token)
