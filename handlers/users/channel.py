import secrets
import math
from datetime import datetime
from aiogram import types
from loader import dp, bot
from data.config import channelid,user_collection, ticket_collection, staff_collection, settings_collection, states_collection, pmessages_collection
from states import ProjectManage,SupportManage
from aiogram.types import CallbackQuery,ReplyKeyboardRemove, InputFile, video_note
from aiogram.utils.callback_data import CallbackData
from utils.misc.logging import logging
from utils.misc import rate_limit
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher import FSMContext
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.types import InputMediaPhoto
from utils.misc import group_valid_check,isadmin,support_role_check, xstr, photoparser, parse_message_by_tag_name, getCryptoData, parse_video_by_tag_name

from keyboards.inline import usersupportchoiceinline, ticket_callback, add_operator_callback, show_support_pages, edit_something_admin, show_cities_pages, knowledge_list_call
from keyboards.default import userendsupport,defaultmenu, operatorcontrol,operatorshowuser


@dp.message_handler(state=SupportManage.menu, text='канал')
async def channelgetid(message: types.Message):
    await bot.send_message(chat_id=-1001330118375, text='_',parse_mode='HTML', reply_markup=None)



@dp.message_handler(content_types=['photo','text'],chat_type=types.ChatType.SUPERGROUP, is_forwarded=True)
async def groupcatcher(message: types.Message):

    thismsgid=message.message_id
    thismsggrpid=message.chat.id

    if group_valid_check(thismsggrpid) == True:
        
        getmsg=ticket_collection.find_one({'original_channel':message.forward_from_chat.id, 'original_id':message.forward_from_message_id})
        if getmsg!=None:
            thismsgs=getmsg['extrafield']
            for x in thismsgs:
                if x['type']=='voice':
                    await bot.send_message(chat_id=thismsggrpid, text=x['text'], reply_to_message_id=thismsgid)
                    await bot.send_voice(chat_id=thismsggrpid, voice=x['mediaid'], reply_to_message_id=thismsgid)
                elif x['type']=='photo':
                    await bot.send_photo(chat_id=thismsggrpid, photo=x['mediaid'], caption=x['text'], reply_to_message_id=thismsgid)
                elif x['type']=='video':
                    await bot.send_video(chat_id=thismsggrpid, video=x['mediaid'], caption=x['text'], reply_to_message_id=thismsgid)
                elif x['type']=='video_note':
                    await bot.send_message(chat_id=thismsggrpid, text=x['text'], reply_to_message_id=thismsgid)
                    await bot.send_video_note(chat_id=thismsggrpid, video_note=x['mediaid'], reply_to_message_id=thismsgid)
                elif x['type']=='document':
                    await bot.send_document(chat_id=thismsggrpid, document=x['mediaid'], caption=x['text'], reply_to_message_id=thismsgid)
                else:
                    await bot.send_message(chat_id=thismsggrpid, text=x['text'], reply_to_message_id=thismsgid)
        else:
            getmsg_partner=ticket_collection.find_one({'original_channel_partner':message.forward_from_chat.id, 'original_id_partner':message.forward_from_message_id})
            if getmsg_partner!=None:
                thismsgs=getmsg_partner['extrafield']
                for x in thismsgs:
                    if x['type']=='voice':
                        await bot.send_message(chat_id=thismsggrpid, text=x['text'], reply_to_message_id=thismsgid)
                        await bot.send_voice(chat_id=thismsggrpid, voice=x['mediaid'], reply_to_message_id=thismsgid)
                    elif x['type']=='photo':
                        await bot.send_photo(chat_id=thismsggrpid, photo=x['mediaid'], caption=x['text'], reply_to_message_id=thismsgid)
                    elif x['type']=='video':
                        await bot.send_video(chat_id=thismsggrpid, video=x['mediaid'], caption=x['text'], reply_to_message_id=thismsgid)
                    elif x['type']=='video_note':
                        await bot.send_message(chat_id=thismsggrpid, text=x['text'], reply_to_message_id=thismsgid)
                        await bot.send_video_note(chat_id=thismsggrpid, video_note=x['mediaid'], reply_to_message_id=thismsgid)
                    elif x['type']=='document':
                        await bot.send_document(chat_id=thismsggrpid, document=x['mediaid'], caption=x['text'], reply_to_message_id=thismsgid)
                    else:
                        await bot.send_message(chat_id=thismsggrpid, text=x['text'], reply_to_message_id=thismsgid)