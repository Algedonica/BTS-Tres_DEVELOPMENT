from pymongo import settings
from data.config import language_collection, partner_collection,staff_collection, ticket_collection, settings_collection,  photos_collection, channelid, user_collection, links_collection
from loader import dp, bot
from datetime import datetime
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, user, KeyboardButton, ReplyKeyboardMarkup



def issupport(x):
    thisuser=staff_collection.find({"user_id":x, "$or":[{"staffrole":"support"},{"staffrole":"owner"}, {"staffrole":"admin"}]})
    if thisuser.count()==1:
        return True      
    else:
        return False
def isowner(x):
    thisuser=staff_collection.find({"user_id":x, "$or":[{"staffrole":"owner"}]})
    if thisuser.count()==1:
        return True      
    else:
        return False
def isadmin(x):
    thisuser=staff_collection.find({"user_id":x, "$or":[{"staffrole":"owner"},{"staffrole":"admin"}]})
    if thisuser.count()==1:
        return True      
    else:
        return False

def ispartnerowner(x):
    partner_objs=partner_collection.find({'owned_by':x})
    if partner_objs==None:
        return 'none'
    else:
        ret_arr=[]
        for partner in partner_objs:
            ret_arr.append(partner['unique_id'])
        return ret_arr
            
def support_role_check(x):
    thisuser=staff_collection.find_one({"user_id":x})
    if thisuser["role"]=="1":
        return 'MAIN'      
    else:
        return 'PLUS'

def reverse_check(x):
    thisuser=staff_collection.find_one({"user_id":x})
    if thisuser!=None:
        if thisuser["isreverse"]==True:
            return False      
        else:
            return True
    else:
        return True


def get_partner_channel(x):
    asd=partner_collection.find_one({'system_tag':x})
    channel_partner=asd["channel_id"]
    return channel_partner
def get_user_city(x):
    asd=user_collection.find_one({'user_id':x})
    cities_obj=asd["citytag"]
    return cities_obj

def get_user_came_from(x):
    asd=user_collection.find_one({'user_id':x})
    cities_obj=asd["came_from"]
    return cities_obj

# def parse_message_by_tag_name(x):
#     asd = pmessages_collection.find_one({"tag_name":x})
#     if asd==None:
#         return ''
#     return asd['text']

async def check_error_ticket(x):
    asd = ticket_collection.find_one({'ticketid':x})
    if asd==None:
        return ''
    elif asd['isopen']=='created':
        returning='Connection failed. Perhaps bot was banned from client side.'
        
        counttickets=ticket_collection.find().count()+1

        if asd['operator']=='none':
            
            operatorcallmeas='none'
            operatornickname='none'
        else:
            operatornickname=staff_collection.find_one({'user_id':asd['operator']})
            operatorcallmeas=operatornickname['callmeas']
            operatornickname=operatornickname['username']

        clientnickname=user_collection.find_one({'user_id':asd['userid']})
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
                '<b>Request № '+str(counttickets)+'</b>',
                asd['title'],
                '',
                '🗣 '+clientnickname+' - '+clientcallmeas,
                '👨‍💻 '+operatornickname+' - '+operatorcallmeas,
                '',
                '<i>'+asd['date'].strftime("%d.%m.%Y / %H:%M")+'</i>',
                asd['ticketid'],
                '',
                asd["messagedata"],
                '',
                '<b>‼️Error, perhaps bot was banned from client side‼️</b> <i>('+datetime.now().strftime("%d.%m.%Y / %H:%M")+')</i>',
                '',
                '=========================',
                '',
                "Request ended with error (bot was banned from client side)",
                "<i>"+datetime.now().strftime("%d.%m.%Y / %H:%M")+"</i>"

            ]
        ) 
        ticket_collection.update({"ticketid": asd['ticketid'], "isopen": "created"},{"$set":{"isopen":"botbanned","messagedata":datamessagehere}})
        await bot.send_message(chat_id=channelid, text=datamessagehere)

        return returning
    elif asd['isopen']=='paused':
        returning='Connection failed. Perhaps bot was banned from client side.'
    
        counttickets=ticket_collection.find().count()+1

        if asd['operator']=='none':
            
            operatorcallmeas='No nickname'
            operatornickname='No nickname'
        else:
            operatornickname=staff_collection.find_one({'user_id':asd['operator']})
            operatorcallmeas=operatornickname['callmeas']
            operatornickname=operatornickname['username']

        clientnickname=user_collection.find_one({'user_id':asd['userid']})
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
                '<b>Request № '+str(counttickets)+'</b>',
                asd['title'],
                '',
                '🗣 '+clientnickname+' - '+clientcallmeas,
                '👨‍💻 '+operatornickname+' - '+operatorcallmeas,
                '',
                '<i>'+asd['date'].strftime("%d.%m.%Y / %H:%M")+'</i>',
                asd['ticketid'],
                '',
                asd["messagedata"],
                '',
                '<b>‼️Error, perhaps bot was banned from client side‼️</b> <i>('+datetime.now().strftime("%d.%m.%Y / %H:%M")+')</i>',
                '',
                '=========================',
                '',
                "Request ended with error (bot was banned from client side)",
                "<i>"+datetime.now().strftime("%d.%m.%Y / %H:%M")+"</i>"

            ]
        ) 
        ticket_collection.update({"ticketid": asd['ticketid'], "isopen": "paused"},{"$set":{"isopen":"botbanned","messagedata":datamessagehere}})
        bot.send_message(chat_id=channelid, text=datamessagehere)

        return returning
    elif asd['isopen']=='onair':
        returning='Connection failed. Another support took this request.'
        return returning
    else:
        returning='Connection failed. Unknown error.'
        return returning

# -----------------media----parsers-----------------------


# def parse_video_by_tag_name(x):
#     asd = videos_collection.find_one({"name":x})
#     if asd==None:
#         return ''
#     return asd['video_id']

def parse_photos_by_tag_name(x):
    asd = photos_collection.find_one({"name":x})
    if asd==None:
        return ''
    return asd['photo_id']


# def parse_videocircles_by_tag_name(x):
#     asd = videocircles_collection.find_one({"name":x})
#     if asd==None:
#         return ''
#     return asd['videocircle_id']

def photoparser(x):
    asd = photos_collection.find_one({"name":x})
    if asd==None:
        return ''
    return asd['photo_id']



# -----------------media----parsers----end--------------

def xstr(s):
    if s is None:
        return 'none'
    return str(s)


def send_to_channel(x):
    asd = ticket_collection.find_one({"ticketid":x})
    bot.send_message(chat_id=channelid, text=asd['messagedata'])
    return False



def linkparser(x):
    asd = links_collection.find_one({"uniquename":x})
    if asd!=None:
        return asd['city'], asd['citycode'], asd['social']
    else:
        asd = links_collection.find_one({"uniquename":'default'})
        return asd['city'], asd['citycode'], asd['social']
def linkparser_default():
    asd = links_collection.find_one({"uniquename":'default'})
    return asd['city'], asd['citycode'], asd['social']    

def system_text_parser(x):
    asd=settings_collection.find_one({"settings":"mainsettings"})
    mytext=asd['text_system'][x]
    return mytext

def get_partner_obj(x):
    asd=partner_collection.find_one({'system_tag':x})
    return asd


def build_support_menu(x):
    html_text="\n".join(
        [
            get_text(text_code='support_main_menu', user_id=x)
        ]
    )
    supportmenubase = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
        [InlineKeyboardButton(
            text=get_text(text_code='support_incoming_requests_button_text', user_id=x),
            callback_data='to_tickets'
        )],
    ]) 
    if isadmin(x)== True:
        supportmenubase.add(InlineKeyboardButton(
        text=get_text(text_code='support_adminpanel_button_text', user_id=x),
        callback_data='to_admin_menu'
    ))
    if support_role_check(x)== "PLUS":
        supportmenubase.add(InlineKeyboardButton(
            text=get_text(text_code='support_report_button_text', user_id=x),
            callback_data='to_csv_tables'
        ))
        supportmenubase.add(InlineKeyboardButton(
            text=get_text(text_code='support_broadcast_button_text', user_id=x),
            callback_data='to_broadcast_admin'
        ))
    return html_text, supportmenubase


###############menu builders###################33
def build_user_menu(x):
    html_text="\n".join(
        [
            get_text(text_code='test_test', user_id=x)
        ]
    )
    defaultmenu = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=get_text('user_mainmenu_defbutton_text', x))
            ],
            [
                KeyboardButton(text='Simba Storage'),
                KeyboardButton(text='Tres'),
            ],
            [
                KeyboardButton(text='Foster'),
                KeyboardButton(text='Schutz'),
            
            ]
        ],
        resize_keyboard=True
    )
    return html_text, defaultmenu


def build_userendsupport(x):

    userendsupport = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=get_text('user_сlose_dialogue_two_button_text', x)) 
            ],
        ],
        resize_keyboard=True
    )
    return userendsupport


def build_operatorcontrol(x):

    operatorcontrol = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=get_text('user_end_dialogue_text', x)),
                KeyboardButton(text=get_text('user_shift_out_from_button_text', x)),
            ],
        ],
        resize_keyboard=True
    )
    return operatorcontrol

###############menu builders###################33

def group_valid_check(x):
    asd=[]
    settings_obj=settings_collection.find_one({"settings":"mainsettings"})
    asd.append(settings_obj['main_channel_id'])
    asd.append(settings_obj['main_group_id'])
    
    partners=partner_collection.find()
    for xy in partners:
        if xy['channel_id']!='none':
            asd.append(xy['channel_id'])
        if xy['group_id']!='none':
            asd.append(xy['group_id'])

    if x in asd:
        return True
    else:
        return False
    


def get_text(text_code, user_id):
    lang_obj=language_collection.find_one({'text_code':text_code})
    thisuser=user_collection.find_one({'user_id':user_id})
    user_lang=thisuser['lang_code']
    finaltext=lang_obj[user_lang]
    return finaltext


def broadcast_parse_activity(status, user_id):

    thisuser=user_collection.find_one({'user_id':user_id})
    user_lang=thisuser['lang_code']
    lang_obj=language_collection.find_one({'text_code':'support_broadcasts_status_'+status+'_text'})

    finaltext=lang_obj[user_lang]
    return finaltext