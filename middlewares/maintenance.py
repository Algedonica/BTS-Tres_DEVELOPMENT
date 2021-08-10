from aiogram import types
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from typing import Any, Dict, List, Set
from data.config import settings_collection
from loader import dp, bot

from utils.misc import isowner

class OndevMiddleware(BaseMiddleware):
    async def on_pre_process_message(self, message: types.Message, data: dict):
        getstat = settings_collection.find_one({"settings":"mainsettings"})
        if getstat == None:
            return True
        else:
            if isowner(message.from_user.id) == False:
                getstat = settings_collection.find_one({"settings":"mainsettings"})
                if getstat["ondev"]==False:
                    await message.answer(text='К сожалению, бот поддержки КриптоКонсалтинг недоступен на данный момент из-за технических работ. Пожалуйста, повторите попытку чуть позже. Мы продолжим ровно на том же месте :)')
                    raise CancelHandler()
            return True
    async def on_pre_process_callback_query(self, cq: types.CallbackQuery, data: dict):
        getstat = settings_collection.find_one({"settings":"mainsettings"})
        if getstat == None:
            return True
        else:
            if isowner(cq.from_user.id) == False:
                getstat = settings_collection.find_one({"settings":"mainsettings"})
                if getstat["ondev"]==False:
                    await cq.answer(text='Бот временно недоступен')
                    await bot.send_message(chat_id=cq.from_user.id, text='К сожалению, бот поддержки КриптоКонсалтинг недоступен на данный момент из-за технических работ. Пожалуйста, повторите попытку чуть позже. Мы продолжим ровно на том же месте :)')
                    raise CancelHandler()
            return True           