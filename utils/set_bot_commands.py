from aiogram import types


async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        types.BotCommand("start", "Launch the work"),
        types.BotCommand("reset", "Reset bot (if you got stuck)"),
        types.BotCommand("lang", "Language switch (only in menu)")
    ])

    await dp.bot.set_my_commands([
        types.BotCommand("start", "Начало работы"),
        types.BotCommand("reset", "Сброс (если все сломалось)"),
        types.BotCommand("lang", "Выбор языка (только в меню)")
    ], language_code='ru')
