from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

usersupportchoiceinline = InlineKeyboardMarkup(row_width=2, inline_keyboard=[
    [InlineKeyboardButton(
        text='Выбрать город',
        callback_data='pick_city'
    ),
    InlineKeyboardButton(
        text='Общий вопрос',
        callback_data='global_question'
    )],
    [InlineKeyboardButton(
        text='⬅ Вернуться в меню',
        callback_data='userbacktomenu'
    )]
])