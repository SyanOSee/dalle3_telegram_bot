# Third-party
from aiogram import Bot, Dispatcher

# Project
import config as cf

# Initialize the bot with the token and set the parse mode to HTML
bot = Bot(cf.bot['token'], parse_mode='html')

# Create a dispatcher for the bot
dispatcher = Dispatcher(bot=bot)