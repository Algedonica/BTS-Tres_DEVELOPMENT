import os

from dotenv import load_dotenv

import pymongo
import array
load_dotenv()
client = pymongo.MongoClient(str(os.getenv("db_connect")))

states_connect=str(os.getenv("states_connect"))

db = client.cryptocons_dev
user_collection = db.users
ticket_collection= db.tickets
staff_collection=db.staff
settings_collection = db.settings
dbstates = client.aiogram_fsm
states_collection=dbstates.aiogram_state
knowledge_collection = db.knowledge_base
pmessages_collection = db.personal_message
videos_collection = db.videos
photos_collection=db.photos
videocircles_collection=db.videocircle
partner_collection=db.partner
links_collection=db.partnerlinks
broadcast_collection=db.broadcast

inline_materials_collection=db.inline_materials

settings_obj=settings_collection.find_one({"settings":"mainsettings"})
channelid=settings_obj['main_channel_id']

BOT_TOKEN = str(os.getenv("BOT_TOKEN"))
admins = [
    
]
admincode = str(os.getenv("admincode"))
ip = os.getenv("ip")



aiogram_redis = {
    'host': ip,
}

redis = {
    'address': (ip, 6379),
    'encoding': 'utf8'
}
