from aiogram.dispatcher.filters.state import StatesGroup,State
from aiogram import types
from loader import dp, bot
from data.config import user_collection, ticket_collection, staff_collection, settings_collection, admincode 
from states import ProjectManage,SupportManage,SetupBTSstates
from aiogram.types import CallbackQuery,ReplyKeyboardRemove
from aiogram.utils.callback_data import CallbackData
from utils.misc.logging import logging
from utils.misc import rate_limit
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher import FSMContext


@dp.callback_query_handler(state=SetupBTSstates.getadmincode,text='initialize_bts_setup')
async def initsetupbts(call:CallbackQuery):
    await call.message.edit_text(text="Введите ваш админ-код",reply_markup=None)
    await SetupBTSstates.catchadmincode.set()


############################FOR#####################################
################################TEXT#################################
######################################HANDLERS########################
@dp.message_handler(state=SetupBTSstates.catchadmincode)
async def approveadmincode (message: types.Message, state: FSMContext):
    if message.text==admincode:
        staff_collection.insert_one(
                    {"user_id": message.from_user.id,
                    "first_name": message.from_user.first_name,
                    "last_name": message.from_user.last_name,
                    "username": message.from_user.username,
                    "callmeas": message.from_user.first_name,
                    "staffrole":"owner",
                    "city_code":"none",
                    "notified":"disabled",
                    'soicalnet':'none'})
        settings_collection.insert_one({
            "ondev":True,
            "settings":"mainsettings",
            "current_cities":"none"
        })
        html_text="\n".join(
                [
                    'Это меню. Здесь вы можете приступить к работе'
                ]
            )
        supportmenubase = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
            [InlineKeyboardButton(
                text='Перейти к заявкам',
                callback_data='to_tickets'
            )],
            [InlineKeyboardButton(
                text='Настройки(в разработке)',
                callback_data='to_settings'
            )]
        ]) 
        await state.finish()
        await message.answer(text=html_text,parse_mode='HTML',reply_markup=supportmenubase ) 
        await SupportManage.menu.set()               