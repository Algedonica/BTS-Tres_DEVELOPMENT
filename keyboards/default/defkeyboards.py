from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

defaultmenu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='🗣 Получить консультацию')
        ],
        [
            KeyboardButton(text='💎 О нас / услуги'),
            KeyboardButton(text='📚 Новичку'),
        ],
        [
             KeyboardButton(text='💵 Курс валют'),
            KeyboardButton(text='💎 Партнерам «КК»'),
           
        ]
    ],
    resize_keyboard=True
)

userendsupport = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='✅ Завершить диалог')
        ],
    ],
    resize_keyboard=True
)

operatorshowuser = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='🗣 Показать всех ожидающих')
        ],
    ],
    resize_keyboard=True
)

operatorcontrol = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='❌ Завершить'),
            KeyboardButton(text='🗣 Переключиться'),
        ],
    ],
    resize_keyboard=True
)