from aiogram.utils.callback_data import CallbackData

ticket_callback=CallbackData("ticket_call","command","ticketid","operatorid")
add_operator_callback=CallbackData("add_operator_callback_factory","command","operator_role")
show_support_pages=CallbackData("show_support_pages_factory","command","page")
show_cities_pages=CallbackData("show_support_pages_factory","command","page")
edit_something_admin=CallbackData("edit_something_admin_factory","command","something","deleteoradd","userid")
csv_tables_call = CallbackData("showcsvpages_factory","command","param1","param2")
knowledge_list_call= CallbackData("knowledge_list_factory","command","param1","param2")
about_team_call= CallbackData("about_team_factory","command","param1","param2")

show_broadcast_pages=CallbackData("brdcstfctr","command","param1","param2")