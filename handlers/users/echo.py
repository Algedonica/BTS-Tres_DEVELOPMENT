from re import split
import secrets
import math
from datetime import datetime
from typing import Text
from aiogram import types
from loader import dp, bot
from data.config import inline_materials_collection, links_collection, partner_collection, user_collection, ticket_collection, staff_collection, settings_collection, states_collection, pmessages_collection, channelid
from states import ProjectManage,SupportManage
from aiogram.types import CallbackQuery,ReplyKeyboardRemove, InputFile, message
from aiogram.utils.callback_data import CallbackData
from utils.misc.logging import logging
from utils.misc import rate_limit
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher import FSMContext
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.types import InputMediaPhoto
from utils.misc import build_operatorcontrol,build_userendsupport,build_user_menu, get_text, get_partner_channel,build_support_menu,system_text_parser,get_partner_obj,isadmin,support_role_check, xstr, photoparser, parse_message_by_tag_name, getCryptoData, parse_video_by_tag_name, send_to_channel, get_user_city,   get_user_came_from, check_error_ticket
from aiogram.utils.parts import safe_split_text
from aiogram.dispatcher.handler import CancelHandler
from keyboards.inline import show_ticket_pages,usersupportchoiceinline, ticket_callback, add_operator_callback, show_support_pages, edit_something_admin, show_cities_pages, knowledge_list_call, about_team_call


from aiogram.utils.exceptions import BotBlocked

from PIL import Image, ImageChops,ImageDraw, ImageFont

scheduler = AsyncIOScheduler()
async def clearnotified():
    staff_collection.find_and_modify(
        query={"staffrole":"support", "notified":"notified"},
        update={"$set":{"notified":"none"}}
    )         
scheduler.add_job(clearnotified, 'interval', seconds=180)



#---------------------------about-----us-------------------------------------


#---------------------------about-----us-----end-----------------------------


@dp.message_handler(state=ProjectManage.menu, text=['🗣 Получить консультацию', '🗣 Consultation'])
async def initialize_ticket(message: types.Message):
    html_text="\n".join(
        [
            get_text('user_getconsult_text', message.from_user.id)
        ]
    )
    backbutton=InlineKeyboardMarkup(row_width=1, inline_keyboard=[
        [InlineKeyboardButton(
            text=get_text('user_backtomenu_button_text', message.from_user.id),
            callback_data='userbacktomenu'
        )]
    ])
    await message.answer(text='_',parse_mode='HTML', reply_markup=ReplyKeyboardRemove())
    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id+1)
    await bot.send_message(chat_id=message.from_user.id,text=html_text,parse_mode='HTML', reply_markup=backbutton)
    await ProjectManage.initializingsup.set()

@dp.message_handler(state=ProjectManage.initializingsup)
async def initializing_support (message: types.Message):

    user=user_collection.find_one({"user_id": message.from_user.id})

    ticketid=user['citytag']+'-'+secrets.token_hex(4)+'-'+"{:03d}".format(secrets.randbelow(999))

    extradd={
        "side":"fromuser" ,
        "date": datetime.now(), 
        "text":'<b>❓ Request: </b>'+message.text,
        "from_id":message.from_user.id,
        "message_from_id":message.message_id,
        "type":"text",
        "mediaid":"none",
        "isread":True}


    if ticket_collection.count_documents({"ticketid": ticketid}) == 0 and message.from_user.is_bot==False:
        ticket_collection.insert_one(
        {"ticketid": ticketid,
        "date": datetime.now(),
        "isopen": "created",
        "operator": "none",
        "title": message.text,
        "userid":  message.from_user.id,
        "messagedata":"",
        "original_channel":"",
        "original_id":"",
        "original_channel_partner":"none",
        "original_id_partner":"none",
        "citytag":user['citytag'],
        'extrafield':[extradd]})
    
    html_text="\n".join(
        [
            get_text('user_waitingsupport_text', message.from_user.id),       
            get_text('user_waitingsupport_urid_text', message.from_user.id)+' '+ticketid
        ]
    )
    
    await message.answer(text=html_text,parse_mode='HTML',reply_markup=build_userendsupport(message.from_user.id)   )
    await ProjectManage.awaitingsup.set()

    sups = staff_collection.find({"staffrole":"support","notified":"none","city_code":user['citytag'], 'isreverse':False})
    gotgot = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
        [InlineKeyboardButton(
            text=get_text('user_OKAY_text', message.from_user.id),
            callback_data='ivegotit'
        )]
    ]) 
    for x in sups:
        await bot.send_photo(chat_id=x['user_id'],parse_mode='HTML', reply_markup=gotgot, photo=photoparser('new_question'))



@dp.callback_query_handler(text='userbacktomenu', state=[ProjectManage.preparingquest,ProjectManage.initializingsup,ProjectManage.menu])
async def user_come_to_menu(call:types.CallbackQuery):
    html_text,defaultmenu=build_user_menu(message.from_user.id)   
    await call.message.delete()
    await ProjectManage.menu.set()
    await call.message.answer_photo(photo=photoparser('usermainmenu'), caption=html_text ,reply_markup=defaultmenu)

@dp.callback_query_handler(text='ivegotit', state=[SupportManage.menu, SupportManage.onair])
async def igotiwork(call:CallbackQuery):
    staff_collection.find_one_and_update(
        { "user_id":call.from_user.id, "notified":"none"},
        { "$set": { "notified": "notified" } }
    )
    await call.message.delete()
@dp.message_handler(state=ProjectManage.awaitingsup, text=['✅ Завершить диалог', '✅ End dialogue'])
async def end_support(message: types.Message):
    thisicket=ticket_collection.find_one({"userid": message.from_user.id, "$or":[{'isopen':'onair'},{'isopen':'onpause'}, {'isopen':'created'}]})
    if thisicket!=None:
        counttickets=ticket_collection.find().count()+1

        if thisicket['operator']!='none':
            operatornickname=staff_collection.find_one({'user_id':thisicket['operator']})

            operatorcallmeas=operatornickname['callmeas']
            operatornickname=operatornickname['username']
            if operatornickname=='none':
                operatornickname='No nickname'
            else:
                operatornickname="@"+operatornickname
        else:
            operatornickname='No operator'
            operatorcallmeas='conversation was early concluded by client'

        clientnickname=user_collection.find_one({'user_id':thisicket['userid']})
        clientcallmeas=clientnickname['callmeas']
        clientnickname=clientnickname['username']

        

        if clientnickname=='none':
            clientnickname='No nickname'
        else:
            clientnickname="@"+clientnickname

        datamessagehere = "\n".join(
            [
                '<b>№'+str(counttickets)+' '+thisicket['citytag']+'</b>',
                '<b>'+thisicket['title']+'</b>',
                '🗣 '+clientnickname+' - '+clientcallmeas,
                '<i>'+thisicket['date'].strftime("%d.%m.%Y / %H:%M")+'</i>',
                '',
                '👨‍💻 '+operatornickname+' - '+operatorcallmeas,
                thisicket['ticketid'],
                '',
                '===',
                "🗣 Closed by client",
                "<i>"+datetime.now().strftime("%d.%m.%Y / %H:%M")+"</i>"
            ]
        )
        tomad= "\n".join([
            "Conversation was early concluded by client",
            "<i>"+datetime.now().strftime("%d.%m.%Y / %H:%M")+"</i>"
        ])
        extradd={
            "side":"fromuser" ,
            "date": datetime.now(),
            "text":tomad,
            "from_id":message.from_user.id,
            "message_from_id":message.message_id,
            "type":"text",
            "mediaid":"none",
            "isread":True}



        photos=await bot.get_user_profile_photos(user_id=thisicket['userid'], limit=1)

        if photos.total_count>0:
            photofinal=photos.photos[0][0].file_id

            mesid=await bot.send_photo(chat_id=channelid, caption=datamessagehere, photo=photofinal)   
            channelid_partner=get_partner_channel(thisicket['citytag'])
            if channelid_partner!='none':
                mesid_partner=await bot.send_photo(chat_id=channelid_partner, caption=datamessagehere, photo=photofinal)  
                ticket_collection.update({"userid": message.from_user.id, "$or":[{'isopen':'onair'},{'isopen':'onpause'}, {'isopen':'created'}]},{"$set":{"isopen":"closedbyclient", "messagedata":datamessagehere, 'original_id':mesid['message_id'], 'original_channel':mesid['sender_chat']['id'], 'original_id_partner':mesid_partner['message_id'], 'original_channel_partner':mesid_partner['sender_chat']['id']}, '$addToSet': { 'extrafield': extradd } })
            ticket_collection.update({"userid": message.from_user.id, "$or":[{'isopen':'onair'},{'isopen':'onpause'}, {'isopen':'created'}]},{"$set":{"isopen":"closedbyclient", "messagedata":datamessagehere, 'original_id':mesid['message_id'], 'original_channel':mesid['sender_chat']['id'], 'original_id_partner':'none', 'original_channel_partner':'none',}, '$addToSet': { 'extrafield': extradd } })

        else:
            mesid=await bot.send_message(chat_id=channelid, text=datamessagehere)   
            channelid_partner=get_partner_channel(thisicket['citytag'])
            if channelid_partner!='none':
                mesid_partner=await bot.send_message(chat_id=channelid_partner, text=datamessagehere)
                ticket_collection.update({"userid": message.from_user.id, "$or":[{'isopen':'onair'},{'isopen':'onpause'}, {'isopen':'created'}]},{"$set":{"isopen":"closedbyclient", "messagedata":datamessagehere, 'original_id':mesid['message_id'], 'original_channel':mesid['sender_chat']['id'], 'original_id_partner':mesid_partner['message_id'], 'original_channel_partner':mesid_partner['sender_chat']['id']}, '$addToSet': { 'extrafield': extradd } })
            ticket_collection.update({"userid": message.from_user.id, "$or":[{'isopen':'onair'},{'isopen':'onpause'}, {'isopen':'created'}]},{"$set":{"isopen":"closedbyclient", "messagedata":datamessagehere, 'original_id':mesid['message_id'], 'original_channel':mesid['sender_chat']['id'], 'original_id_partner':'none', 'original_channel_partner':'none',}, '$addToSet': { 'extrafield': extradd } })


        if thisicket['operator']!='none':
            html_text2=get_text('user_clientendedconvers_text', message.from_user.id)
            endinline= InlineKeyboardMarkup(row_width=1, inline_keyboard=[
                [InlineKeyboardButton(
                    text=get_text('user_end_dialogue_text', message.from_user.id),
                    callback_data='operator_end_inline_ticket'
                )]
            ]) 
            await bot.send_photo(chat_id=thisicket['operator'],parse_mode='HTML', photo=photoparser('clientfinished'), reply_markup=ReplyKeyboardRemove())
            await bot.send_message(chat_id=thisicket['operator'], text=html_text2,parse_mode='HTML',reply_markup=endinline)
    html_text,defaultmenu=build_user_menu(message.from_user.id)
    await message.answer_photo(photo=photoparser('operatorticketfinished') ,parse_mode='HTML')
    await message.answer_photo(photo=photoparser('usermainmenu'), caption=html_text,parse_mode='HTML',reply_markup=defaultmenu)
    await ProjectManage.menu.set()



@dp.callback_query_handler(state=SupportManage.onair, text='operator_end_inline_ticket')
async def end_supportbysupport(call: CallbackQuery):
    thisicket=ticket_collection.find_one({"operator": call.from_user.id,"isopen": "onair"}) 
    if thisicket!=None:
        ticket_collection.update({"operator": call.from_user.id, "isopen": "onair"},{"$set":{"isopen":"closedbyoperator"}})
        await bot.send_message(chat_id=channelid, text=thisicket['messagedata'])
        html_text2="\n".join(
            [
                ' ',
            ]
        )
        clientgotomenu= InlineKeyboardMarkup(row_width=1, inline_keyboard=[
            [InlineKeyboardButton(
                text= get_text('support_end_dialogue_button_text', message.from_user.id),
                callback_data='to_client_menu'
            )]
        ]) 
        await bot.send_photo(chat_id=thisicket['userid'],photo=photoparser('operatorticketfinished') ,caption=html_text2,parse_mode='HTML',reply_markup=ReplyKeyboardRemove())
        await bot.send_message(chat_id=thisicket['userid'],text=get_text('user_support_ended_dialogue_text', message.from_user.id),parse_mode='HTML',reply_markup=clientgotomenu)
    html_text,supportmenubase=build_support_menu(call.from_user.id) 
   
    await bot.send_photo(chat_id=call.from_user.id,photo=photoparser("operatormainmenu"), caption=html_text,parse_mode='HTML',reply_markup=supportmenubase ) 
    await call.message.delete()
    await SupportManage.menu.set()   


@dp.callback_query_handler(state=SupportManage.onair, text='operator_end_inline_ticket_error')
async def end_supportbysupport_error(call: CallbackQuery):
    thisicket=ticket_collection.find_one({"operator": call.from_user.id,"isopen": "onair"}) 
    if thisicket!=None:
        

        counttickets=ticket_collection.find().count()+1

        operatornickname=staff_collection.find_one({'user_id':thisicket['operator']})
        operatorcallmeas=operatornickname['callmeas']
        operatornickname=operatornickname['username']

        clientnickname=user_collection.find_one({'user_id':thisicket['userid']})
        clientcallmeas=clientnickname['callmeas']
        clientnickname=clientnickname['username']

        if operatornickname=='none':
            operatornickname='No nickname'
        else:
            operatornickname="@"+operatornickname

        if clientnickname=='none':
            clientnickname='No nickname'
        else:
            clientnickname="@"+clientnickname
        datamessagehere = "\n".join(
            [

                '<b>№'+str(counttickets)+' '+thisicket['citytag']+'</b>',
                '<b>'+thisicket['title']+'</b>',
                '🗣 '+clientnickname+' - '+clientcallmeas,
                '<i>'+thisicket['date'].strftime("%d.%m.%Y / %H:%M")+'</i>',
                '',
                '👨‍💻 '+operatornickname+' - '+operatorcallmeas,
                thisicket['ticketid'],
                '',
                '===',
                "❌ Request closed with an error:",
                "bot banned by client.",
                "<i>"+datetime.now().strftime("%d.%m.%Y / %H:%M")+"</i>"
                
            ]
        )
        tomad= "\n".join([
            "Request closed with an error (bot banned by client) ",
            "<i>"+datetime.now().strftime("%d.%m.%Y / %H:%M")+"</i>"
        ])
        extradd={
            "side":"error",
            "date": datetime.now(),
            "text":tomad,
            "from_id":call.from_user.id,
            "message_from_id":call.message.message_id,
            "type":"text",
            "mediaid":"none",
            "isread":True}


        photos=await bot.get_user_profile_photos(user_id=thisicket['userid'], limit=1)

        if photos.total_count>0:
            photofinal=photos.photos[0][0].file_id

            mesid=await bot.send_photo(chat_id=channelid, caption=datamessagehere, photo=photofinal)
            channelid_partner=get_partner_channel(thisicket['citytag'])
            if channelid_partner!='none':
                mesid_partner=await bot.send_photo(chat_id=channelid_partner, caption=datamessagehere, photo=photofinal)
                ticket_collection.update({"ticketid": thisicket['ticketid'], "isopen": "onair"},{"$set":{"isopen":"botbanned","messagedata":datamessagehere, 'original_id':mesid['message_id'], 'original_channel':mesid['sender_chat']['id'], 'original_id_partner':mesid_partner['message_id'], 'original_channel_partner':mesid_partner['sender_chat']['id']}, '$addToSet': { 'extrafield': extradd }})
            ticket_collection.update({"ticketid": thisicket['ticketid'], "isopen": "onair"},{"$set":{"isopen":"botbanned","messagedata":datamessagehere, 'original_id':mesid['message_id'], 'original_channel':mesid['sender_chat']['id']}, '$addToSet': { 'extrafield': extradd }})

        else:
            mesid=await bot.send_message(chat_id=channelid, text=datamessagehere)
            channelid_partner=get_partner_channel(thisicket['citytag'])
            if channelid_partner!='none':
                mesid_partner=await bot.send_message(chat_id=channelid_partner, text=datamessagehere)
                ticket_collection.update({"ticketid": thisicket['ticketid'], "isopen": "onair"},{"$set":{"isopen":"botbanned","messagedata":datamessagehere, 'original_id':mesid['message_id'], 'original_channel':mesid['sender_chat']['id'], 'original_id_partner':mesid_partner['message_id'], 'original_channel_partner':mesid_partner['sender_chat']['id']}, '$addToSet': { 'extrafield': extradd }})
            ticket_collection.update({"ticketid": thisicket['ticketid'], "isopen": "onair"},{"$set":{"isopen":"botbanned","messagedata":datamessagehere, 'original_id':mesid['message_id'], 'original_channel':mesid['sender_chat']['id']}, '$addToSet': { 'extrafield': extradd }})

        
       

    html_text,supportmenubase=build_support_menu(call.from_user.id)   
   
    await bot.send_photo(chat_id=call.from_user.id,photo=photoparser("operatormainmenu"), caption=html_text,parse_mode='HTML',reply_markup=supportmenubase ) 
    await call.message.delete()
    await SupportManage.menu.set()  


@dp.message_handler(state=SupportManage.onair, text=['❌ Завершить', '❌ End dialogue'])
async def end_supportbysupport(message: types.Message):
    thisicket=ticket_collection.find_one({"operator": message.from_user.id,"isopen": "onair"}) 
    if thisicket!=None:
        counttickets=ticket_collection.find().count()+1

        operatornickname=staff_collection.find_one({'user_id':thisicket['operator']})
        operatorcallmeas=operatornickname['callmeas']
        operatornickname=operatornickname['username']

        clientnickname=user_collection.find_one({'user_id':thisicket['userid']})
        clientcallmeas=clientnickname['callmeas']
        clientnickname=clientnickname['username']

        if operatornickname=='none':
            operatornickname='No nickname'
        else:
            operatornickname="@"+operatornickname

        if clientnickname=='none':
            clientnickname='No nickname'
        else:
            clientnickname="@"+clientnickname

        datamessagehere = "\n".join(
            [
                '<b>№'+str(counttickets)+' '+thisicket['citytag']+'</b>',
                '<b>'+thisicket['title']+'</b>',
                '🗣 '+clientnickname+' - '+clientcallmeas,
                '<i>'+thisicket['date'].strftime("%d.%m.%Y / %H:%M")+'</i>',
                '',
                '👨‍💻 '+operatornickname+' - '+operatorcallmeas,
                thisicket['ticketid'],
                '',
                '===',
                "👨‍💻 Closed by operator",
                "<i>"+datetime.now().strftime("%d.%m.%Y / %H:%M")+"</i>"

            ]
        )
        
        
        html_text2="\n".join(
            [
                ' ',
            ]
        )
        clientgotomenu= InlineKeyboardMarkup(row_width=1, inline_keyboard=[
            [InlineKeyboardButton(
                text=get_text('support_end_dialogue_button_text',message.from_user.id),
                callback_data='to_client_menu'
            )]
        ]) 
        

        await bot.send_photo(chat_id=thisicket['userid'],photo=photoparser('operatorticketfinished') ,caption=html_text2,parse_mode='HTML',reply_markup=ReplyKeyboardRemove())
        await bot.send_message(chat_id=thisicket['userid'],text='Оператор завершил диалог',parse_mode='HTML',reply_markup=clientgotomenu)      

        tomad= "\n".join([
            "Closed by operator",
            "<i>"+datetime.now().strftime("%d.%m.%Y / %H:%M")+"</i>"
        ])
        extradd={
            "side":"fromoperator" ,
            "date": datetime.now(),
            "text":tomad,
            "from_id":message.from_user.id,
            "message_from_id":message.message_id,
            "type":"text",
            "mediaid":"none",
            "isread":True}


        photos=await bot.get_user_profile_photos(user_id=thisicket['userid'], limit=1)

        if photos.total_count>0:
            photofinal=photos.photos[0][0].file_id

            mesid=await bot.send_photo(chat_id=channelid, caption=datamessagehere, photo=photofinal)
            channelid_partner=get_partner_channel(thisicket['citytag'])
            if channelid_partner!='none':
                mesid_partner=await bot.send_photo(chat_id=channelid_partner, caption=datamessagehere, photo=photofinal)
                ticket_collection.update({"ticketid":thisicket['ticketid']},{"$set":{"isopen":"closedbyoperator","messagedata":datamessagehere,'original_id':mesid['message_id'], 'original_channel':mesid['sender_chat']['id'],'original_id_partner':mesid_partner['message_id'], 'original_channel_partner':mesid_partner['sender_chat']['id']},'$addToSet': { 'extrafield': extradd }})
            ticket_collection.update({"ticketid":thisicket['ticketid']},{"$set":{"isopen":"closedbyoperator","messagedata":datamessagehere,'original_id':mesid['message_id'], 'original_channel':mesid['sender_chat']['id']},'$addToSet': { 'extrafield': extradd }})
            

        else:
            mesid=await bot.send_message(chat_id=channelid, text=datamessagehere)
            channelid_partner=get_partner_channel(thisicket['citytag'])
            if channelid_partner!='none':
                mesid_partner=await bot.send_message(chat_id=channelid_partner, text=datamessagehere)
                ticket_collection.update({"ticketid":thisicket['ticketid']},{"$set":{"isopen":"closedbyoperator","messagedata":datamessagehere,'original_id':mesid['message_id'], 'original_channel':mesid['sender_chat']['id'],'original_id_partner':mesid_partner['message_id'], 'original_channel_partner':mesid_partner['sender_chat']['id']},'$addToSet': { 'extrafield': extradd }})
            ticket_collection.update({"ticketid":thisicket['ticketid']},{"$set":{"isopen":"closedbyoperator","messagedata":datamessagehere,'original_id':mesid['message_id'], 'original_channel':mesid['sender_chat']['id']},'$addToSet': { 'extrafield': extradd }})
            
    html_text,supportmenubase=build_support_menu(message.from_user.id)    
    await bot.send_message(chat_id=message.from_user.id,text=get_text('support_endeddialogue_text', message.from_user.id) ,parse_mode='HTML',reply_markup=ReplyKeyboardRemove())
    await bot.send_photo(chat_id=message.from_user.id,photo=photoparser("operatormainmenu"), caption=html_text,parse_mode='HTML',reply_markup=supportmenubase ) 
    
    await SupportManage.menu.set()   

@dp.callback_query_handler(text='to_client_menu', state=ProjectManage.awaitingsup)
async def clientgogotomenucallback(call: CallbackQuery):
    html_text,defaultmenu=build_user_menu(call.from_user.id) 
    await call.message.delete()
    await ProjectManage.menu.set()
    await call.message.answer_photo(photo=photoparser('usermainmenu'), caption=html_text ,reply_markup=defaultmenu)









@dp.callback_query_handler(show_ticket_pages.filter(command='tonewtickets'), state=SupportManage.menu)
async def tonewticketsfunc(call:types.CallbackQuery,callback_data:dict):
    page = callback_data.get("page")
    page = int(page)
    prevpage = page - 1
    nextpage = page + 1

    operator = staff_collection.find_one({"user_id":call.from_user.id})
    newticket=ticket_collection.find({"isopen":"created", "operator":"none", "citytag": {"$in": operator['city_code'][1:]}}).skip((page-1)*5).limit(5)
    opentickets = InlineKeyboardMarkup()
    if newticket.count()>0:
        for x in newticket:
            thisuser = user_collection.find_one({"user_id":x['userid']})
            thisbutton = InlineKeyboardButton(text=str(thisuser['callmeas'])+' ❓ '+x['title'], callback_data=ticket_callback.new("openticket",ticketid=x['ticketid'], operatorid=call.from_user.id)  )
            opentickets.add(thisbutton)

    if prevpage < 1:
        prevtoadd=InlineKeyboardButton(
            text='◀️',
            callback_data=show_ticket_pages.new("tonewtickets",page=1) 
        )
    else:
        prevtoadd=InlineKeyboardButton(
            text='◀️',
            callback_data=show_ticket_pages.new("tonewtickets",page=prevpage) 
        )

    if  math.ceil(newticket.count()/5)==page:
        nexttoadd=InlineKeyboardButton(
            text='▶️',
            callback_data=show_ticket_pages.new("tonewtickets",page=page) 
        )      
    else:
        nexttoadd=InlineKeyboardButton(
            text='▶️',
            callback_data=show_ticket_pages.new("tonewtickets",page=nextpage) 
        )  
    opentickets.add(prevtoadd,nexttoadd)

    opentickets.add(InlineKeyboardButton(text=get_text('support_back_to_requests_button_text',call.from_user.id),callback_data='to_tickets'))

    await call.message.edit_media(media=InputMediaPhoto(media=photoparser("waiting"), caption="<b>"+get_text('support_new_requests_text',call.from_user.id)+": 🗣"+str(newticket.count())+"</b>"), reply_markup=opentickets) 












@dp.callback_query_handler(show_ticket_pages.filter(command='tourpaused'), state=SupportManage.menu)
async def tourpausedticketsfunc(call:types.CallbackQuery,callback_data:dict):
    page = callback_data.get("page")
    page = int(page)
    prevpage = page - 1
    nextpage = page + 1



    operator = staff_collection.find_one({"user_id":call.from_user.id})
    pausedticket=ticket_collection.find({"isopen":"onpause", "operator":call.from_user.id,"citytag": {"$in": operator['city_code'][1:]}}).skip((page-1)*5).limit(5)
    opentickets = InlineKeyboardMarkup()    
    if pausedticket.count()>0:
        for x in pausedticket:
            thisuser = user_collection.find_one({"user_id":x['userid']})
            thisbutton = InlineKeyboardButton(text=str(thisuser['callmeas'])+' ❓ '+x['title'], callback_data=ticket_callback.new("openticket",ticketid=x['ticketid'], operatorid=call.from_user.id)  )
            opentickets.add(thisbutton)

    
    if prevpage < 1:
        prevtoadd=InlineKeyboardButton(
            text='◀️',
            callback_data=show_ticket_pages.new("tourpaused",page=1) 
        )
    else:
        prevtoadd=InlineKeyboardButton(
            text='◀️',
            callback_data=show_ticket_pages.new("tourpaused",page=prevpage) 
        )

    if  math.ceil(pausedticket.count()/5)==page:
        nexttoadd=InlineKeyboardButton(
            text='▶️',
            callback_data=show_ticket_pages.new("tourpaused",page=page) 
        )      
    else:
        nexttoadd=InlineKeyboardButton(
            text='▶️',
            callback_data=show_ticket_pages.new("tourpaused",page=nextpage) 
        )  
    opentickets.add(prevtoadd,nexttoadd)


    opentickets.add(InlineKeyboardButton(text=get_text('support_back_to_requests_button_text',call.from_user.id),callback_data='to_tickets'))

    await call.message.edit_media(media=InputMediaPhoto(media=photoparser("waiting"), caption="<b>"+get_text('support_requests_open_text',call.from_user.id)+": 🗣"+str(pausedticket.count())+"</b>"), reply_markup=opentickets) 







@dp.callback_query_handler(text='to_tickets', state=SupportManage.menu)
async def to_tickets_func(call:types.CallbackQuery):
    await call.answer(cache_time=0)
    inlinekeyb=InlineKeyboardMarkup(row_width=1)
    operator = staff_collection.find_one({"user_id":call.from_user.id})
    created=ticket_collection.count_documents({'isopen':'created', 'operator':'none', "citytag": {"$in": operator['city_code'][1:]}})
    paused=ticket_collection.count_documents({'isopen':'onpause', 'operator':call.from_user.id, "citytag": {"$in":operator['city_code'][1:]}}) 
    updatebutton=InlineKeyboardButton(
        text=get_text('support_requests_update_text',call.from_user.id),
        callback_data="to_tickets"
    )
    inlinekeyb.add(updatebutton)
    if created>0:
        createdbutton=InlineKeyboardButton(
            text=get_text('support_new_requests_text',call.from_user.id),
            callback_data=show_ticket_pages.new("tonewtickets",page=1) 
        )
        inlinekeyb.add(createdbutton)
    if paused>0:
        pausedbutton=InlineKeyboardButton(
            text=get_text('support_requests_open_text',call.from_user.id),
            callback_data=show_ticket_pages.new("tourpaused",page=1) 
        )
        inlinekeyb.add(pausedbutton)
    html_text="\n".join(
        [
            '<b>'+get_text('support_new_requests_text',call.from_user.id)+': 🗣'+ str(created)+'</b>',
            '<b>'+get_text('support_requests_open_text',call.from_user.id)+': 🗣'+str(paused)+'</b>'

        ]
    )
    
    inlinekeyb.add(InlineKeyboardButton(text=get_text('user_backtomenu_button_text',call.from_user.id),callback_data='supportbacktomenu'))
    if created == 0 and paused == 0:
       
        await call.message.edit_media(media=InputMediaPhoto(media=photoparser("silent"), caption=html_text), reply_markup=inlinekeyb) 
    else:
  
        await call.message.edit_media(media=InputMediaPhoto(media=photoparser("waiting"), caption=html_text), reply_markup=inlinekeyb) 
    
         

@dp.callback_query_handler(text='supportbacktomenu', state=SupportManage.menu)
async def supportbacktomenufunc(call:types.CallbackQuery):
    html_text,supportmenubase=build_support_menu(call.from_user.id)
    await call.message.edit_media(media=InputMediaPhoto(media=photoparser("operatormainmenu"), caption=html_text), reply_markup=supportmenubase) 

############################################admin_menu###########################################

@dp.callback_query_handler(text='to_admin_menu', state=SupportManage.menu)
async def adminmenustart(call: types.CallbackQuery):
    html_text=get_text('support_admin_menu_describe_text',call.from_user.id)
    supportmenubase = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
        [InlineKeyboardButton(
            text=get_text('support_admin_menu_operators_button_text',call.from_user.id),
            callback_data='edit_support'
        )],
        [InlineKeyboardButton(
            text=get_text('user_backtomenu_button_text',call.from_user.id),
            callback_data='supportbacktomenu'
        )],
    ])

    await call.message.edit_media(media=InputMediaPhoto(media=photoparser("adminpanel"), caption=html_text), reply_markup=supportmenubase) 




################################################Admin menu - support manage#########################################################
@dp.callback_query_handler(text='edit_support', state=SupportManage.menu)
async def admin_menu_edit_support(call: types.CallbackQuery):
    html_text="\n".join(
        [
            ' '
        ]
    )
    supportmenubase = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
        [InlineKeyboardButton(
            text=get_text('support_admin_menu_edit_support_supports_text',call.from_user.id),
            callback_data=show_support_pages.new("showsuppages",page=1)
        )],
        [InlineKeyboardButton(
            text=get_text('support_admin_menu_edit_support_add_text',call.from_user.id),
            switch_inline_query='add_operator'
        )],
        [InlineKeyboardButton(
            text=get_text('support_admin_menu_edit_support_back_text',call.from_user.id),
            callback_data='to_admin_menu'
        )],
    ])
    await call.message.edit_media(media=InputMediaPhoto(photoparser('operatormanage'), caption=html_text), reply_markup=supportmenubase)







@dp.callback_query_handler(show_support_pages.filter(command='showsuppages'), state=SupportManage.menu)
async def system_operator_check_list_func(call: types.CallbackQuery, callback_data:dict):
    page = callback_data.get("page")
    page = int(page)
    prevpage = page - 1
    nextpage = page + 1

    inlinekeys = InlineKeyboardMarkup(row_width=2)
    x=staff_collection.find({"staffrole":"support"}).skip((page-1)*5).limit(5)

    for i in x:
        inlinekeys.add(InlineKeyboardButton(text=i["callmeas"]+' '+i["first_name"]+' ('+support_role_check(i['user_id'])+')', callback_data=show_support_pages.new("openoperator",page=i['user_id'])))
    
    
    if prevpage < 1:
        prevtoadd=InlineKeyboardButton(
            text='◀️',
            callback_data=show_support_pages.new("showsuppages",page=1)
        )
    else:
        prevtoadd=InlineKeyboardButton(
            text='◀️',
            callback_data=show_support_pages.new("showsuppages",page=prevpage)
        )

    if  math.ceil(x.count()/5)==page:
        nexttoadd=InlineKeyboardButton(
            text='▶️',
            callback_data=show_support_pages.new("showsuppages",page=page)
        )      
    else:
        nexttoadd=InlineKeyboardButton(
            text='▶️',
            callback_data=show_support_pages.new("showsuppages",page=nextpage)
        )  
    inlinekeys.add(prevtoadd,nexttoadd)
    inlinekeys.add(InlineKeyboardButton(text=get_text('support_admin_menu_edit_support_back_text',call.from_user.id),callback_data='to_admin_menu'))  
    await call.message.edit_media(media=InputMediaPhoto(photoparser('operatorlist'), caption=get_text('support_admin_menu_showsup_pages_text',call.from_user.id)+'<b>'+str(page)+'</b>'), reply_markup=inlinekeys)
 


@dp.callback_query_handler(show_support_pages.filter(command='openoperator'), state=SupportManage.menu)
async def system_operator_open_func(call: types.CallbackQuery, callback_data:dict):
    x = staff_collection.find_one({"user_id" : int(callback_data.get("page"))})
    html_text="\n".join(
        [
            get_text('support_am_es_menu_opername_text',call.from_user.id)+str(x['user_id'])+'">'+x["first_name"]+'</a>',
            get_text('support_am_es_menu_callmeas_text',call.from_user.id)+x['callmeas'],
            get_text('support_am_es_menu_rights_text',call.from_user.id)+str(support_role_check(x['user_id'])),
            get_text('support_am_es_menu_partners_text',call.from_user.id)+str(x["city_code"][1:])
        ]
    )
    operatorbuttons = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
        [InlineKeyboardButton(
            text=get_text('support_am_es_change_name_button_text',call.from_user.id),
            callback_data=show_support_pages.new('operator_change_name',page=x["user_id"])
        )],
        [InlineKeyboardButton(
            text=get_text('support_am_es_partner_tags_button_text',call.from_user.id),
            callback_data=show_support_pages.new("changecityoperator",page=x["user_id"])
        )],
        [InlineKeyboardButton(
            text=get_text('support_am_es_rights_button_text',call.from_user.id)+str(support_role_check(x['user_id'])),
            callback_data=show_support_pages.new("changepassoperator",page=x["user_id"])
        )],
        [InlineKeyboardButton(
            text=get_text('support_am_es_change_photo_button_text',call.from_user.id),
            callback_data=show_support_pages.new("ch_ph_oper",page=x["user_id"])
        )],
        [InlineKeyboardButton(
            text=get_text('remove_text',call.from_user.id),
            callback_data=show_support_pages.new("deleteoperatorinit",page=x["user_id"])
        )],
        [InlineKeyboardButton(
            text=get_text('support_am_es_back_to_operatorslist_button_text',call.from_user.id),
            callback_data=show_support_pages.new("showsuppages",page=1)
        )]
    ])
    phav=x['photo_avatar']
    if phav=='none':
        phav=photoparser('nameroletags')
    await call.message.edit_media(media=InputMediaPhoto(phav, caption=html_text, parse_mode='HTML'), reply_markup=operatorbuttons)


@dp.callback_query_handler(show_support_pages.filter(command='deleteoperatorinit'), state=SupportManage.menu)
async def delete_operator_init(call: types.CallbackQuery, callback_data:dict):
    await call.answer(cache_time=1)
    x = staff_collection.find_one({"user_id" : int(callback_data.get("page"))}) 
    html_text="\n".join(
        [
            ' '
        ]
    )
    operatorbuttons = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
        [InlineKeyboardButton(
            text=get_text('support_remove_yes_button_text',call.from_user.id),
            callback_data=show_support_pages.new('deleteoperatoryes',page=x["user_id"])
        )],
        [InlineKeyboardButton(
            text=get_text('support_remove_no_button_text',call.from_user.id),
            callback_data=show_support_pages.new("openoperator",page=x["user_id"])
        )]
    ])

    await call.message.edit_media(media=InputMediaPhoto(photoparser('deleteoperatorask'), caption=html_text), reply_markup=operatorbuttons)


@dp.callback_query_handler(show_support_pages.filter(command='deleteoperatoryes'), state=SupportManage.menu)
async def delete_operator_done(call: types.CallbackQuery, callback_data:dict):
    await call.answer(cache_time=1)
    staff_collection.remove({"user_id" : int(callback_data.get("page"))}) 

    states_collection.find_one_and_update(
        { "user":int(callback_data.get("page")) },
        {"$set":{ "state":'ProjectManage:menu' }}
    )

    html_text="\n".join(
        [
            ' '
        ]
    )
    operatorbuttons = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
        [InlineKeyboardButton(
            text=get_text('support_am_es_back_to_operatorslist_button_text',call.from_user.id),
            callback_data=show_support_pages.new('showsuppages',page=1)
        )],
    ])

    await call.message.edit_media(media=InputMediaPhoto(photoparser('deleteoperatorask'), caption=html_text), reply_markup=operatorbuttons)


@dp.callback_query_handler(show_support_pages.filter(command='changepassoperator'), state=SupportManage.menu)
async def system_change_role(call: types.CallbackQuery, callback_data:dict):
    await call.answer(cache_time=1)
    x = staff_collection.find_one({"user_id" : int(callback_data.get("page"))})

    if x["role"] == "1":
        staff_collection.find_and_modify( 
            query={"user_id":x["user_id"]}, 
            update={ "$set": { 'role': "2"} }
            )
    elif x["role"] == "2":
        staff_collection.find_and_modify( 
            query={"user_id":x["user_id"]}, 
            update={ "$set": { 'role': "1"}}
            )        
    x = staff_collection.find_one({"user_id" : int(callback_data.get("page"))})


    
    html_text="\n".join(
        [
            get_text('support_am_es_menu_opername_text',call.from_user.id)+str(x['user_id'])+'">'+x["first_name"]+'</a>',
            get_text('support_am_es_menu_callmeas_text',call.from_user.id)+x['callmeas'],
            get_text('support_am_es_menu_rights_text',call.from_user.id)+str(support_role_check(x['user_id'])),
            get_text('support_am_es_menu_partners_text',call.from_user.id)+str(x["city_code"][1:])
        ]
    )
    operatorbuttons = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
        [InlineKeyboardButton(
            text=get_text('support_am_es_change_name_button_text',call.from_user.id),
            callback_data=show_support_pages.new('operator_change_name',page=x["user_id"])
        )],
        [InlineKeyboardButton(
            text=get_text('support_am_es_partner_tags_button_text',call.from_user.id),
            callback_data=show_support_pages.new("changecityoperator",page=x["user_id"])
        )],
        [InlineKeyboardButton(
            text=get_text('support_am_es_rights_button_text',call.from_user.id)+str(support_role_check(x['user_id'])),
            callback_data=show_support_pages.new("changepassoperator",page=x["user_id"])
        )],
        [InlineKeyboardButton(
            text=get_text('support_am_es_change_photo_button_text',call.from_user.id),
            callback_data=show_support_pages.new("ch_ph_oper",page=x["user_id"])
        )],
        [InlineKeyboardButton(
            text=get_text('remove_text',call.from_user.id),
            callback_data=show_support_pages.new("deleteoperatorinit",page=x["user_id"])
        )],
        [InlineKeyboardButton(
            text=get_text('support_am_es_back_to_operatorslist_button_text',call.from_user.id),
            callback_data=show_support_pages.new("showsuppages",page=1)
        )]
    ])
    phav=x['photo_avatar']
    if phav=='none':
        phav=photoparser('nameroletags')
    await call.message.edit_media(media=InputMediaPhoto(phav, caption=html_text, parse_mode='HTML'), reply_markup=operatorbuttons)



#======Operator_change_photo

@dp.callback_query_handler(show_support_pages.filter(command='ch_ph_oper'), state=SupportManage.menu)
async def system_operator_photochange_func(call: types.CallbackQuery, callback_data:dict, state: FSMContext): 
    await call.answer(cache_time=1)
    html_text=get_text('support_am_es_change_photo_oper_text',call.from_user.id)
     
    operatorbuttons = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
        [InlineKeyboardButton(
            text=get_text('support_am_es_abort_and_return_text',call.from_user.id),
            callback_data=show_support_pages.new('op_ch_ph_canc',page=int(callback_data.get("page")))
        )]
    ])

    await SupportManage.changeoperatorphoto.set()
    await state.update_data(operph=int(callback_data.get("page")))
    await call.message.edit_media(media=InputMediaPhoto(photoparser('operatormainmenu'), caption=html_text, parse_mode='HTML'), reply_markup=operatorbuttons)


@dp.callback_query_handler(show_support_pages.filter(command='op_ch_ph_canc'), state=SupportManage.changeoperatorphoto)
async def system_operator_photochange_canc_func(call: types.CallbackQuery, callback_data:dict, state: FSMContext): 
    x = staff_collection.find_one({"user_id" : int(callback_data.get("page"))})

    html_text="\n".join(
        [
            get_text('support_am_es_menu_opername_text',call.from_user.id)+str(x['user_id'])+'">'+x["first_name"]+'</a>',
            get_text('support_am_es_menu_callmeas_text',call.from_user.id)+x['callmeas'],
            get_text('support_am_es_menu_rights_text',call.from_user.id)+str(support_role_check(x['user_id'])),
            get_text('support_am_es_menu_partners_text',call.from_user.id)+str(x["city_code"][1:])
        ]
    )
    operatorbuttons = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
        [InlineKeyboardButton(
            text=get_text('support_am_es_change_name_button_text',call.from_user.id),
            callback_data=show_support_pages.new('operator_change_name',page=x["user_id"])
        )],
        [InlineKeyboardButton(
            text=get_text('support_am_es_partner_tags_button_text',call.from_user.id),
            callback_data=show_support_pages.new("changecityoperator",page=x["user_id"])
        )],
        [InlineKeyboardButton(
            text=get_text('support_am_es_rights_button_text',call.from_user.id)+str(support_role_check(x['user_id'])),
            callback_data=show_support_pages.new("changepassoperator",page=x["user_id"])
        )],
        [InlineKeyboardButton(
            text=get_text('support_am_es_change_photo_button_text',call.from_user.id),
            callback_data=show_support_pages.new("ch_ph_oper",page=x["user_id"])
        )],
        [InlineKeyboardButton(
            text=get_text('remove_text',call.from_user.id),
            callback_data=show_support_pages.new("deleteoperatorinit",page=x["user_id"])
        )],
        [InlineKeyboardButton(
            text=get_text('support_am_es_back_to_operatorslist_button_text',call.from_user.id),
            callback_data=show_support_pages.new("showsuppages",page=1)
        )]
    ])
    phav=x['photo_avatar']
    if phav=='none':
        phav=photoparser('nameroletags')
    await SupportManage.menu.set()
    await call.message.edit_media(media=InputMediaPhoto(phav, caption=html_text, parse_mode='HTML'), reply_markup=operatorbuttons)


@dp.message_handler(content_types=['photo'],state=SupportManage.changeoperatorphoto)
async def system_operator_photoget_func(message: types.Message, state: FSMContext):
    data = await state.get_data()
    operatorid = data.get("operph")
    thisphoto=message.photo[0].file_id

    staff_collection.find_one_and_update(
        { "user_id":operatorid },
        {"$set":{ "photo_avatar":thisphoto }}
    )

    x = staff_collection.find_one({"user_id" : operatorid})

    html_text="\n".join(
        [
            get_text('support_am_es_menu_opername_text',message.from_user.id)+str(x['user_id'])+'">'+x["first_name"]+'</a>',
            get_text('support_am_es_menu_callmeas_text',message.from_user.id)+x['callmeas'],
            get_text('support_am_es_menu_rights_text',message.from_user.id)+str(support_role_check(x['user_id'])),
            get_text('support_am_es_menu_partners_text',message.from_user.id)+str(x["city_code"][1:])
        ]
    )
    operatorbuttons = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
        [InlineKeyboardButton(
            text=get_text('support_am_es_change_name_button_text',message.from_user.id),
            callback_data=show_support_pages.new('operator_change_name',page=x["user_id"])
        )],
        [InlineKeyboardButton(
            text=get_text('support_am_es_partner_tags_button_text',message.from_user.id),
            callback_data=show_support_pages.new("changecityoperator",page=x["user_id"])
        )],
        [InlineKeyboardButton(
            text=get_text('support_am_es_rights_button_text',message.from_user.id)+str(support_role_check(x['user_id'])),
            callback_data=show_support_pages.new("changepassoperator",page=x["user_id"])
        )],
        [InlineKeyboardButton(
            text=get_text('support_am_es_change_photo_button_text',message.from_user.id),
            callback_data=show_support_pages.new("ch_ph_oper",page=x["user_id"])
        )],
        [InlineKeyboardButton(
            text=get_text('remove_text',message.from_user.id),
            callback_data=show_support_pages.new("deleteoperatorinit",page=x["user_id"])
        )],
        [InlineKeyboardButton(
            text=get_text('support_am_es_back_to_operatorslist_button_text',message.from_user.id),
            callback_data=show_support_pages.new("showsuppages",page=1)
        )]
    ])

    phav=x['photo_avatar']
    if phav=='none':
        phav=photoparser('nameroletags')
    await SupportManage.menu.set()
    await message.answer_photo(photo=phav, caption=html_text, reply_markup=operatorbuttons, parse_mode='HTML')
#======Operator_change_photo_end







#=======Operator_change_cities_array

@dp.callback_query_handler(show_support_pages.filter(command='changecityoperator'), state=SupportManage.menu)
async def system_operator_city_change_func(call: types.CallbackQuery, callback_data:dict):
    x = staff_collection.find_one({"user_id" : int(callback_data.get("page"))})
    inlinekeys = InlineKeyboardMarkup(row_width=2)
    cities = x["city_code"]
    
    cities_in_sys = partner_collection.find({})
    for i in cities_in_sys:
        galka=""
        deleteoradd="1"
        if i['system_tag'] in cities:
            galka="✔️"
            deleteoradd="0"
        inlinekeys.add(InlineKeyboardButton(text=galka+i["city_name"]+' : '+i["system_tag"], callback_data=edit_something_admin.new('ecu',i["system_tag"],deleteoradd,int(callback_data.get("page")) )))
    inlinekeys.add(InlineKeyboardButton(text=get_text('support_am_es_back_to+oper_button_text',call.from_user.id),callback_data=show_support_pages.new("openoperator",page=int(callback_data.get("page")))))
    await call.message.edit_media(media=InputMediaPhoto(photoparser('operatorcitiesaccess'), caption=' '), reply_markup=inlinekeys)

@dp.callback_query_handler(edit_something_admin.filter(command='ecu'), state=SupportManage.menu)
async def system_operator_city_change_and_update_func(call: types.CallbackQuery, callback_data:dict):
    await call.answer(cache_time=1)
    if callback_data.get("deleteoradd") == "1":
        
        staff_collection.find_and_modify( 
            query={"user_id":int(callback_data.get("userid"))}, 
            update={ "$push": { 'city_code': callback_data.get("something") }}
            )
    elif callback_data.get("deleteoradd") == "0":
       
        staff_collection.find_and_modify( 
            query={"user_id":int(callback_data.get("userid"))}, 
            update={ "$pull": { 'city_code': callback_data.get("something") }}
            )
    x = staff_collection.find_one({"user_id" : int(callback_data.get("userid"))})
    inlinekeys = InlineKeyboardMarkup(row_width=2)
    cities = x["city_code"]
    
    cities_in_sys = partner_collection.find({})

    for i in cities_in_sys:
        galka=""
        deleteoradd="1"
        if i['system_tag'] in cities:
            galka="✔️"
            deleteoradd="0"
        inlinekeys.add(InlineKeyboardButton(text=galka+i["city_name"]+' : '+i["system_tag"], callback_data=edit_something_admin.new('ecu',i["system_tag"],deleteoradd,int(callback_data.get("userid")) )))
    inlinekeys.add(InlineKeyboardButton(text=get_text('support_am_es_back_to+oper_button_text',call.from_user.id),callback_data=show_support_pages.new("openoperator",page=int(callback_data.get("userid")))))

    await call.message.edit_media(media=InputMediaPhoto(photoparser('operatorcitiesaccess'), caption=' '), reply_markup=inlinekeys)

#=======Operator_change_cities_array_end



@dp.callback_query_handler(show_support_pages.filter(command='operator_change_name'), state=SupportManage.menu)
async def operator_change_name_support(call: types.CallbackQuery,state: FSMContext, callback_data:dict):
    html_text="\n".join(
        [
            ' '
        ]
    )
    await SupportManage.changeoperatorname.set()
    await state.update_data(operatorid=int(callback_data.get("page")))
    await call.message.edit_media(media=InputMediaPhoto(photoparser('operatorchangename'), caption=html_text), reply_markup=None)

@dp.message_handler(state=SupportManage.changeoperatorname)
async def operator_write_new_name_support(message: types.Message, state: FSMContext):
    data = await state.get_data()
    operid = data.get("operatorid")
    staff_collection.find_and_modify( 
            query={"user_id":operid}, 
            update={ "$set": { 'callmeas':message.text }}
            )
    await state.reset_state()
    await SupportManage.menu.set()
    inlinekeys = InlineKeyboardMarkup(row_width=2)
    inlinekeys.add(InlineKeyboardButton(text=get_text('support_am_es_back_to+oper_button_text',message.from_user.id),callback_data=show_support_pages.new("openoperator",page=operid)))
    await message.answer_photo(photo=photoparser("operatornameupdated"), caption=" ", reply_markup=inlinekeys)
  
# ----------------здесь инлайн функции-----------------------
@dp.inline_handler(text="add_operator", state=SupportManage.menu)
async def initialize_adding_operator_tosys(query: types.InlineQuery):
    if isadmin(query.from_user.id)==False:
        await query.answer(
            results=[],
            switch_pm_text='Access denied.',
            cache_time=0
           
        )
        return  
    supportmenubase = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
        [InlineKeyboardButton(
            text="I'm in!",
            callback_data=add_operator_callback.new("addoperatorfactory",operator_role='1')
        )]
    ])
    await query.answer(
        results=[
            types.InlineQueryResultArticle(
                id="1",
                title='Make this user operator',
                input_message_content=types.InputMessageContent(message_text="You are offered to become an operator. If you agree, press the button below:"),
                reply_markup=supportmenubase
            )
        ],
        cache_time=0
    )  

@dp.inline_handler(text="invite", state='*')
async def generate_agent_button(query: types.InlineQuery):


    this_agent=staff_collection.find_one({'user_id':query.from_user.id})
    this_agent_partners=links_collection.find({'citycode': {'$in': this_agent['city_code'][1:]}, 'additional':'default'})
    results_arr=[]
    i=1
    if this_agent!=None and this_agent_partners!=None:
        for x in this_agent_partners: 
            supportmenubase = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
                [InlineKeyboardButton(
                    text=get_text('support_inline_jumptobot_button_text',query.from_user.id),
                    url='https://t.me/btstrestestbot?start='+x['uniquename']
                )]
            ])
            toadd=types.InlineQueryResultArticle(
                    id=i,
                    title=x['uniquename'],
                    description=x['citycode']+'-'+x['city'],
                    input_message_content=types.InputMessageContent(message_text=get_text('support_inline_invite_text',query.from_user.id), parse_mode='HTML'),
                    reply_markup=supportmenubase,
                    
                )
            results_arr.append(toadd)
            i=i+1


        await query.answer(
            results=results_arr,
            cache_time=0
        )





# ----------------здесь инлайн функции конец-----------------------
@dp.callback_query_handler(add_operator_callback.filter(command='addoperatorfactory'), state=[ProjectManage.menu, None])
async def providing_adding_operator_tosys(call:types.CallbackQuery, callback_data:dict):
    
    getoperator=staff_collection.find_one({"user_id":call.from_user.id})
    if getoperator==None:
        staff_collection.insert_one(
        {"user_id": call.from_user.id,
        "first_name":xstr(call.from_user.first_name),
        "last_name":xstr(call.from_user.last_name),
        "username": xstr(call.from_user.username),
        "staffrole": "support",
        "notified": "none",
        "city_code":['none'],
        "callmeas":'none',
        "role":callback_data.get("operator_role"),
        'photo_avatar':'none',
        'isreverse':False,
        'lang_code':'en'})
        html_text=get_text('support_registred_as_operator_text',call.from_user.id)
        await bot.edit_message_text(inline_message_id=call.inline_message_id,text=html_text, parse_mode='HTML', reply_markup=None)
    else:
        html_text=get_text('support_already_registred_as_operator_text',call.from_user.id)
        await bot.edit_message_text(inline_message_id=call.inline_message_id,text=html_text, parse_mode='HTML', reply_markup=None)
    




######################################################talksupport##########################################
@dp.callback_query_handler(ticket_callback.filter(command='openticket'), state=SupportManage.menu)
async def showcard(call:types.CallbackQuery, callback_data:dict):
    await call.answer(cache_time=1)
    thisicket=ticket_collection.find_one({"ticketid":callback_data.get("ticketid")})
    thisuser = user_collection.find_one({"user_id":thisicket['userid']})
    x=''
    if thisuser['username']!='none':
        x=' (@'+thisuser['username']+')'
    html_text="\n".join(
        [
            '<b>'+get_text('support_ticket_id_text',call.from_user.id)+thisicket["ticketid"]+'</b> ',
            '<b>'+thisuser['callmeas']+x+':</b> '+thisicket['title'],
            '<b>'+get_text('support_partner_info_ticket_text',call.from_user.id)+thisuser['city']
        ]
    )        
    inlinekeyb=InlineKeyboardMarkup(row_width=1, inline_keyboard=[
        [InlineKeyboardButton(
            text=get_text('support_jumptoconversation_button_text',call.from_user.id),
            callback_data=ticket_callback.new("jumptoclient",ticketid=thisicket['ticketid'], operatorid=callback_data.get("operatorid"))
        )],
        [
        InlineKeyboardButton(
            text=get_text('back_button_text',call.from_user.id),
            callback_data='tonewtickets'
        ),]
    ])
    photos=await bot.get_user_profile_photos(user_id=thisicket['userid'], limit=1)

    if photos.total_count>0:
        photofinal=photos.photos[0][0].file_id
    else:
        photofinal=thisuser['user_photo']
    
    await call.message.edit_media(media=InputMediaPhoto(media=photofinal, caption=html_text), reply_markup=inlinekeyb)


@dp.callback_query_handler(ticket_callback.filter(command='jumptoclient'), state=SupportManage.menu)
async def jumptothis(call:types.CallbackQuery, callback_data:dict):
    thisicket=ticket_collection.find_one({"ticketid":callback_data.get("ticketid")})
    thisoperator = staff_collection.find_one({"user_id":call.from_user.id})
    thisuser = user_collection.find_one({"user_id":thisicket['userid']})
    html_text="\n".join(
        [
            get_text('support_conversation_started_text',call.from_user.id),
            ' ',
            '<b>🗣️ '+thisuser['callmeas']+'</b> ',
            get_text('support_requestisstarted_text',call.from_user.id)+thisicket['title'],
        ]
    )

    tomsas="\n".join(
            [
                get_text('user_operator_connected_text',thisicket['userid'])+" <i>("+datetime.now().strftime("%d.%m.%Y / %H:%M")+")</i>"
            ]
        )
    extradd={
        "side":"fromoperator" ,
        "date": datetime.now(), 
        "text":tomsas,
        "from_id":call.from_user.id,
        "message_from_id":call.message.message_id,
        "type":"text",
        "mediaid":"none",
        "isread":True}


    if thisicket["isopen"]=="created":
        if thisoperator['photo_avatar']!='none':
            try:
                
                await bot.send_photo(chat_id=thisicket['userid'],caption='👨‍💻 <b>'+thisoperator['callmeas']+'</b> '+get_text('user_operator_just_connected_text',thisicket['userid']),parse_mode='HTML', photo=thisoperator['photo_avatar'])
            except:
                error_ticket= await check_error_ticket(thisicket['ticketid'])
                await call.answer(text=error_ticket, cache_time=0, show_alert=True)
                await call.message.delete()
                opentickets = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
                    [
                    InlineKeyboardButton(text=get_text('support_back_to_requests_button_text',call.from_user.id),callback_data='to_tickets')]
                    
                ])
                

                await bot.send_photo(chat_id=call.from_user.id,parse_mode='HTML', photo=photoparser('clientfinished'), reply_markup=opentickets)
                raise CancelHandler()
        else:    
            try:
               
                await bot.send_message(chat_id=thisicket['userid'],text='👨‍💻 <b>'+thisoperator['callmeas']+'</b> '+get_text('user_operator_just_connected_text',thisicket['userid']),parse_mode='HTML')
            except:
                error_ticket= await check_error_ticket(thisicket['ticketid'])
               
                await call.answer(text=error_ticket, cache_time=0, show_alert=True)
                await call.message.delete()
                opentickets = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
                    [
                    InlineKeyboardButton(text=get_text('support_back_to_requests_button_text',call.from_user.id),callback_data='to_tickets')]
                ])
                

                await bot.send_photo(chat_id=call.from_user.id,parse_mode='HTML', photo=photoparser('clientfinished'), reply_markup=opentickets)

                raise CancelHandler()
    elif thisicket["isopen"]=="onair":

        await call.answer(text=get_text('support_another_operator_alreadyonair_text',call.from_user.id), cache_time=0, show_alert=True)
        await call.message.delete()
        opentickets = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
            [
            InlineKeyboardButton(text=get_text('support_back_to_requests_button_text',call.from_user.id),callback_data='to_tickets')]
        ])
        

        await bot.send_photo(chat_id=call.from_user.id,parse_mode='HTML', photo=photoparser('clientfinished'), reply_markup=opentickets)
        raise CancelHandler()

    

    await call.message.delete()
    
    
    await bot.send_photo(chat_id=call.from_user.id,caption=html_text,parse_mode='HTML', reply_markup=build_operatorcontrol(call.from_user.id),photo=photoparser('changed'))
    
    
    msgs=ticket_collection.find_one({"ticketid":callback_data.get("ticketid"),"$or":[{'isopen':'created'},{'isopen':'onpause'}]})
    lostmsgs=msgs['extrafield']
    for lm in lostmsgs:
        if lm['isread']==False:


            if lm['type']=='voice':
                await bot.send_voice(chat_id=call.from_user.id, voice=lm['mediaid'])
            elif lm['type']=='photo':
                await bot.send_photo(chat_id=call.from_user.id, photo=lm['mediaid'], caption=lm['text'])
            elif lm['type']=='video':
                await bot.send_video(chat_id=call.from_user.id, video=lm['mediaid'], caption=lm['text'])
            elif lm['type']=='video_note':
                await bot.send_video_note(chat_id=call.from_user.id, video_note=lm['mediaid'])
            elif lm['type']=='document':
                await bot.send_document(chat_id=call.from_user.id, document=lm['mediaid'], caption=lm['text'])
            else:
                await bot.send_message(chat_id=call.from_user.id, text=lm['text'], parse_mode='HTML')
            

    ticket_collection.find_one_and_update(
        filter={"ticketid":callback_data.get("ticketid"), "$or":[{'isopen':'created'},{'isopen':'onpause'}]},
        update={"$set":{"extrafield.$[].isread": True}  }
    )
    ticket_collection.find_one_and_update(
        filter={"ticketid":callback_data.get("ticketid"), "$or":[{'isopen':'created'},{'isopen':'onpause'}]},
        update={"$set":{"isopen":"onair","operator":call.from_user.id,},'$addToSet': { 'extrafield': extradd }  }
    )
    
    await SupportManage.onair.set()
    await call.answer(cache_time=0)

@dp.message_handler(state=SupportManage.onair, text=['🗣 Переключиться', '🗣 Shift out'])
async def changeticket_supportbysupport(message: types.Message):     
    datamessagehere = "\n".join(
        [
            get_text('support_operator_paused_conversation_text',message.from_user.id)+" <i>("+datetime.now().strftime("%d.%m.%Y / %H:%M")+")</i>"
        ]
    ) 
    extradd={
            "side":"fromoperator" ,
            "date": datetime.now(), 
            "text":datamessagehere,
            "from_id":message.from_user.id,
            "message_from_id":message.message_id,
            "type":"text",
            "mediaid":"none",
            "isread":True}

    ticket_collection.find_and_modify(
        query={"operator": message.from_user.id, "isopen":"onair"},
        update={"$set":{"isopen":"onpause"},'$addToSet': { 'extrafield': extradd }}
    )
    html_text,supportmenubase=build_support_menu(message.from_user.id)

    await message.answer_photo(caption=get_text('support_operator_paused_message_text',message.from_user.id),parse_mode='HTML',reply_markup=ReplyKeyboardRemove(), photo=photoparser('paused') )
    await message.answer_photo(photo=photoparser('operatormainmenu'), caption=html_text,parse_mode='HTML',reply_markup=supportmenubase ) 
    await SupportManage.menu.set()

##################################
##################################
###################################ВСЕ ЧТО НИЖЕ ДОЛЖНО БЫТЬ В КОНЦЕ ДОКУМЕНТА########################################################
@dp.message_handler(state=SupportManage.onair)
async def currenttalk(message: types.Message):
    thisoperator =  staff_collection.find_one({"user_id":message.from_user.id})
    html_text="\n".join(
        [
            '<b>👨‍💻 '+thisoperator["callmeas"]+':</b>',
            message.text
        ]
    ) 
    thisicket=ticket_collection.find_one({"operator":message.from_user.id, "isopen":"onair"})
    try:
        await bot.send_message(chat_id=thisicket['userid'],text=html_text,parse_mode='HTML')
    except:
        datamessagehere="\n".join(
            [
                '<b>‼️Error, perhaps bot was banned from client side‼️</b> <i>('+datetime.now().strftime("%d.%m.%Y / %H:%M")+')</i>',
            ]
        )
        extradd={
            "side":"error" ,
            "date": datetime.now(), 
            "text":datamessagehere,
            "from_id":message.from_user.id,
            "message_from_id":message.message_id,
            "type":"text",
            "mediaid":"none",
            "isread":True}

        ticket_collection.find_and_modify(
            query={"ticketid":thisicket["ticketid"]},
            update={'$addToSet': { 'extrafield': extradd }}
        )
        html_text2=get_text('user_clientendedconvers_text',message.from_user.id)

        endinline= InlineKeyboardMarkup(row_width=1, inline_keyboard=[
            [InlineKeyboardButton(
                text=get_text('user_end_dialogue_text',message.from_user.id),
                callback_data='operator_end_inline_ticket_error'
            )]
        ]) 
        await bot.send_photo(chat_id=thisicket['operator'],parse_mode='HTML', photo=photoparser('clientfinished'), reply_markup=ReplyKeyboardRemove())
        await bot.send_message(chat_id=thisicket['operator'], text=html_text2,parse_mode='HTML',reply_markup=endinline)

        #проверка на билет
        raise CancelHandler()       

    
    tomsas="\n".join(
            [
                '<b>👨‍💻 '+thisoperator["callmeas"]+':</b> <i>('+datetime.now().strftime("%d.%m.%Y / %H:%M")+')</i>',
                message.text
            ]
        )
    extradd={
        "side":"fromoperator" ,
        "date": datetime.now(), 
        "text":tomsas,
        "from_id":message.from_user.id,
        "message_from_id":message.message_id,
        "type":"text",
        "mediaid":"none",
        "isread":True}


    ticket_collection.find_and_modify(
        query={"ticketid":thisicket["ticketid"]},
        update={'$addToSet': { 'extrafield': extradd }}
    )
@dp.message_handler(state=ProjectManage.awaitingsup)
async def usercurrenttalk(message: types.Message, state: FSMContext):
    thisicket=ticket_collection.find_one({"userid":message.from_user.id, "$or":[{'isopen':'onair'},{'isopen':'onpause'},{'isopen':'created'}]})
    thisuser = user_collection.find_one({"user_id":message.from_user.id})
    if thisicket["isopen"]=="onair":
        html_text="\n".join(
            [
                '<b>🗣️ '+thisuser["callmeas"]+':</b>',
                message.text
            ]
        ) 
        await bot.send_message(chat_id=thisicket['operator'],text=html_text,parse_mode='HTML')
        tomsas="\n".join(
            [
                '<b>🗣️ '+thisuser["callmeas"]+':</b> <i>('+datetime.now().strftime("%d.%m.%Y / %H:%M")+')</i>',
                message.text
            ]
        )
        extradd={
            "side":"fromuser" ,
            "date": datetime.now(), 
            "text":tomsas,
            "from_id":message.from_user.id,
            "message_from_id":message.message_id,
            "type":"text",
            "mediaid":"none",
            "isread":True}

        ticket_collection.find_and_modify(
            query={"ticketid":thisicket["ticketid"]},
            update={'$addToSet': { 'extrafield': extradd }}
        )
    elif thisicket["isopen"]=="onpause" or thisicket["isopen"]=="created":
        tomsas="\n".join(
            [
                '<b>🗣️ '+thisuser["callmeas"]+':</b> <i>('+datetime.now().strftime("%d.%m.%Y / %H:%M")+')</i>',
                message.text
            ]
        )
        extradd={
            "side":"fromuser" ,
            "date": datetime.now(), 
            "text":tomsas,
            "from_id":message.from_user.id,
            "message_from_id":message.message_id,
            "type":"text",
            "mediaid":"none",
            "isread":False}

        ticket_collection.find_and_modify(
            query={"ticketid":thisicket["ticketid"]},
            update={'$addToSet': { 'extrafield': extradd }}
        )
  



###################################БЛОК ОТПРАВКИ ГОЛОСОВЫХ########################################################

@dp.message_handler( content_types=['voice'], state=SupportManage.onair)
async def currenttalk_voice(message: types.Message):
    thisoperator =  staff_collection.find_one({"user_id":message.from_user.id})
    tomsas="\n".join(
        [
            '<b>👨‍💻 '+thisoperator["callmeas"]+':</b> <i>('+datetime.now().strftime("%d.%m.%Y / %H:%M")+')</i>',
        ]
    )
    thisicket=ticket_collection.find_one({"operator":message.from_user.id, "isopen":"onair"})
    try:
        await bot.send_voice(chat_id=thisicket['userid'], voice=message.voice.file_id)
    except:
        datamessagehere="\n".join(
            [
                '<b>‼️Error, perhaps bot was banned from client side‼️</b> <i>('+datetime.now().strftime("%d.%m.%Y / %H:%M")+')</i>',
            ]
        )
        extradd={
            "side":"error" ,
            "date": datetime.now(), 
            "text":datamessagehere,
            "from_id":message.from_user.id,
            "message_from_id":message.message_id,
            "type":"text",
            "mediaid":"none",
            "isread":True}

        ticket_collection.find_and_modify(
            query={"ticketid":thisicket["ticketid"]},
            update={'$addToSet': { 'extrafield': extradd }}
        )
        

        html_text2=get_text('user_clientendedconvers_text',message.from_user.id)

        endinline= InlineKeyboardMarkup(row_width=1, inline_keyboard=[
            [InlineKeyboardButton(
                text=get_text('user_end_dialogue_text',message.from_user.id),
                callback_data='operator_end_inline_ticket_error'
            )]
        ]) 


        await bot.send_photo(chat_id=thisicket['operator'],parse_mode='HTML', photo=photoparser('clientfinished'), reply_markup=ReplyKeyboardRemove())
        await bot.send_message(chat_id=thisicket['operator'], text=html_text2,parse_mode='HTML',reply_markup=endinline)

        raise CancelHandler()       

    extradd={
        "side":"fromoperator" ,
        "date": datetime.now(), 
        "text":tomsas,
        "from_id":message.from_user.id,
        "message_from_id":message.message_id,
        "type":"voice",
        "mediaid":message.voice.file_id,
        "isread":True}

    ticket_collection.find_and_modify(
        query={"ticketid":thisicket["ticketid"]},
        update={'$addToSet': { 'extrafield': extradd }}
    )

@dp.message_handler(content_types=['voice'],state=ProjectManage.awaitingsup)
async def usercurrenttalk_voice(message: types.Message, state: FSMContext):


    thisicket=ticket_collection.find_one({"userid":message.from_user.id, "$or":[{'isopen':'onair'},{'isopen':'onpause'},{'isopen':'created'}]})
    thisuser = user_collection.find_one({"user_id":message.from_user.id})
    if thisicket["isopen"]=="onair":
    
        await bot.send_voice(chat_id=thisicket['operator'], voice=message.voice.file_id)
        tomsas="\n".join(
            [
                '<b>🗣️ '+thisuser["callmeas"]+':</b> <i>('+datetime.now().strftime("%d.%m.%Y / %H:%M")+')</i>',
            ]
        )
        extradd={
            "side":"fromuser" ,
            "date": datetime.now(), 
            "text":tomsas,
            "from_id":message.from_user.id,
            "message_from_id":message.message_id,
            "type":"voice",
            "mediaid":message.voice.file_id,
            "isread":True}

        ticket_collection.find_and_modify(
            query={"ticketid":thisicket["ticketid"]},
            update={'$addToSet': { 'extrafield': extradd }}
        )
    elif thisicket["isopen"]=="onpause" or thisicket["isopen"]=="created":
        tomsas="\n".join(
            [
                '<b>🗣️ '+thisuser["callmeas"]+':</b> <i>('+datetime.now().strftime("%d.%m.%Y / %H:%M")+')</i>',
            ]
        )
        extradd={
            "side":"fromuser" ,
            "date": datetime.now(), 
            "text":tomsas,
            "from_id":message.from_user.id,
            "message_from_id":message.message_id,
            "type":"voice",
            "mediaid":message.voice.file_id,
            "isread":False}

        ticket_collection.find_and_modify(
            query={"ticketid":thisicket["ticketid"]},
            update={'$addToSet': { 'extrafield': extradd }}
        )


###################################БЛОК ОТПРАВКИ фоточчек########################################################

@dp.message_handler( content_types=['photo'], state=SupportManage.onair)
async def currenttalk_photo(message: types.Message):

    thisoperator =  staff_collection.find_one({"user_id":message.from_user.id})
    if message.caption==None:
        message.caption=''
    tomsas="\n".join(
        [
            '<b>👨‍💻 '+thisoperator["callmeas"]+':</b> <i>('+datetime.now().strftime("%d.%m.%Y / %H:%M")+')</i>',
            message.caption
        ]
    )
    thisicket=ticket_collection.find_one({"operator":message.from_user.id, "isopen":"onair"})
    try:
        await bot.send_photo(chat_id=thisicket['userid'], photo=message.photo[0].file_id, caption=message.caption)
    except:
        datamessagehere="\n".join(
            [
                '<b>‼️Error, perhaps bot was banned from client side‼️</b> <i>('+datetime.now().strftime("%d.%m.%Y / %H:%M")+')</i>',
            ]
        )
        extradd={
            "side":"error" ,
            "date": datetime.now(), 
            "text":datamessagehere,
            "from_id":message.from_user.id,
            "message_from_id":message.message_id,
            "type":"text",
            "mediaid":"none",
            "isread":True}

        ticket_collection.find_and_modify(
            query={"ticketid":thisicket["ticketid"]},
            update={'$addToSet': { 'extrafield': extradd }}
        )
        html_text2=get_text('user_clientendedconvers_text',message.from_user.id)

        endinline= InlineKeyboardMarkup(row_width=1, inline_keyboard=[
            [InlineKeyboardButton(
                text=get_text('user_end_dialogue_text',message.from_user.id),
                callback_data='operator_end_inline_ticket_error'
            )]
        ]) 
        await bot.send_photo(chat_id=thisicket['operator'],parse_mode='HTML', photo=photoparser('clientfinished'), reply_markup=ReplyKeyboardRemove())
        await bot.send_message(chat_id=thisicket['operator'], text=html_text2,parse_mode='HTML',reply_markup=endinline)

        #проверка на билет
        raise CancelHandler()       

    extradd={
        "side":"fromoperator" ,
        "date": datetime.now(), 
        "text":tomsas,
        "from_id":message.from_user.id,
        "message_from_id":message.message_id,
        "type":"photo",
        "mediaid":message.photo[0].file_id,
        "isread":True}

    ticket_collection.find_and_modify(
        query={"ticketid":thisicket["ticketid"]},
        update={'$addToSet': { 'extrafield': extradd }}
    )

@dp.message_handler(content_types=['photo'],state=ProjectManage.awaitingsup)
async def usercurrenttalk_photo(message: types.Message, state: FSMContext):
    if message.caption==None:
        message.caption=''

    thisicket=ticket_collection.find_one({"userid":message.from_user.id, "$or":[{'isopen':'onair'},{'isopen':'onpause'},{'isopen':'created'}]})
    thisuser = user_collection.find_one({"user_id":message.from_user.id})
    if thisicket["isopen"]=="onair":
    
        await bot.send_photo(chat_id=thisicket['operator'], photo=message.photo[0].file_id, caption=message.caption)
        tomsas="\n".join(
            [
                '<b>🗣️ '+thisuser["callmeas"]+':</b> <i>('+datetime.now().strftime("%d.%m.%Y / %H:%M")+')</i>',
                message.caption
            ]
        )
        extradd={
            "side":"fromoperator" ,
            "date": datetime.now(), 
            "text":tomsas,
            "from_id":message.from_user.id,
            "message_from_id":message.message_id,
            "type":"photo",
            "mediaid":message.photo[0].file_id,
            "isread":True}

        ticket_collection.find_and_modify(
            query={"ticketid":thisicket["ticketid"]},
            update={'$addToSet': { 'extrafield': extradd }}
        )
    elif thisicket["isopen"]=="onpause" or thisicket["isopen"]=="created":
        tomsas="\n".join(
            [
                '<b>🗣️ '+thisuser["callmeas"]+':</b> <i>('+datetime.now().strftime("%d.%m.%Y / %H:%M")+')</i>',
                message.caption
            ]
        )
        extradd={
            "side":"fromoperator" ,
            "date": datetime.now(), 
            "text":tomsas,
            "from_id":message.from_user.id,
            "message_from_id":message.message_id,
            "type":"photo",
            "mediaid":message.photo[0].file_id,
            "isread":False}

        ticket_collection.find_and_modify(
            query={"ticketid":thisicket["ticketid"]},
            update={'$addToSet': { 'extrafield': extradd }}
        )



###################################БЛОК ОТПРАВКИ Видюшшеччекк########################################################

@dp.message_handler( content_types=['video'], state=SupportManage.onair)
async def currenttalk_video(message: types.Message):

    thisoperator =  staff_collection.find_one({"user_id":message.from_user.id})
    if message.caption==None:
        message.caption=''
    tomsas="\n".join(
        [
            '<b>👨‍💻 '+thisoperator["callmeas"]+':</b> <i>('+datetime.now().strftime("%d.%m.%Y / %H:%M")+')</i>',
            message.caption
        ]
    )
    thisicket=ticket_collection.find_one({"operator":message.from_user.id, "isopen":"onair"})
    try:
        await bot.send_video(chat_id=thisicket['userid'], video=message.video.file_id, caption=message.caption)
    except:
        datamessagehere="\n".join(
            [
                '<b>‼️Error, perhaps bot was banned from client side‼️</b> <i>('+datetime.now().strftime("%d.%m.%Y / %H:%M")+')</i>',
            ]
        )
        extradd={
            "side":"error" ,
            "date": datetime.now(), 
            "text":datamessagehere,
            "from_id":message.from_user.id,
            "message_from_id":message.message_id,
            "type":"text",
            "mediaid":"none",
            "isread":True}

        ticket_collection.find_and_modify(
            query={"ticketid":thisicket["ticketid"]},
            update={'$addToSet': { 'extrafield': extradd }}
        )
        html_text2=get_text('user_clientendedconvers_text',message.from_user.id)

        endinline= InlineKeyboardMarkup(row_width=1, inline_keyboard=[
            [InlineKeyboardButton(
                text=get_text('user_end_dialogue_text',message.from_user.id),
                callback_data='operator_end_inline_ticket_error'
            )]
        ]) 
        await bot.send_photo(chat_id=thisicket['operator'],parse_mode='HTML', photo=photoparser('clientfinished'), reply_markup=ReplyKeyboardRemove())
        await bot.send_message(chat_id=thisicket['operator'], text=html_text2,parse_mode='HTML',reply_markup=endinline)

        #проверка на билет
        raise CancelHandler()       

    extradd={
        "side":"fromoperator" ,
        "date": datetime.now(), 
        "text":tomsas,
        "from_id":message.from_user.id,
        "message_from_id":message.message_id,
        "type":"video",
        "mediaid":message.video.file_id,
        "isread":True}

    ticket_collection.find_and_modify(
        query={"ticketid":thisicket["ticketid"]},
        update={'$addToSet': { 'extrafield': extradd }}
    )

@dp.message_handler(content_types=['video'],state=ProjectManage.awaitingsup)
async def usercurrenttalk_video(message: types.Message, state: FSMContext):
    if message.caption==None:
        message.caption=''

    thisicket=ticket_collection.find_one({"userid":message.from_user.id, "$or":[{'isopen':'onair'},{'isopen':'onpause'},{'isopen':'created'}]})
    thisuser = user_collection.find_one({"user_id":message.from_user.id})
    if thisicket["isopen"]=="onair":
    
        await bot.send_video(chat_id=thisicket['operator'], video=message.video.file_id, caption=message.caption)
        tomsas="\n".join(
            [
                '<b>🗣️ '+thisuser["callmeas"]+':</b> <i>('+datetime.now().strftime("%d.%m.%Y / %H:%M")+')</i>',
                message.caption
            ]
        )
        extradd={
            "side":"fromuser" ,
            "date": datetime.now(), 
            "text":tomsas,
            "from_id":message.from_user.id,
            "message_from_id":message.message_id,
            "type":"video",
            "mediaid":message.video.file_id,
            "isread":True}

        ticket_collection.find_and_modify(
            query={"ticketid":thisicket["ticketid"]},
            update={'$addToSet': { 'extrafield': extradd }}
        )
    elif thisicket["isopen"]=="onpause" or thisicket["isopen"]=="created":
        tomsas="\n".join(
            [
                '<b>🗣️ '+thisuser["callmeas"]+':</b> <i>('+datetime.now().strftime("%d.%m.%Y / %H:%M")+')</i>',
                message.caption
            ]
        )
        extradd={
            "side":"fromuser" ,
            "date": datetime.now(), 
            "text":tomsas,
            "from_id":message.from_user.id,
            "message_from_id":message.message_id,
            "type":"video",
            "mediaid":message.video.file_id,
            "isread":False}

        ticket_collection.find_and_modify(
            query={"ticketid":thisicket["ticketid"]},
            update={'$addToSet': { 'extrafield': extradd }}
        )


###################################БЛОК ОТПРАВКИ Видевоквужочков########################################################

@dp.message_handler( content_types=['video_note'], state=SupportManage.onair)
async def currenttalk_video_note(message: types.Message):
    thisoperator =  staff_collection.find_one({"user_id":message.from_user.id})
    tomsas="\n".join(
        [
            '<b>👨‍💻 '+thisoperator["callmeas"]+':</b> <i>('+datetime.now().strftime("%d.%m.%Y / %H:%M")+')</i>',
        ]
    )
    thisicket=ticket_collection.find_one({"operator":message.from_user.id, "isopen":"onair"})
    try:
        await bot.send_video_note(chat_id=thisicket['userid'], video_note=message.video_note.file_id)
    except:
        datamessagehere="\n".join(
            [
                '<b>‼️Error, perhaps bot was banned from client side‼️</b> <i>('+datetime.now().strftime("%d.%m.%Y / %H:%M")+')</i>',
            ]
        )
        extradd={
            "side":"error" ,
            "date": datetime.now(), 
            "text":datamessagehere,
            "from_id":message.from_user.id,
            "message_from_id":message.message_id,
            "type":"text",
            "mediaid":"none",
            "isread":True}

        ticket_collection.find_and_modify(
            query={"ticketid":thisicket["ticketid"]},
            update={'$addToSet': { 'extrafield': extradd }}
        )
        html_text2=get_text('user_clientendedconvers_text',message.from_user.id)

        endinline= InlineKeyboardMarkup(row_width=1, inline_keyboard=[
            [InlineKeyboardButton(
                text=get_text('user_end_dialogue_text',message.from_user.id),
                callback_data='operator_end_inline_ticket_error'
            )]
        ]) 
        await bot.send_photo(chat_id=thisicket['operator'],parse_mode='HTML', photo=photoparser('clientfinished'), reply_markup=ReplyKeyboardRemove())
        await bot.send_message(chat_id=thisicket['operator'], text=html_text2,parse_mode='HTML',reply_markup=endinline)

        #проверка на билет
        raise CancelHandler()       

    extradd={
        "side":"fromoperator" ,
        "date": datetime.now(), 
        "text":tomsas,
        "from_id":message.from_user.id,
        "message_from_id":message.message_id,
        "type":"video_note",
        "mediaid":message.video_note.file_id,
        "isread":True}

    ticket_collection.find_and_modify(
        query={"ticketid":thisicket["ticketid"]},
        update={'$addToSet': { 'extrafield': extradd }}
    )

@dp.message_handler(content_types=['video_note'],state=ProjectManage.awaitingsup)
async def usercurrenttalk_video_note(message: types.Message, state: FSMContext):


    thisicket=ticket_collection.find_one({"userid":message.from_user.id, "$or":[{'isopen':'onair'},{'isopen':'onpause'},{'isopen':'created'}]})
    thisuser = user_collection.find_one({"user_id":message.from_user.id})
    if thisicket["isopen"]=="onair":
    
        await bot.send_video_note(chat_id=thisicket['operator'], voice=message.video_note.file_id)
        tomsas="\n".join(
            [
                '<b>🗣️ '+thisuser["callmeas"]+':</b> <i>('+datetime.now().strftime("%d.%m.%Y / %H:%M")+')</i>',
            ]
        )
        extradd={
            "side":"fromuser" ,
            "date": datetime.now(), 
            "text":tomsas,
            "from_id":message.from_user.id,
            "message_from_id":message.message_id,
            "type":"video_note",
            "mediaid":message.video_note.file_id,
            "isread":True}

        ticket_collection.find_and_modify(
            query={"ticketid":thisicket["ticketid"]},
            update={'$addToSet': { 'extrafield': extradd }}
        )
    elif thisicket["isopen"]=="onpause" or thisicket["isopen"]=="created":
        tomsas="\n".join(
            [
                '<b>🗣️ '+thisuser["callmeas"]+':</b> <i>('+datetime.now().strftime("%d.%m.%Y / %H:%M")+')</i>',
            ]
        )
        extradd={
            "side":"fromuser" ,
            "date": datetime.now(), 
            "text":tomsas,
            "from_id":message.from_user.id,
            "message_from_id":message.message_id,
            "type":"video_note",
            "mediaid":message.video_note.file_id,
            "isread":False}

        ticket_collection.find_and_modify(
            query={"ticketid":thisicket["ticketid"]},
            update={'$addToSet': { 'extrafield': extradd }}
        )


###################################БЛОК ОТПРАВКИ Файликов########################################################

@dp.message_handler( content_types=['document'], state=SupportManage.onair)
async def currenttalk_doc(message: types.Message):

    thisoperator =  staff_collection.find_one({"user_id":message.from_user.id})
    if message.caption==None:
        message.caption=''
    tomsas="\n".join(
        [
            '<b>👨‍💻 '+thisoperator["callmeas"]+':</b> <i>('+datetime.now().strftime("%d.%m.%Y / %H:%M")+')</i>',
            message.caption
        ]
    )
    thisicket=ticket_collection.find_one({"operator":message.from_user.id, "isopen":"onair"})
    try:
        await bot.send_document(chat_id=thisicket['userid'], document=message.document.file_id, caption=message.caption)
    except:
        datamessagehere="\n".join(
            [
                '<b>‼️Error, perhaps bot was banned from client side‼️</b> <i>('+datetime.now().strftime("%d.%m.%Y / %H:%M")+')</i>',
            ]
        )
        extradd={
            "side":"error" ,
            "date": datetime.now(), 
            "text":datamessagehere,
            "from_id":message.from_user.id,
            "message_from_id":message.message_id,
            "type":"text",
            "mediaid":"none",
            "isread":True}

        ticket_collection.find_and_modify(
            query={"ticketid":thisicket["ticketid"]},
            update={'$addToSet': { 'extrafield': extradd }}
        )
        html_text2=get_text('user_clientendedconvers_text',message.from_user.id)

        endinline= InlineKeyboardMarkup(row_width=1, inline_keyboard=[
            [InlineKeyboardButton(
                text=get_text('user_end_dialogue_text',message.from_user.id),
                callback_data='operator_end_inline_ticket_error'
            )]
        ]) 
        await bot.send_photo(chat_id=thisicket['operator'],parse_mode='HTML', photo=photoparser('clientfinished'), reply_markup=ReplyKeyboardRemove())
        await bot.send_message(chat_id=thisicket['operator'], text=html_text2,parse_mode='HTML',reply_markup=endinline)

        #проверка на билет
        raise CancelHandler()       

    extradd={
        "side":"fromoperator" ,
        "date": datetime.now(), 
        "text":tomsas,
        "from_id":message.from_user.id,
        "message_from_id":message.message_id,
        "type":"document",
        "mediaid":message.document.file_id,
        "isread":True}

    ticket_collection.find_and_modify(
        query={"ticketid":thisicket["ticketid"]},
        update={'$addToSet': { 'extrafield': extradd }}
    )

@dp.message_handler(content_types=['document'],state=ProjectManage.awaitingsup)
async def usercurrenttalk_doc(message: types.Message, state: FSMContext):
    if message.caption==None:
        message.caption=''

    thisicket=ticket_collection.find_one({"userid":message.from_user.id, "$or":[{'isopen':'onair'},{'isopen':'onpause'},{'isopen':'created'}]})
    thisuser = user_collection.find_one({"user_id":message.from_user.id})
    if thisicket["isopen"]=="onair":
    
        await bot.send_document(chat_id=thisicket['operator'], document=message.document.file_id, caption=message.caption)
        tomsas="\n".join(
            [
                '<b>🗣️ '+thisuser["callmeas"]+':</b> <i>('+datetime.now().strftime("%d.%m.%Y / %H:%M")+')</i>',
                message.caption
            ]
        )
        extradd={
            "side":"fromuser" ,
            "date": datetime.now(), 
            "text":tomsas,
            "from_id":message.from_user.id,
            "message_from_id":message.message_id,
            "type":"document",
            "mediaid":message.document.file_id,
            "isread":True}

        ticket_collection.find_and_modify(
            query={"ticketid":thisicket["ticketid"]},
            update={'$addToSet': { 'extrafield': extradd }}
        )
    elif thisicket["isopen"]=="onpause" or thisicket["isopen"]=="created":
        tomsas="\n".join(
            [
                '<b>🗣️ '+thisuser["callmeas"]+':</b> <i>('+datetime.now().strftime("%d.%m.%Y / %H:%M")+')</i>',
                message.caption
            ]
        )
        extradd={
            "side":"fromuser" ,
            "date": datetime.now(), 
            "text":tomsas,
            "from_id":message.from_user.id,
            "message_from_id":message.message_id,
            "type":"document",
            "mediaid":message.document.file_id,
            "isread":False}

        ticket_collection.find_and_modify(
            query={"ticketid":thisicket["ticketid"]},
            update={'$addToSet': { 'extrafield': extradd }}
        )




#-------------------------------------инлайн ответы---------------------------
@dp.message_handler( text='/creatematerial', state=SupportManage.menu)
async def generatematerial(message: types.Message):
    xs=secrets.token_hex(4)+'MATERIAL'+"{:03d}".format(secrets.randbelow(999))
    await message.answer(xs)


@dp.inline_handler(state='*')
async def show_inline_materials(query: types.InlineQuery):
   
    if len(query.query)<1:
        raise CancelHandler() 
    elif query.query.startswith('#'):
        string_modified=query.query.replace('#', '')
        materials_arr=inline_materials_collection.find({'category':{'$regex':string_modified}})
        results_arr=[]

        for mat_obj in materials_arr:

            toadd=types.InlineQueryResultArticle(
                id=mat_obj['material_id'],
                title=mat_obj['title'],
                description=mat_obj['description'],
                input_message_content=types.InputMessageContent(message_text=mat_obj['text'], parse_mode='HTML'),
                thumb_url=mat_obj['thumb']
            )

            results_arr.append(toadd)
            
        await query.answer(
            results=results_arr,
            cache_time=0,
            is_personal=True
        )
    else:
        materials_arr=inline_materials_collection.find(
            { "$text": { "$search": query.query}},
            { "score": { "$meta": "textScore" } }
            ).sort([('score', {'$meta': 'textScore'})])
        results_arr=[]

        for mat_obj in materials_arr:

            toadd=types.InlineQueryResultArticle(
                id=mat_obj['material_id'],
                title=mat_obj['title'],
                description=mat_obj['description'],
                input_message_content=types.InputMessageContent(message_text=mat_obj['text'], parse_mode='HTML'),
                thumb_url=mat_obj['thumb']
            )

            results_arr.append(toadd)
            
        await query.answer(
            results=results_arr,
            cache_time=0,
            is_personal=True
        )


#-------------------------------------инлайн ответы конец---------------------------