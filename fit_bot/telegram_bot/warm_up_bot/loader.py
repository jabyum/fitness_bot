from telebot import TeleBot
from .data.config import warm_up_token
from telebot.storage import StateMemoryStorage


bot = TeleBot(warm_up_token, state_storage=StateMemoryStorage())
