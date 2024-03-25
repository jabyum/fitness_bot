from telebot import TeleBot
from telebot.storage import StateMemoryStorage
import telebot.apihelper as apihelper
from .data import token

apihelper.TIMEOUT = 45
bot = TeleBot(token, state_storage=StateMemoryStorage())
