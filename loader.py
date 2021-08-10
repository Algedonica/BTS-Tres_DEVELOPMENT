from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.mongo import MongoStorage
from data import config
from data.config import client, user_collection, states_connect
import pymongo

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)


storage = MongoStorage(uri=states_connect)





dp = Dispatcher(bot, storage=storage)
