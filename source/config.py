import os
import logging
import openai
from aiogram import Bot, Dispatcher, executor, types

admin = os.getenv('admin_id')
TOKEN = os.getenv('TOKEN')
openai.api_key = os.getenv('api_key')
logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
