from aiogram import types


async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        types.BotCommand("start", "Launch the work"),
        types.BotCommand("reset", "Reset bot (if you got stuck)")
    ])

    await dp.bot.set_my_commands([
        types.BotCommand("start", "Начало работы"),
        types.BotCommand("reset", "Сброс (если все сломалось)")
    ], language_code='ru')
