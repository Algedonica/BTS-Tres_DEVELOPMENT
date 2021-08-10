from aiogram_broadcaster import MessageBroadcaster
from loader import dp,bot
from handlers.users.echo import scheduler
from states import ProjectManage,SupportManage, SetupBTSstates
from datetime import datetime
from data.config import broadcast_collection, partner_collection,links_collection,user_collection, staff_collection, settings_collection, pmessages_collection, photos_collection
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, message_id
from aiogram import types
from aiogram.dispatcher import FSMContext
import secrets
import math
from utils.misc import issupport,build_support_menu,system_text_parser,get_partner_obj,isadmin,support_role_check, xstr, photoparser, parse_message_by_tag_name, getCryptoData, parse_video_by_tag_name, send_to_channel, get_user_city,   get_user_came_from, check_error_ticket
from keyboards.inline import show_broadcast_pages



async def broadcaster_go(thisuser, message_id, sendto, broadcast_id):
    finalmsg=await bot.forward_message(chat_id=thisuser, from_chat_id=thisuser, message_id=message_id, disable_notification=True)
    await bot.delete_message(chat_id=thisuser,message_id=finalmsg.message_id)
    users=user_collection.find({'citytag':{"$in":sendto}})
    finalarr=[]
    for x in users:
        if issupport(x['user_id'])!=True:
            finalarr.append(x['user_id'])
    finalarr.append(thisuser)
    await MessageBroadcaster(finalarr, finalmsg).run()
    await bot.send_message(chat_id=thisuser,text='Рассылка успешно завершена')
    broadcast_collection.find_one_and_update(
        { "broadcast_id":broadcast_id},
        { "$set":{"status":"finished"}}
    )
   
async def broadcaster_startup():
    broadcasts=broadcast_collection.find({"status":"active"})
    for broadcast_obj in broadcasts:
        broadcast_date=broadcast_obj['run_date']
        thistext=broadcast_date.split('_')
        datearr=thistext[0].split('-')
        timearr=thistext[1].split(':')
        scheduler.add_job(broadcaster_go, 'date', id=broadcast_obj['broadcast_id'], run_date=datetime(int(datearr[2]), int(datearr[1]), int(datearr[0]), int(timearr[0]), int(timearr[1])), kwargs={'thisuser':broadcast_obj['user_id'], 'message_id':broadcast_obj['message_id'], 'sendto':broadcast_obj['partners'], 'broadcast_id':broadcast_obj['broadcast_id']})
    

@dp.callback_query_handler(text='to_broadcast_admin',state=[SupportManage.menu])
async def broadcasta_init(call:types.CallbackQuery):

    supportmenubase = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
        [InlineKeyboardButton(
            text='+ Добавить рассылку',
            callback_data='add_new_broadcast'
        )],
        [InlineKeyboardButton(
            text='Посмотреть мои рассылки',
            callback_data='my_broadcasts'
        )]
    ]) 

    supportmenubase.add(InlineKeyboardButton(text="↩️ в меню",callback_data='supportbacktomenu'))
    await call.message.edit_caption(caption='Вы находитесь в меню управления рассылками', reply_markup=supportmenubase)




@dp.callback_query_handler(text='add_new_broadcast',state=[SupportManage.menu])
async def broadcasta_init(call:types.CallbackQuery):
    await call.message.edit_caption(caption='Пришлите пост который хотите отослать', reply_markup=None)
    await SupportManage.broadcast_init.set()




@dp.message_handler(content_types=['text', 'photo','document','audio','video', 'video_note'],state=[SupportManage.broadcast_init])
async def broadcasta_get_msg(message:types.Message, state:FSMContext):
    msgtotext=message.message_id
    await MessageBroadcaster(message.from_user.id, message).run()
    supportmenubase = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
        [InlineKeyboardButton(
            text='Далее',
            callback_data=show_broadcast_pages.new("show_avaliable_partners",param1=1, param2='none')
        )]
    ]) 
    await message.answer('Вы добавили пост. Не беспокойтесь, если заметили ошибку. После завершения вы сможете его отредактировать. Нажмите на "Далее".', reply_markup=supportmenubase)
    await SupportManage.broadcast_get.set()
    await state.update_data(thatmessage=msgtotext)
    await state.update_data(partnertosend=[])


@dp.callback_query_handler(show_broadcast_pages.filter(command='show_avaliable_partners'), state=SupportManage.broadcast_get)
async def broadcasta_go_showpartners(call:types.CallbackQuery,state:FSMContext, callback_data:dict):
    await call.answer(cache_time=1)
    page = callback_data.get("param1")
    page = int(page)
    prevpage = page - 1
    nextpage = page + 1
    inlinekeys = InlineKeyboardMarkup(row_width=2)


    data = await state.get_data()
    partnertosend = data.get("partnertosend")

    thisoperator = staff_collection.find_one({"user_id":call.from_user.id})
    operator_cities=thisoperator['city_code'][1:]
    cities_on_page = operator_cities[((page-1)*5):(5*page)]


    for y in cities_on_page:
        galka=""
       
        if y in partnertosend:
            galka="✔️ "
           
        inlinekeys.add(InlineKeyboardButton(text=galka+y, callback_data=show_broadcast_pages.new("aor",param1=page, param2=y)))


    if prevpage < 1:
        prevtoadd=InlineKeyboardButton(
            text='◀️',
            callback_data=show_broadcast_pages.new("show_avaliable_partners",param1=1, param2='none')
        )
    else:
        prevtoadd=InlineKeyboardButton(
            text='◀️',
            callback_data=show_broadcast_pages.new("show_avaliable_partners",param1=prevpage, param2='none')
        )
        
    if  math.ceil(len(operator_cities)/5)==page:
        nexttoadd=InlineKeyboardButton(
            text='▶️',
            callback_data=show_broadcast_pages.new("show_avaliable_partners",param1=page, param2='none')
        )      
    else:
        nexttoadd=InlineKeyboardButton(
            text='▶️',
            callback_data=show_broadcast_pages.new("show_avaliable_partners",param1=nextpage, param2='none')
        )  
    inlinekeys.add(prevtoadd,nexttoadd)
    inlinekeys.add(InlineKeyboardButton(text='Далее',callback_data='broadcast_to_time'))
    await call.message.delete()
    await call.message.answer_photo(caption='Выберите группу пользователей. Вы на странице '+'<b>'+str(page)+'</b>',parse_mode='HTML',reply_markup=inlinekeys, photo=photoparser('operatormainmenu') )


@dp.callback_query_handler(show_broadcast_pages.filter(command='aor'), state=SupportManage.broadcast_get)
async def broadcasta_go_showpartners_deleteoradd(call:types.CallbackQuery,state:FSMContext, callback_data:dict):
    data = await state.get_data()
    partnertosend = data.get("partnertosend")

    if callback_data.get('param2') not in partnertosend:
        partnertosend.append(callback_data.get('param2'))
    else:
        partnertosend.remove(callback_data.get('param2'))
    await call.answer(cache_time=1)
    page = callback_data.get("param1")
    page = int(page)
    prevpage = page - 1
    nextpage = page + 1
    inlinekeys = InlineKeyboardMarkup(row_width=2)


    

    thisoperator = staff_collection.find_one({"user_id":call.from_user.id})
    operator_cities=thisoperator['city_code'][1:]
 
    cities_on_page = operator_cities[((page-1)*5):(5*page)]


    for y in cities_on_page:
        galka=""
      
        if y in partnertosend:
            galka="✔️ "
           
        inlinekeys.add(InlineKeyboardButton(text=galka+y, callback_data=show_broadcast_pages.new("aor",param1=page, param2=y)))


    if prevpage < 1:
        prevtoadd=InlineKeyboardButton(
            text='◀️',
            callback_data=show_broadcast_pages.new("show_avaliable_partners",param1=1, param2='none')
        )
    else:
        prevtoadd=InlineKeyboardButton(
            text='◀️',
            callback_data=show_broadcast_pages.new("show_avaliable_partners",param1=prevpage, param2='none')
        )
        
    if  math.ceil(len(operator_cities)/5)==page:
        nexttoadd=InlineKeyboardButton(
            text='▶️',
            callback_data=show_broadcast_pages.new("show_avaliable_partners",param1=page, param2='none')
        )      
    else:
        nexttoadd=InlineKeyboardButton(
            text='▶️',
            callback_data=show_broadcast_pages.new("show_avaliable_partners",param1=nextpage, param2='none')
        )  
    inlinekeys.add(prevtoadd,nexttoadd)
    inlinekeys.add(InlineKeyboardButton(text='Далее',callback_data='broadcast_to_time'))
    await call.message.delete()
    await call.message.answer_photo(caption='Вы на странице '+'<b>'+str(page)+'</b>',parse_mode='HTML',reply_markup=inlinekeys, photo=photoparser('operatormainmenu') )
    await state.update_data(partnertosend=partnertosend)








@dp.callback_query_handler(text='broadcast_to_time', state=SupportManage.broadcast_get)
async def broadcasta_go_msgyes(call:types.CallbackQuery,state:FSMContext):
    await call.message.edit_caption(caption='Теперь введите дату и время в формате "30-12-2000 в 16:45"', reply_markup=None)
    await SupportManage.broadcast_time.set()



@dp.message_handler(state=[SupportManage.broadcast_time])
async def broadcasta_time(message:types.Message,state:FSMContext):
    thistext=message.text
    thistext=thistext.split(' в ')

    datearr=thistext[0].split('-')
    timearr=thistext[1].split(':')

    data = await state.get_data()
    thatmsg = data.get("thatmessage")
    partnertosend=data.get("partnertosend")
    broadcast_id=str(message.from_user.id)+"{:03d}".format(secrets.randbelow(999))+"{:03d}".format(secrets.randbelow(999))+secrets.token_hex(4)

    scheduler.add_job(broadcaster_go, 'date', id=broadcast_id, run_date=datetime(int(datearr[2]), int(datearr[1]), int(datearr[0]), int(timearr[0]), int(timearr[1])), kwargs={'thisuser':message.from_user.id, 'message_id':thatmsg, 'sendto':partnertosend, 'broadcast_id':broadcast_id})
    
    broadcast_collection.insert_one(
        {"user_id": message.from_user.id,
        "broadcast_id": broadcast_id,
        "when_added": datetime.now(),
        "run_date":thistext[0]+'_'+thistext[1],
        "message_id":thatmsg,
        "partners":partnertosend,
        "status": "active"
        })
    html_text="\n".join(
        [
            '<b>Вы создали пост. Нажмите на кнопку ниже.</b>', 
        ]
    )
    broadcastcontrol = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
        [InlineKeyboardButton(
            text='Готово',
            callback_data=show_broadcast_pages.new("sb_ob",param1=broadcast_id, param2='none')
        )],
    ])

    await SupportManage.menu.set()
    await message.answer_photo(caption=html_text,parse_mode='HTML',reply_markup=broadcastcontrol, photo=photoparser('operatormainmenu') )




# -----------------------------------------------Далее идет менюшка бродкастов для админа--------------------------------------------------------


@dp.callback_query_handler(text='my_broadcasts',state=[SupportManage.menu])
async def show_my_broadcasts(call:types.CallbackQuery):

    supportmenubase = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
        [InlineKeyboardButton(
            text='Активные расслыки',
            callback_data=show_broadcast_pages.new("show_list_broadcasts",param1=1, param2='active')
        )],
        [InlineKeyboardButton(
            text='Завершенные/остановленные рассылки',
            callback_data=show_broadcast_pages.new("show_list_broadcasts",param1=1, param2='finished')
        )]
    ]) 

    supportmenubase.add(InlineKeyboardButton(text="↩️ назад",callback_data='to_broadcast_admin'))
    await call.message.edit_caption(caption='Выберите категорию рассылок', reply_markup=supportmenubase)


@dp.callback_query_handler(show_broadcast_pages.filter(command='show_list_broadcasts'),state=[SupportManage.menu])
async def show_my_active_broadcasts(call:types.CallbackQuery, callback_data:dict):  
    broadcast_type = callback_data.get("param2")


    page = callback_data.get("param1")
    page = int(page)
    prevpage = page - 1
    nextpage = page + 1
    inlinekeys = InlineKeyboardMarkup(row_width=2)

    broadcasts_arr=broadcast_collection.find({"user_id": call.from_user.id,"status": broadcast_type}).skip((page-1)*5).limit(5)

    for i in broadcasts_arr:
        inlinekeys.add(InlineKeyboardButton(text=i['run_date'], callback_data=show_broadcast_pages.new("sb_ob",param1=i['broadcast_id'], param2='none')))
    

    if prevpage < 1:
        prevtoadd=InlineKeyboardButton(
            text='◀️',
            callback_data=show_broadcast_pages.new("show_active_broadcasts",param1=1, param2=broadcast_type)
        )
    else:
        prevtoadd=InlineKeyboardButton(
            text='◀️',
            callback_data=show_broadcast_pages.new("show_active_broadcasts",param1=prevpage, param2=broadcast_type)
        )

    if math.ceil(broadcasts_arr.count()/5)==page:
        nexttoadd=InlineKeyboardButton(
            text='▶️',
            callback_data=show_broadcast_pages.new("show_active_broadcasts",param1=page, param2=broadcast_type)
        )      
    else:
        nexttoadd=InlineKeyboardButton(
            text='▶️',
            callback_data=show_broadcast_pages.new("show_active_broadcasts",param1=nextpage, param2=broadcast_type)
        )  

    inlinekeys.add(prevtoadd,nexttoadd)
    inlinekeys.add(InlineKeyboardButton(text='↩️ назад',callback_data='my_broadcasts'))
    await call.message.edit_caption(caption='Вы находитесь в разделе управления запланнированными активными рассылками', reply_markup=inlinekeys)

# Редактирование поста---------------------------------------------------

@dp.callback_query_handler(show_broadcast_pages.filter(command='sb_ob'),state=[SupportManage.menu])
async def broadcast_object_control(call:types.CallbackQuery, callback_data:dict):
    await call.message.delete()  
    bc_id = callback_data.get("param1")
    broadcast_obj=broadcast_collection.find_one({"broadcast_id":bc_id})

    await bot.forward_message(chat_id=call.from_user.id, from_chat_id=broadcast_obj['user_id'], message_id=broadcast_obj['message_id'], disable_notification=True)

    broadcastcontrol = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
        [InlineKeyboardButton(
            text='Отредактировать пост',
            callback_data=show_broadcast_pages.new("ch_br_p",param1=broadcast_obj['broadcast_id'], param2='none')
        )],
        [InlineKeyboardButton(
            text='Сменить дату рассылки',
            callback_data=show_broadcast_pages.new("ch_br_dt",param1=broadcast_obj['broadcast_id'], param2='none')
        )],
    ])

    if broadcast_obj['status']=='active':
        broadcastcontrol.add(InlineKeyboardButton(
            text='Остановить',
            callback_data=show_broadcast_pages.new("ch_br_stat",param1=broadcast_obj['broadcast_id'], param2='finished')
        ))
    elif broadcast_obj['status']=='finished':
        broadcastcontrol.add(InlineKeyboardButton(
            text='Запустить',
            callback_data=show_broadcast_pages.new("ch_br_stat",param1=broadcast_obj['broadcast_id'], param2='active')
        ))

    broadcastcontrol.add(InlineKeyboardButton(
            text='↩️ назад',
            callback_data=show_broadcast_pages.new("show_list_broadcasts",param1=1, param2=broadcast_obj['status'])
        ))
    
    html_text="\n".join(
        [
            '<b>ID рассылки: </b>'+broadcast_obj['broadcast_id'],
            '<b>Статус: </b>'+broadcast_obj['status'],
            '<b>Запланировано на: </b>'+broadcast_obj['run_date']
        ]
    )
    await bot.send_photo(chat_id=call.from_user.id, photo=photoparser('usermainmenu'), caption= html_text,reply_markup=broadcastcontrol)



# Редактирование - другой пост вставить---------------------------------------------------
@dp.callback_query_handler(show_broadcast_pages.filter(command='ch_br_p'),state=[SupportManage.menu])
async def broadcast_change_post(call:types.CallbackQuery, callback_data:dict, state:FSMContext):
    bc_id = callback_data.get("param1")
    html_text="\n".join(
        [
            '<b>Отправьте пост</b>', 
        ]
    )
    broadcastcontrol = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
        [InlineKeyboardButton(
            text='Отменить и вернуться',
            callback_data=show_broadcast_pages.new("ch_br_p_ex",param1=bc_id, param2='none')
        )],
    ])

    await SupportManage.broadcast_post_edit_post.set()
    await state.update_data(broadcastid=bc_id)
    await call.message.edit_caption(caption=html_text, reply_markup=broadcastcontrol)

@dp.callback_query_handler(show_broadcast_pages.filter(command='ch_br_p_ex'),state=[SupportManage.broadcast_post_edit_post,SupportManage.broadcast_post_edit_date])
async def broadcast_change_post_decline(call:types.CallbackQuery, callback_data:dict):
    bc_id = callback_data.get("param1")
    broadcast_obj=broadcast_collection.find_one({"broadcast_id":bc_id})

    await bot.forward_message(chat_id=call.from_user.id, from_chat_id=broadcast_obj['user_id'], message_id=broadcast_obj['message_id'], disable_notification=True)

    broadcastcontrol = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
        [InlineKeyboardButton(
            text='Отредактировать пост',
            callback_data=show_broadcast_pages.new("ch_br_p",param1=broadcast_obj['broadcast_id'], param2='none')
        )],
        [InlineKeyboardButton(
            text='Сменить дату рассылки',
            callback_data=show_broadcast_pages.new("ch_br_dt",param1=broadcast_obj['broadcast_id'], param2='none')
        )],
    ])

    if broadcast_obj['status']=='active':
        broadcastcontrol.add(InlineKeyboardButton(
            text='Остановить',
            callback_data=show_broadcast_pages.new("ch_br_stat",param1=broadcast_obj['broadcast_id'], param2='finished')
        ))
    elif broadcast_obj['status']=='finished':
        broadcastcontrol.add(InlineKeyboardButton(
            text='Запустить',
            callback_data=show_broadcast_pages.new("ch_br_stat",param1=broadcast_obj['broadcast_id'], param2='active')
        ))

    broadcastcontrol.add(InlineKeyboardButton(
            text='↩️ назад',
            callback_data=show_broadcast_pages.new("show_list_broadcasts",param1=1, param2=broadcast_obj['status'])
        ))
    
    html_text="\n".join(
        [
            '<b>ID рассылки: </b>'+broadcast_obj['broadcast_id'],
            '<b>Статус: </b>'+broadcast_obj['status'],
            '<b>Запланировано на: </b>'+broadcast_obj['run_date']
        ]
    )
    await SupportManage.menu.set()
    await bot.send_photo(chat_id=call.from_user.id, photo=photoparser('usermainmenu'), caption= html_text,reply_markup=broadcastcontrol)

@dp.message_handler(content_types=['text', 'photo','document','audio','video', 'video_note'],state=[SupportManage.broadcast_post_edit_post])
async def broadcast_change_post_part_one(message:types.Message,state:FSMContext):
    data = await state.get_data()
    broadcastid = data.get("broadcastid")
    try:
        await scheduler.remove_job(job_id=broadcastid)
    except:
        pass

    broadcast_obj=broadcast_collection.find_one({"broadcast_id":broadcastid})
    broadcast_date=broadcast_obj['run_date']
    thistext=broadcast_date.split('_')
    datearr=thistext[0].split('-')
    timearr=thistext[1].split(':')

    scheduler.add_job(broadcaster_go, 'date', id=broadcastid, run_date=datetime(int(datearr[2]), int(datearr[1]), int(datearr[0]), int(timearr[0]), int(timearr[1])), kwargs={'thisuser':message.from_user.id, 'message_id':message.message_id, 'sendto':broadcast_obj['partners'], 'broadcast_id':broadcastid})
    
   
    broadcast_collection.find_one_and_update(
        { "broadcast_id":broadcastid },
        {"$set":{ "message_id":message.message_id }}
    )
    html_text="\n".join(
        [
            '<b>Вы отредактировали пост. Нажмите на кнопку чтобы вернуться к меню управления данной рассылкой</b>', 
        ]
    )
    broadcastcontrol = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
        [InlineKeyboardButton(
            text='Готово',
            callback_data=show_broadcast_pages.new("sb_ob",param1=broadcastid, param2='none')
        )],
    ])

    await SupportManage.menu.set()
    await message.answer_photo(caption=html_text,parse_mode='HTML',reply_markup=broadcastcontrol, photo=photoparser('operatormainmenu') )
# ---------------------------------


# Редактирование - другая дата---------------------------------------------------
@dp.callback_query_handler(show_broadcast_pages.filter(command='ch_br_dt'),state=[SupportManage.menu])
async def broadcast_change_post_decline(call:types.CallbackQuery, callback_data:dict, state:FSMContext):
    bc_id = callback_data.get("param1")
    html_text="\n".join(
        [
            '<b>Введите дату и время в формате "30-12-2000 в 16:45"</b>', 
        ]
    )
    broadcastcontrol = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
        [InlineKeyboardButton(
            text='Отменить и вернуться',
            callback_data=show_broadcast_pages.new("ch_br_p_ex",param1=bc_id, param2='none')
        )],
    ])

    await SupportManage.broadcast_post_edit_date.set()
    await state.update_data(broadcastid=bc_id)
    await call.message.edit_caption(caption=html_text, reply_markup=broadcastcontrol)

@dp.message_handler(state=[SupportManage.broadcast_post_edit_date])
async def broadcasta_time(message:types.Message,state:FSMContext):
    data = await state.get_data()
    broadcast_id = data.get("broadcastid")

    try:
        await scheduler.remove_job(job_id=broadcast_id)
    except:
        pass

    thistext=message.text.split(' в ')
    finaltext=thistext[0]+'_'+thistext[1]
    datearr=thistext[0].split('-')
    timearr=thistext[1].split(':')

    broadcast_obj=broadcast_collection.find_one({"broadcast_id":broadcast_id})

    scheduler.add_job(broadcaster_go, 'date', id=broadcast_id, run_date=datetime(int(datearr[2]), int(datearr[1]), int(datearr[0]), int(timearr[0]), int(timearr[1])), kwargs={'thisuser':broadcast_obj['user_id'], 'message_id':broadcast_obj['message_id'], 'sendto':broadcast_obj['partners'], 'broadcast_id':broadcast_id})
    
    broadcast_collection.find_one_and_update(
        { "broadcast_id":broadcast_id },
        {"$set":{ "run_date":finaltext }}
    )

    html_text="\n".join(
        [
            '<b>Вы отредактировали дату. Нажмите на кнопку чтобы вернуться к меню управления данной рассылкой</b>', 
        ]
    )
    broadcastcontrol = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
        [InlineKeyboardButton(
            text='Готово',
            callback_data=show_broadcast_pages.new("sb_ob",param1=broadcast_id, param2='none')
        )],
    ])

    await SupportManage.menu.set()
    await message.answer_photo(caption=html_text,parse_mode='HTML',reply_markup=broadcastcontrol, photo=photoparser('operatormainmenu') )
# ---------------------------------


# Редактирование - on/off---------------------------------------------------
@dp.callback_query_handler(show_broadcast_pages.filter(command='ch_br_stat'),state=[SupportManage.menu])
async def broadcast_onoff(call:types.CallbackQuery, callback_data:dict, state:FSMContext):
    await call.message.delete()  
    broadcast_id = callback_data.get("param1")
    bc_action = callback_data.get("param2")


    try:
        await scheduler.remove_job(job_id=broadcast_id)
    except:
        pass

    broadcast_collection.find_one_and_update(
        { "broadcast_id":broadcast_id},
        { "$set":{"status":bc_action}}
    )
    broadcast_obj=broadcast_collection.find_one({"broadcast_id":broadcast_id})
    if bc_action=='active':
        
        broadcast_date=broadcast_obj['run_date']
        thistext=broadcast_date.split('_')
        datearr=thistext[0].split('-')
        timearr=thistext[1].split(':')
        scheduler.add_job(broadcaster_go, 'date', id=broadcast_id, run_date=datetime(int(datearr[2]), int(datearr[1]), int(datearr[0]), int(timearr[0]), int(timearr[1])), kwargs={'thisuser':broadcast_obj['user_id'], 'message_id':broadcast_obj['message_id'], 'sendto':broadcast_obj['partners'], 'broadcast_id':broadcast_id})
    

    broadcastcontrol = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
        [InlineKeyboardButton(
            text='Отредактировать пост',
            callback_data=show_broadcast_pages.new("ch_br_p",param1=broadcast_obj['broadcast_id'], param2='none')
        )],
        [InlineKeyboardButton(
            text='Сменить дату рассылки',
            callback_data=show_broadcast_pages.new("ch_br_dt",param1=broadcast_obj['broadcast_id'], param2='none')
        )],
    ])

    if broadcast_obj['status']=='active':
        broadcastcontrol.add(InlineKeyboardButton(
            text='Остановить',
            callback_data=show_broadcast_pages.new("ch_br_stat",param1=broadcast_obj['broadcast_id'], param2='finished')
        ))
    elif broadcast_obj['status']=='finished':
        broadcastcontrol.add(InlineKeyboardButton(
            text='Запустить',
            callback_data=show_broadcast_pages.new("ch_br_stat",param1=broadcast_obj['broadcast_id'], param2='active')
        ))

    broadcastcontrol.add(InlineKeyboardButton(
            text='↩️ назад',
            callback_data=show_broadcast_pages.new("show_list_broadcasts",param1=1, param2=broadcast_obj['status'])
        ))
    
    html_text="\n".join(
        [
            '<b>ID рассылки: </b>'+broadcast_obj['broadcast_id'],
            '<b>Статус: </b>'+broadcast_obj['status'],
            '<b>Запланировано на: </b>'+broadcast_obj['run_date']
        ]
    )
    await bot.send_photo(chat_id=call.from_user.id, photo=photoparser('usermainmenu'), caption= html_text,reply_markup=broadcastcontrol)