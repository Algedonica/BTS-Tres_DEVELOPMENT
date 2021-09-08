from datetime import datetime
from aiogram import types, md
from loader import dp, bot
from data.config import user_collection, ticket_collection, staff_collection, settings_collection, states_collection, channelid
from states import ProjectManage,SupportManage
from aiogram.types import CallbackQuery,ReplyKeyboardRemove, InputFile
from aiogram.utils.callback_data import CallbackData
from utils.misc.logging import logging
from utils.misc import rate_limit
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher import FSMContext
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.types import InputMediaPhoto
from utils.misc import build_user_menu, build_operatorcontrol, get_text,get_partner_channel, build_support_menu,isadmin,support_role_check, xstr, photoparser,  getCryptoData,  send_to_channel, issupport

from keyboards.inline import meeting_pick_lang,usersupportchoiceinline, ticket_callback, add_operator_callback, show_support_pages, edit_something_admin, show_cities_pages, knowledge_list_call

@dp.message_handler(text="/reset", state=[
    ProjectManage.menu, 
    ProjectManage.awaitingsup,
    ProjectManage.initializingsup, 
    ProjectManage.preparingquest, 
    ProjectManage.onair
    ])
async def resetbot_byuser(message: types.Message):
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
                '<b>№'+str(counttickets)+' '+thisicket['citytag']+' '+'#'+thisicket['project']+'</b>',
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



@dp.message_handler(text="/reset", state=[
    SupportManage.menu,
    SupportManage.awaitingsup, 
    SupportManage.initializingsup, 
    SupportManage.onair, 
    SupportManage.changeoperatorname, 
    SupportManage.addcityinput,  
    SupportManage.initcsv,  
    SupportManage.inittimecsv,  
    SupportManage.accept_time,  
    SupportManage.knowledge_set_title,  
    SupportManage.knowledge_set_descr,
    ])
async def resetbot_byoperator(message: types.Message, state: FSMContext):
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
                '<b>№'+str(counttickets)+' '+thisicket['citytag']+' '+'#'+thisicket['project']+'</b>',
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
    



@dp.message_handler(text="/vm", state=[SupportManage.menu])
async def reverserole_for_staff(message: types.Message, state: FSMContext):
    if issupport(message.from_user.id)==True:
        await state.reset_state()
        await ProjectManage.menu.set()
        staff_collection.find_and_modify( 
            query={"user_id":message.from_user.id}, 
            update={ "$set": { 'isreverse': True} }
            )
        await message.answer(get_text('support_vm_func_text',message.from_user.id), reply_markup=ReplyKeyboardRemove()) 

@dp.message_handler(text="/vm", state=[ProjectManage.menu])
async def reverserole_for_staff(message: types.Message, state: FSMContext):
    if issupport(message.from_user.id)==True:
        await state.reset_state()
        await SupportManage.menu.set() 
        staff_collection.find_and_modify( 
            query={"user_id":message.from_user.id}, 
            update={ "$set": { 'isreverse': False} }
            )
        await message.answer(get_text('support_vm_func_text',message.from_user.id), reply_markup=ReplyKeyboardRemove())    




@dp.message_handler(text="/lang", state=[SupportManage.menu, ProjectManage.menu])
async def change_lang_for_staff(message: types.Message, state: FSMContext):
    photoo = settings_collection.find_one({"settings":"mainsettings"})
    langs=photoo['langs']
    lang_buttons = InlineKeyboardMarkup()
    for x in langs:
        lang_buttons.add(InlineKeyboardButton(text=x['lang_name'], callback_data=meeting_pick_lang.new("chnglng",param1=message.from_user.id,param2=x['lang_code'])))

    html_text="\n".join(
        [
            'Choose your language:'
        ]
    )
    
    if issupport(message.from_user.id)==True:
        await state.reset_state()
        await SupportManage.change_lang.set()
    else:
        await state.reset_state()
        await ProjectManage.change_lang.set()

    await bot.send_message(chat_id= message.from_user.id, text=html_text,parse_mode='HTML', reply_markup=lang_buttons)


@dp.callback_query_handler(meeting_pick_lang.filter(command='chnglng'), state=[SupportManage.change_lang, ProjectManage.change_lang])
async def picked_lang_meeting(call: types.CallbackQuery, callback_data:dict):
    param1 = callback_data.get("param1")
    user_id=int(param1)
    lang_code=callback_data.get("param2")

    if issupport(user_id)==True:
        staff_collection.find_and_modify(
            query={"user_id":user_id},
            update={"$set":{"lang_code":lang_code}}
        )

    user_collection.find_and_modify(
        query={"user_id":user_id},
        update={"$set":{"lang_code":lang_code}}
    )

    html_text=get_text('language_changed_text',call.from_user.id)
    await call.message.delete()
    await ProjectManage.menu.set()
    await bot.send_message(chat_id= call.from_user.id, text=html_text,parse_mode='HTML', reply_markup=None)