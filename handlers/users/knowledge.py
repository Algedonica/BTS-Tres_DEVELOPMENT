from aiogram import types
import secrets
import math
from data.config import user_collection, staff_collection, settings_collection, knowledge_collection
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from loader import dp,bot
from states import ProjectManage,SupportManage, SetupBTSstates
from aiogram.dispatcher import FSMContext
from utils.misc import issupport, isadmin, support_role_check, xstr, photoparser
from aiogram.types import InputMediaPhoto
from keyboards.default import defaultmenu,operatorshowuser
from keyboards.inline import usersupportchoiceinline, ticket_callback, add_operator_callback, show_support_pages, edit_something_admin, show_cities_pages, knowledge_list_call




@dp.message_handler(state=ProjectManage.menu, text='📚 Новичку')
async def knwoledge_user_show(message: types.Message):
    itemstoshow=knowledge_collection.find({'parent':'main','item_id': {'$ne': 'main'}})
    html_text="\n".join(
        [
            'Здесь вы можете найти всю необходимую информацию, чтобы сложилось понимание о криптовалютах и о том, как их приобрести и хранить.', 
            ' ',
            'Выберите интересующий раздел:'
        ]
    )
    inlinekeys = InlineKeyboardMarkup(row_width=2)
    for x in itemstoshow:
        inlinekeys.add(InlineKeyboardButton(text=x['title'], callback_data=knowledge_list_call.new("shfqfrusr",param1=x['item_id'], param2='none')))
    inlinekeys.add(InlineKeyboardButton(
            text='↩️ Назад',
            callback_data='userbacktomenu'
            ))
    await message.answer_photo(photo=photoparser('userknowledgebase'),caption=html_text, reply_markup=inlinekeys)

@dp.callback_query_handler(knowledge_list_call.filter(command='shfqfrusr'), state=ProjectManage.menu)
async def show_knowledge_user_item_func(call: types.CallbackQuery, callback_data:dict):
    thissection=callback_data.get('param1')
    thissection_items=knowledge_collection.find({"parent":thissection, 'item_id': {'$ne': 'main'}})
    thissection = knowledge_collection.find_one({'item_id':thissection})
    if thissection['photo_knowledge']!='none':
        finalphoto=thissection['photo_knowledge']
    else:
        finalphoto=photoparser('userknowledgebase')
    if thissection['item_id'] == 'main':
        html_text="\n".join(
            [
                'Здесь вы можете найти всю необходимую информацию, чтобы сложилось понимание о криптовалютах и о том, как их приобрести и хранить.', 
                ' ',
                'Выберите интересующий раздел:'
            ]
        )
        inlinekeys = InlineKeyboardMarkup(row_width=2)
        for x in thissection_items:
            inlinekeys.add(InlineKeyboardButton(text=x['title'], callback_data=knowledge_list_call.new("shfqfrusr",param1=x['item_id'], param2='none')))
        inlinekeys.add(InlineKeyboardButton(
            text='↩️ Назад',
            callback_data='userbacktomenu'
            ))
        await call.message.edit_media(media=InputMediaPhoto(finalphoto, caption=html_text), reply_markup=inlinekeys)
    else:
        html_text="\n".join(
            [
                '<b>'+thissection['title']+'</b>',
                ' ',
                thissection['description']
            ]
        )
        inlinekeys = InlineKeyboardMarkup(row_width=2)
        for x in thissection_items:
            inlinekeys.add(InlineKeyboardButton(text=x['title'], callback_data=knowledge_list_call.new("shfqfrusr",param1=x['item_id'], param2='none')))
        inlinekeys.add(InlineKeyboardButton(text='↩️ Назад', callback_data=knowledge_list_call.new("shfqfrusr",param1=thissection['parent'], param2='none')))
    
        
        await call.message.edit_media(media=InputMediaPhoto(finalphoto, caption=html_text), reply_markup=inlinekeys)


@dp.callback_query_handler(knowledge_list_call.filter(command='show_faq'), state=SupportManage.menu)
async def show_knowledge_func(call: types.CallbackQuery, callback_data:dict):
    thissection=callback_data.get('param1')
    thissection_items=knowledge_collection.find({"parent":thissection})
    thissection = knowledge_collection.find_one({'item_id':thissection})
    if thissection['photo_knowledge']!='none':
        finalphoto=thissection['photo_knowledge']
    else:
        finalphoto=photoparser('adminknowledgebase')
    if thissection['item_id'] == "main":
        html_text="\n".join(
            [
                '<b>Вы находитесь в меню управления разделами базы знаний</b>'
            ]
        )
        inlinekeys = InlineKeyboardMarkup(row_width=2)
        for x in thissection_items:
            if x['item_id'] != "main":
                inlinekeys.add(InlineKeyboardButton(text=x['title'], callback_data=knowledge_list_call.new("show_faq",param1=x['item_id'], param2='none')))

        inlinekeys.add(InlineKeyboardButton(text='Добавить раздел', callback_data=knowledge_list_call.new("add_faq",param1=thissection['item_id'], param2='none')))
        inlinekeys.add(InlineKeyboardButton(text='◀️ главное меню', callback_data='to_admin_menu'))

        await call.message.edit_media(media=InputMediaPhoto(finalphoto, caption=html_text), reply_markup=inlinekeys)
    else:
        html_text="\n".join(
            [
                'Название раздела: '+thissection['title'],
                ' ',
                'Описание раздела: ',
                ' ',
                thissection['description']
            ]
        )
        inlinekeys = InlineKeyboardMarkup(row_width=2)
        for x in thissection_items:
            if x['item_id'] != "main":
                inlinekeys.add(InlineKeyboardButton(text=x['title'], callback_data=knowledge_list_call.new("show_faq",param1=x['item_id'], param2='none')))

        inlinekeys.add(InlineKeyboardButton(text='Изменить название раздела', callback_data=knowledge_list_call.new("edit_title_faq",param1=thissection['item_id'], param2='none')))
        inlinekeys.add(InlineKeyboardButton(text='Изменить описание раздела', callback_data=knowledge_list_call.new("edit_descr_faq",param1=thissection['item_id'], param2='none')))
        inlinekeys.add(InlineKeyboardButton(text='Удалить раздел', callback_data=knowledge_list_call.new("del_item_faq",param1=thissection['item_id'], param2='none')))


        inlinekeys.add(InlineKeyboardButton(text='Добавить раздел', callback_data=knowledge_list_call.new("add_faq",param1=thissection['item_id'], param2='none')))
        inlinekeys.add(InlineKeyboardButton(text='◀️ на уровень выше', callback_data=knowledge_list_call.new("show_faq",param1=thissection['parent'], param2="none")))

        await call.message.edit_media(media=InputMediaPhoto(finalphoto, caption=html_text), reply_markup=inlinekeys)

@dp.callback_query_handler(knowledge_list_call.filter(command='add_faq'), state=SupportManage.menu)
async def add_knowledge_func(call: types.CallbackQuery, callback_data:dict):
    thisnewid=secrets.token_hex(10)
    thissection=callback_data.get('param1')
    thissection_items=knowledge_collection.find({"parent":thissection})
    thissection = knowledge_collection.find_one({'item_id':thissection})
    if thissection['photo_knowledge']!='none':
        finalphoto=thissection['photo_knowledge']
    else:
        finalphoto=photoparser('adminknowledgebase')

    knowledge_collection.insert_one(
        {"item_id": thisnewid,
        "description":'none',
        "videocircle":'none',
        "parent": thissection['item_id'],
        "title": "none",
        "photo_knowledge":"none"})

    await call.answer('Раздел создан')


    if thissection['item_id'] == "main":
        html_text="\n".join(
            [
                '<b>Вы находитесь в меню управления разделами базы знаний</b>'
            ]
        )
        inlinekeys = InlineKeyboardMarkup(row_width=2)
        for x in thissection_items:
            if x['item_id'] != "main":
                inlinekeys.add(InlineKeyboardButton(text=x['title'], callback_data=knowledge_list_call.new("show_faq",param1=x['item_id'], param2='none')))

        inlinekeys.add(InlineKeyboardButton(text='Добавить раздел', callback_data=knowledge_list_call.new("add_faq",param1=thissection['item_id'], param2='none')))
        inlinekeys.add(InlineKeyboardButton(text='◀️ главное меню', callback_data='to_admin_menu'))

        await call.message.edit_media(media=InputMediaPhoto(finalphoto, caption=html_text), reply_markup=inlinekeys)
    else:
        html_text="\n".join(
            [
                'Название раздела: '+thissection['title'],
                ' ',
                'Описание раздела: ',
                ' ',
                thissection['description']
            ]
        )
        inlinekeys = InlineKeyboardMarkup(row_width=2)
        for x in thissection_items:
            if x['item_id'] != "main":
                inlinekeys.add(InlineKeyboardButton(text=x['title'], callback_data=knowledge_list_call.new("show_faq",param1=x['item_id'], param2='none')))

        inlinekeys.add(InlineKeyboardButton(text='Изменить название раздела', callback_data=knowledge_list_call.new("edit_title_faq",param1=thissection['item_id'], param2='none')))
        inlinekeys.add(InlineKeyboardButton(text='Изменить описание раздела', callback_data=knowledge_list_call.new("edit_descr_faq",param1=thissection['item_id'], param2='none')))
        inlinekeys.add(InlineKeyboardButton(text='Удалить раздел', callback_data=knowledge_list_call.new("del_item_faq",param1=thissection['item_id'], param2='none')))


        inlinekeys.add(InlineKeyboardButton(text='Добавить раздел', callback_data=knowledge_list_call.new("add_faq",param1=thissection['item_id'], param2='none')))
        inlinekeys.add(InlineKeyboardButton(text='◀️ на уровень выше', callback_data=knowledge_list_call.new("show_faq",param1=thissection['parent'], param2="none")))

        await call.message.edit_media(media=InputMediaPhoto(finalphoto, caption=html_text), reply_markup=inlinekeys)
    


@dp.callback_query_handler(knowledge_list_call.filter(command='edit_title_faq'), state=SupportManage.menu)
async def edit_title_knowledge_func(call: types.CallbackQuery, callback_data:dict, state: FSMContext):
    html_text="\n".join(
        [
            '<b>Введите новое название раздела</b>'
        ]
    )
    await SupportManage.knowledge_set_title.set()
    await state.update_data(new_title_faq=callback_data.get('param1'))
    await call.message.edit_media(media=InputMediaPhoto(photoparser('adminknowledgebase_change_name'), caption=html_text), reply_markup=None)

@dp.message_handler(state=SupportManage.knowledge_set_title)
async def write_new_title_knowledge_func(message: types.Message, state: FSMContext):
    data = await state.get_data()
    thisitem = data.get("new_title_faq")
    knowledge_collection.find_and_modify( 
        query={"item_id":thisitem}, 
        update={ "$set": { 'title':message.text }}
        )
    await state.reset_state()
    await SupportManage.menu.set()
    inlinekeys = InlineKeyboardMarkup(row_width=2)
    inlinekeys.add(InlineKeyboardButton(text='◀️ назад к разделу', callback_data=knowledge_list_call.new("show_faq",param1=thisitem, param2="none")))
    await message.answer_photo(photo=photoparser("adminknowledgebase_change_name_done"), caption=" ", reply_markup=inlinekeys)


@dp.callback_query_handler(knowledge_list_call.filter(command='edit_descr_faq'), state=SupportManage.menu)
async def edit_descr_knowledge_func(call: types.CallbackQuery, callback_data:dict, state: FSMContext):
    html_text="\n".join(
        [
            '<b>Введите новое описание раздела</b>'
        ]
    )
    await SupportManage.knowledge_set_descr.set()
    await state.update_data(new_descr_faq=callback_data.get('param1'))
    await call.message.edit_media(media=InputMediaPhoto(photoparser('adminknowledgebase'), caption=html_text), reply_markup=None)

@dp.message_handler(state=SupportManage.knowledge_set_descr)
async def write_new_descr_knowledge_func(message: types.Message, state: FSMContext):
    data = await state.get_data()
    thisitem = data.get("new_descr_faq")
    knowledge_collection.find_and_modify( 
        query={"item_id":thisitem}, 
        update={ "$set": { 'description':message.text }}
        )
    await state.reset_state()
    await SupportManage.menu.set()
    inlinekeys = InlineKeyboardMarkup(row_width=2)
    inlinekeys.add(InlineKeyboardButton(text='◀️ назад к разделу', callback_data=knowledge_list_call.new("show_faq",param1=thisitem, param2="none")))
    await message.answer_photo(photo=photoparser("adminknowledgebase"), caption=" ", reply_markup=inlinekeys)





@dp.callback_query_handler(knowledge_list_call.filter(command='del_item_faq'), state=SupportManage.menu)
async def ask_for_delete_knowledge_func(call: types.CallbackQuery, callback_data:dict):
    await call.answer(cache_time=0)
    html_text="\n".join(
        [
            'Удалить раздел?',
        ]
    )
    inlinekeys = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
        [InlineKeyboardButton(
            text='❌ Да, удалить',
            callback_data=knowledge_list_call.new("done_delete_faq",param1=callback_data.get('param1'), param2="none")
        )],
        [InlineKeyboardButton(
            text='◀️ Нет, оставить',
            callback_data=knowledge_list_call.new("show_faq",param1=callback_data.get('param1'), param2="none")
        )],
    ])
    # await call.message.edit_text(text=html_text,parse_mode='HTML', reply_markup=inlinekeys)
    await call.message.edit_media(media=InputMediaPhoto(media=photoparser("deletetagask"), caption=html_text), reply_markup=inlinekeys) 


@dp.callback_query_handler(knowledge_list_call.filter(command='done_delete_faq'), state=SupportManage.menu)
async def deleting_knowledge_func(call: types.CallbackQuery, callback_data:dict):
    thisitem=callback_data.get('param1')
    thisdoc = knowledge_collection.find_one({'item_id':thisitem})
    thisdocparent = thisdoc['parent']
    html_text="\n".join(
        [
            'Удаление завершено',
        ]
    )
# .remove
    i = False
    target_list=[thisitem]

    while i == False:
        if len(target_list)==0:
            i = True
            break
        knowledge_collection.remove({'item_id':{"$in": target_list}})
        childrenobjects = knowledge_collection.find({'parent': {"$in": target_list}})
        target_list=[]
        for x in childrenobjects:
            target_list.append(x['item_id'])

    
    

    inlinekeys = InlineKeyboardMarkup(row_width=2)
    inlinekeys.add(InlineKeyboardButton(text='◀️ назад к базе знаний', callback_data=knowledge_list_call.new("show_faq",param1=thisdocparent, param2="none")))



    await call.message.edit_media(media=InputMediaPhoto(media=photoparser("deletetagask"), caption=html_text), reply_markup=inlinekeys) 