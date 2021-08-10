from typing import final
from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
import math
import secrets
import random
from datetime import datetime
from aiogram.types.message import Message
import json
import aiogram_broadcaster
from aiogram_broadcaster import message_broadcaster
from data.config import partner_collection,links_collection,user_collection, staff_collection, settings_collection, pmessages_collection, photos_collection
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, message_id
from loader import dp,bot
from states import ProjectManage,SupportManage, SetupBTSstates
from aiogram.dispatcher import FSMContext
from utils.misc import build_support_menu, reverse_check,get_partner_obj, system_text_parser,issupport, isadmin, support_role_check, xstr, photoparser, parse_message_by_tag_name, get_user_came_from,   get_user_city, linkparser, linkparser_default
from aiogram.types import InputMediaPhoto
from keyboards.default import defaultmenu,operatorshowuser
from keyboards.inline import usersupportchoiceinline, ticket_callback, add_operator_callback, show_support_pages, edit_something_admin, show_cities_pages


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    if staff_collection.find({"staffrole":"owner"}).count()<1:
        html_text="\n".join(
            [
                '<b>Спасибо за приобретение BTS!</b>',
                '',
                'Чтобы начать работу и настроить систему, пожалуйста, подготовьте ваш уникальный код и приготовьтесь его ввести'
            ]
        )
        setupsys= InlineKeyboardMarkup(row_width=1, inline_keyboard=[
            [InlineKeyboardButton(
                text='Давайте начинать!',
                callback_data='initialize_bts_setup'
            )]
        ]) 
        await message.answer(text=html_text,parse_mode='HTML',reply_markup=setupsys)
        await SetupBTSstates.getadmincode.set()

    else:
        if issupport(message.from_user.id) == True:
            
            html_text,supportmenubase=build_support_menu(message.from_user.id)

            await message.answer_photo(photo=photoparser("operatormainmenu"), caption=html_text,parse_mode='HTML',reply_markup=supportmenubase )     
           
            await SupportManage.menu.set()  
        else:
            if user_collection.count_documents({"user_id": message.from_user.id}) == 0 and message.from_user.is_bot==False:
                    
                photoo = settings_collection.find_one({"settings":"mainsettings"})
                photoo_add= photoo["photos_profile"]
                pdasasd = photoo_add[random.randint(0, 14)]

                deeplink = "none"
                deeplink = message.get_args()

                if deeplink!="":
                    actualcity, actualcode, socialnet=linkparser(deeplink)
                else:
                    actualcity, actualcode, socialnet=linkparser_default()

                user_collection.insert_one(
                {"user_id": message.from_user.id,
                "first_name": xstr(message.from_user.first_name),
                "last_name": xstr(message.from_user.last_name),
                "username": xstr(message.from_user.username),
                "callmeas":"none",
                "citytag":actualcode,
                "city":actualcity,
                "came_from": deeplink,
                "when_came": datetime.now(),
                "user_photo":pdasasd,
                "socialnet":socialnet
                })
                html_text="\n".join(
                    [
                        '<b>👋Здравствуйте',
                        '💎 Спасибо, что обратились в «Крипто Консалтинг».</b>',
                        'Здесь мы собрали для вас всю необходимую информацию о криптовалютах и о нашей компании.',
                    ]
                )
                inlinebutt = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
                    [InlineKeyboardButton(
                        text='Хорошо, продолжить',
                        callback_data='start_meeting_user'
                    )],
                ]) 
                await bot.send_message(chat_id= message.from_user.id, text=html_text,parse_mode='HTML', reply_markup=inlinebutt)
                await ProjectManage.startmeeting.set()
            elif message.from_user.is_bot==False:
                html_text="\n".join(
                    [
                        system_text_parser('menu_system_text')
                    ]
                )         
                thisuser=user_collection.find_one({'user_id':message.from_user.id})
                userpartner=get_partner_obj(thisuser['citytag'])
                
                await ProjectManage.menu.set()
                caption_attach="\n".join(
                    [
                        userpartner['datatext']['menu']      
                    ]
                )
                await message.answer_photo(photo=photoparser('usermainmenu'), caption=html_text ,reply_markup=defaultmenu)
                await message.answer_photo(photo=userpartner['menu_photo'], caption=caption_attach)
                
#################################################User Meet#############################################33                    
@dp.callback_query_handler(text='start_meeting_user', state=ProjectManage.startmeeting)
async def start_meeting_user_func(call:types.CallbackQuery):
    html_text="\n".join(
        [
            'Напишите свое имя 😊'
        ]
    )
    await ProjectManage.getnameuser.set()
    await call.message.edit_text(text=html_text, parse_mode='HTML', reply_markup=None)

########################################################Все что ниже должно быть внизу########################################################



@dp.message_handler(state=[ProjectManage.getnameuser])
async def askcityuser_func(message: types.Message):
    user_collection.find_and_modify(
        query={"user_id":message.from_user.id},
        update={"$set":{"callmeas":message.text}}
    )

    html_text="\n".join(
        [
            system_text_parser('menu_system_text')
        ]
    )  
    thisuser=user_collection.find_one({'user_id':message.from_user.id})
    userpartner=get_partner_obj(thisuser['citytag'])
    await ProjectManage.menu.set()
    caption_attach="\n".join(
        [
            userpartner['datatext']['menu']      
        ]
    )
    await ProjectManage.menu.set() 
    await message.answer_photo(photo=photoparser('usermainmenu'), caption=html_text ,reply_markup=defaultmenu)
    await message.answer_photo(photo=userpartner['menu_photo'], caption=caption_attach)




@dp.message_handler(state=ProjectManage.menu)
async def menu_hand(message: types.Message, state: FSMContext):  
    if user_collection.count_documents({"user_id": message.from_user.id}) == 0 and message.from_user.is_bot==False:
        photoo = settings_collection.find_one({"settings":"mainsettings"})
        photoo_add= photoo["photos_profile"]
        pdasasd = photoo_add[random.randint(0, 14)]

        deeplink = "none"
        deeplink = message.get_args()

        if deeplink!="":
            actualcity, actualcode, socialnet=linkparser(deeplink)
        else:
            actualcity, actualcode, socialnet=linkparser_default()

        user_collection.insert_one(
        {"user_id": message.from_user.id,
        "first_name": xstr(message.from_user.first_name),
        "last_name": xstr(message.from_user.last_name),
        "username": xstr(message.from_user.username),
        "callmeas":"none",
        "citytag":actualcode,
        "city":actualcity,
        "came_from": deeplink,
        "when_came": datetime.now(),
        "user_photo":pdasasd,
        "socialnet":socialnet
        })
        html_text="\n".join(
            [
                '<b>👋Здравствуйте',
                '💎 Спасибо, что обратились в «Крипто Консалтинг».</b>',
                'Здесь мы собрали для вас всю необходимую информацию о криптовалютах и о нашей компании.',
            ]
        )
        inlinebutt = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
            [InlineKeyboardButton(
                text='Хорошо, продолжить',
                callback_data='start_meeting_user'
            )],
        ]) 
        await bot.send_message(chat_id= message.from_user.id, text=html_text,parse_mode='HTML', reply_markup=inlinebutt)
        await ProjectManage.startmeeting.set()
    elif issupport(message.from_user.id) == True and reverse_check(message.from_user.id) == True:
        html_text,supportmenubase=build_support_menu(message.from_user.id)
        await state.reset_state()
        await SupportManage.menu.set()  
        #await message.answer(text=html_text,parse_mode='HTML',reply_markup=supportmenubase )
        await message.answer_photo(photo=photoparser("operatormainmenu"), caption=html_text,parse_mode='HTML',reply_markup=supportmenubase )    
    else:    
        thisuser=user_collection.find_one({'user_id':message.from_user.id})
        html_text="\n".join(
            [
                system_text_parser('menu_system_text')
            ]
        )
        await state.reset_state()
        await ProjectManage.menu.set() 

        userpartner=get_partner_obj(thisuser['citytag'])
        await ProjectManage.menu.set()
        caption_attach="\n".join(
            [
                userpartner['datatext']['menu']      
            ]
        )
        await message.answer_photo(photo=photoparser('usermainmenu'), caption=html_text ,reply_markup=defaultmenu)
        await message.answer_photo(photo=userpartner['menu_photo'], caption=caption_attach)




@dp.message_handler(content_types=['photo'], state=SupportManage.menu)
async def parsephoto_hand(message: types.Message, state: FSMContext): 
   
    await message.answer(text=message.photo[0].file_id)
    await bot.send_photo(chat_id=message.from_user.id, photo=message.photo[0].file_id, caption=message.caption)

@dp.message_handler(content_types=['video_note'], state=SupportManage.menu)
async def parse_video_note_hand(message: types.Message, state: FSMContext): 
    await message.answer(text=message.video_note.file_id)
    await bot.send_video_note(chat_id=message.from_user.id, video_note=message.video_note.file_id)


@dp.message_handler(content_types=['video'], state=SupportManage.menu)
async def parse_video_hand(message: types.Message, state: FSMContext): 
    await message.answer(text=message.video.file_id)
    await bot.send_video(chat_id=message.from_user.id, video=message.video.file_id)

@dp.message_handler(content_types=['voice'], state=SupportManage.menu)
async def parse_voice_hand(message: types.Message, state: FSMContext): 
    await message.answer(text=message.voice.file_id)
    await bot.send_voice(chat_id=message.from_user.id, voice=message.voice.file_id)

@dp.message_handler(text='showallphoto', state=SupportManage.menu)
async def parse_video_hand(message: types.Message, state: FSMContext): 
    photosss=photos_collection.find({})
    for x in photosss:
        await bot.send_photo(chat_id=message.from_user.id, photo=x['photo_id'], caption=x['name']+' '+x['photo_id'])

@dp.message_handler(text='createtagg', state=SupportManage.menu)
async def parse_video_hand(message: types.Message, state: FSMContext): 
    await message.answer(text=secrets.token_hex(10)+"{:03d}".format(secrets.randbelow(999)))








@dp.message_handler(state=SupportManage.menu)
async def support_menu_hand(message: types.Message, state: FSMContext):  
    if issupport(message.from_user.id) == True and reverse_check(message.from_user.id) == True:
        html_text,supportmenubase=build_support_menu(message.from_user.id) 
        await state.reset_state()
        await SupportManage.menu.set()     
        await message.answer_photo(photo=photoparser("operatormainmenu"), caption=html_text,parse_mode='HTML',reply_markup=supportmenubase )   
    else:    
        thisuser=user_collection.find_one({'user_id':message.from_user.id})
        html_text="\n".join(
            [
                system_text_parser('menu_system_text')
            ]
        )
        await state.reset_state()
        await ProjectManage.menu.set() 

        userpartner=get_partner_obj(thisuser['citytag'])
        caption_attach="\n".join(
            [
                userpartner['datatext']['menu']      
            ]
        )
        await message.answer_photo(photo=photoparser('usermainmenu'), caption=html_text ,reply_markup=defaultmenu)
        await message.answer_photo(photo=userpartner['menu_photo'], caption=caption_attach)
        
@dp.message_handler(state=SetupBTSstates.getadmincode)
async def blockbts(message: types.Message):
    html_text="\n".join(
            [
                '<b>Спасибо за приобретение BTS!</b>',
                '',
                'Чтобы начать работу и настроить систему, пожалуйста, подготовьте ваш уникальный код и приготовьтесь его ввести'
            ]
    )
    setupsys= InlineKeyboardMarkup(row_width=1, inline_keyboard=[
        [InlineKeyboardButton(
            text='Давайте начинать!',
            callback_data='initialize_bts_setup'
        )]
    ]) 
    await message.answer(text=html_text,parse_mode='HTML',reply_markup=setupsys)
