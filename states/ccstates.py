from aiogram.dispatcher.filters import state
from aiogram.dispatcher.filters.state import StatesGroup,State

class ProjectManage(StatesGroup):
    menu = State()
    awaitingsup = State()
    initializingsup = State()
    preparingquest = State()
    onair = State()
    getnameuser = State()
    startmeeting = State()
    getcityuser = State()
    addglblcity = State()
class SupportManage(StatesGroup):
    menu = State()
    awaitingsup = State()
    initializingsup = State()
    onair = State()  
    changeoperatorname = State()  
    changeoperatorphoto = State()
    addcityinput = State() 
    initcsv = State()
    inittimecsv = State()
    accept_time = State()
    knowledge_set_title = State()
    knowledge_set_descr = State()

    broadcast_init=State()
    broadcast_get=State()
    broadcast_time=State()
    broadcast_finalgo=State()

    broadcast_post_edit_post=State()
    broadcast_post_edit_date=State()
class SetupBTSstates(StatesGroup):
    getadmincode = State()
    catchadmincode = State()
