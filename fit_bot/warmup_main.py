import time

import os, django, sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fit_bot.settings')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
django.setup()

from telegram_bot.warm_up_bot.bot import start_warmup_bot


if __name__ == '__main__':
    start_warmup_bot()
