from telebot.custom_filters import SimpleCustomFilter
from ..data.config import ADMINS
from ..loader import bot


class IsAdminFilter(SimpleCustomFilter):
    key = 'is_admin'

    def __init__(self, bot):
        self._bot = bot

    def check(self, message):
        print(message.from_user.id in ADMINS)
        return message.from_user.id in ADMINS

