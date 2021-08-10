from re import split
import secrets
import math
from datetime import datetime
from typing import Text
from aiogram import types
from loader import dp, bot
from data.config import inline_materials_collection, links_collection, partner_collection, user_collection, ticket_collection, staff_collection, settings_collection, states_collection, pmessages_collection, channelid
from states import ProjectManage,SupportManage
from aiogram.types import CallbackQuery,ReplyKeyboardRemove, InputFile, message
from aiogram.utils.callback_data import CallbackData
from utils.misc.logging import logging
from utils.misc import rate_limit
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher import FSMContext
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.types import InputMediaPhoto
from utils.misc import get_partner_channel,build_support_menu,system_text_parser,get_partner_obj,isadmin,support_role_check, xstr, photoparser, parse_message_by_tag_name, getCryptoData, parse_video_by_tag_name, send_to_channel, get_user_city,   get_user_came_from, check_error_ticket
from aiogram.utils.parts import safe_split_text
from aiogram.dispatcher.handler import CancelHandler
from keyboards.inline import usersupportchoiceinline, ticket_callback, add_operator_callback, show_support_pages, edit_something_admin, show_cities_pages, knowledge_list_call, about_team_call
from keyboards.default import userendsupport,defaultmenu, operatorcontrol,operatorshowuser

from aiogram.utils.exceptions import BotBlocked

from PIL import Image, ImageChops,ImageDraw, ImageFont

scheduler = AsyncIOScheduler()
async def clearnotified():
    staff_collection.find_and_modify(
        query={"staffrole":"support", "notified":"notified"},
        update={"$set":{"notified":"none"}}
    )

            
scheduler.add_job(clearnotified, 'interval', seconds=180)

import sys,os
pathname = os.path.dirname(sys.argv[0]) 
if pathname!='':
    pathname=pathname+'/'
@dp.message_handler(state=ProjectManage.menu, text='💵 Курс валют')
async def initialize_costs(message: types.Message):
    html_text="\n".join(
        [
            '<a href="t.me/cryptoconsbot?start=exchange">💎 Курс валют от ООО «Крипто Консалтинг»</a>'
        ]
    )


    img = Image.open(pathname+r"courses/courses.png")
    idraw = ImageDraw.Draw(img)

    usd_headline = ImageFont.truetype(pathname+r'courses/Jura-Bold.ttf', size=60)
    rub_headline = ImageFont.truetype(pathname+r'courses/Jura-Light.ttf', size=50)
    change24_headline = ImageFont.truetype(pathname+r'courses/Jura-Light.ttf', size=50)

    unicode_font = ImageFont.truetype(pathname+r"courses/arial.ttf", size=50)

    # SST
    text=getCryptoData('simba-storage-token')
    usd=str("{:,.2f}".format(text[0]))
    rub=str("{:,.2f}".format(text[1]))
    if text[2]>0:
        change24=str("{:,.2f}".format(text[2]))+'%'
        idraw.text((124,775), '▲', font=unicode_font, fill='#666666')
    else: 
        change24=str("{:,.2f}".format(text[2]))+'%'
        idraw.text((124,775), '▼', font=unicode_font, fill='#666666')
    
    idraw.text((182,632), usd, font=usd_headline, fill='#B2904B')
    idraw.text((182,710), rub, font=rub_headline, fill='#666666')
    idraw.text((182,775), change24, font=change24_headline, fill='#666666')

    
    # ------------------------------------

    # BTC
    text=getCryptoData('bitcoin')
    usd=str("{:,.2f}".format(text[0]))
    rub=str("{:,.2f}".format(text[1]))
    if text[2]>0:
        change24=str("{:,.2f}".format(text[2]))+'%'
        idraw.text((581,775), '▲', font=unicode_font, fill='#666666')
    else: 
        change24=str("{:,.2f}".format(text[2]))+'%'
        idraw.text((581,775), '▼', font=unicode_font, fill='#666666')
    
    idraw.text((639,632), usd, font=usd_headline, fill='#FF8A00')
    idraw.text((639,710), rub, font=rub_headline, fill='#666666')
    idraw.text((639,775), change24, font=change24_headline, fill='#666666')
    # -------------------------------------

    # ETH
    text=getCryptoData('ethereum')
    usd=str("{:,.2f}".format(text[0]))
    rub=str("{:,.2f}".format(text[1]))
    if text[2]>0:
        change24=str("{:,.2f}".format(text[2]))+'%'
        idraw.text((1038,775), '▲', font=unicode_font, fill='#666666')
    else: 
        change24=str("{:,.2f}".format(text[2]))+'%'
        idraw.text((1038,775), '▼', font=unicode_font, fill='#666666')
    
    idraw.text((1096,632), usd, font=usd_headline, fill='#62688F')
    idraw.text((1096,710), rub, font=rub_headline, fill='#666666')
    idraw.text((1096,775), change24, font=change24_headline, fill='#666666')
    # ------------------------------------

    datenow = datetime.now().strftime("%d.%m.%Y / %I:%M%p")
    idraw.text((948,1020), datenow, font=change24_headline, fill='#A1DACC')


    img.save(pathname+r'courses/simba.png')


    await bot.send_photo(chat_id=message.from_user.id,caption=html_text,parse_mode='HTML', photo=InputFile(pathname+r'courses/simba.png',filename='final-simba.png'))

@dp.message_handler(state=ProjectManage.menu, text='💎 Партнерам «КК»')
async def initialize_partners(message: types.Message):
    html_text="\n".join(
        [
            'Если вы хотите открыть представительство в своем городе, пожалуйста, заполните форму, нажав кнопку ниже: ',
        ]
    )
    inlinemenu=InlineKeyboardMarkup(row_width=2, inline_keyboard=[
        [InlineKeyboardButton(
            text='🤝 Стать партнером',
            url='http://bit.ly/cryptocons_partner'
            )
        ],
        [InlineKeyboardButton(
            text='↩️ Назад',
            callback_data='userbacktomenu'
            ),
        ]])
    await bot.send_photo(chat_id=message.from_user.id, caption=html_text, parse_mode='HTML', photo=photoparser('topartnerspic'), reply_markup=inlinemenu)





#---------------------------about-----us-------------------------------------

@dp.message_handler(state=ProjectManage.menu, text='💎 О нас / услуги')
async def aboutususer(message: types.Message):

    html_text="\n".join(
        [
            '<b>💎 ООО «Крипто Консалтинг» — компания, предоставляющая консалтинговые услуги в сфере  криптовалют в России.</b>',
            '<b>Основной партнер — швейцарский холдинг TRES Group GmbH.</b>',
            ' ',
            '🧠 Опыт работы на рынке СНГ с 2017 года. Полностью отслеживаемая история становления компании и более 1000 отзывов клиентов и инвесторов.',
            ' ',
            '<b>🗣 Мы оказываем многопрофильную помощь по криптовалютам:</b>',
        ]
    )

    inlinemenu=InlineKeyboardMarkup(row_width=2, inline_keyboard=[
        [InlineKeyboardButton(
            text='👩🏻‍💻 О команде',
            callback_data=about_team_call.new(command='showaboutcard', param1=1, param2='none')
            ),
        InlineKeyboardButton(
            text='💎 Консалтинг',
            callback_data='consulting_about_us'
            )
        ],
        [InlineKeyboardButton(
            text='💰 80-101% годовых',
            callback_data='earn_about_us'
            ),
            InlineKeyboardButton(
            text='🦁 Купить биткоин',
            callback_data='SIMBA_about_us'
            ),
        ],
        [InlineKeyboardButton(
            text='📚 Обучение',
            callback_data='learn_about_us'
            ), 
            InlineKeyboardButton(
            text='📈 Аналитика',
            callback_data='analytics_about_us'
            ),      
        ],
        [InlineKeyboardButton(
            text='💼 Инвестпортфель',
            callback_data='investport_about_us'
            ),
            InlineKeyboardButton(
            text='💱 Легальный обмен',
            callback_data='legal_change_about_us'
            ), 
        ],
        [InlineKeyboardButton(
            text='↩️ Назад',
            callback_data='userbacktomenu'
            ),
            InlineKeyboardButton(
            text='🧩 Другие',
            callback_data='another_about_us'
            ),
        ],
    ])

    # await bot.send_video(chat_id=message.from_user.id, video='BAACAgIAAxkBAAITBGB08pMf6qokJrqy-Eaaw36PcfKaAAIkDQACjFapS_Ary3cMrUSvHgQ', reply_markup=inlinemenu, caption=html_text)
    await bot.send_video(chat_id=message.from_user.id, video=parse_video_by_tag_name('about_kk_square'), reply_markup=inlinemenu, caption=html_text)





@dp.callback_query_handler(text='earn_about_us', state=[ProjectManage.menu])
async def earn_about_us_func(call: CallbackQuery):
    html_text="\n".join(
        [
            '✅ <b>283 445 800 ₽</b> под управлением',
            '✅ <b>57 442 309 ₽</b> инвестиций за апрель 2021',
            '✅ <b>13 331 472 ₽</b> выплачено тел вкладов в апреле 2021',
            '',
            '💵 Уже четыре года мы зарабатываем на криптовалютах.',
            'Главным источником заработка является трейдинг — купить по низкой цене, продать по высокой. Но не у каждого это получается и не каждый хочет, потому что требуется много усилий, времени и знаний. Чтобы получать прибыль и не вовлекаться самому, нашими партнерами был создан инвестиционный продукт SCHUTZ. Выбрав данную опцию вы можете получать от 80% годовых чистой прибыли в USDT (цифровой доллар) до 101% (удвоить депозит).',
            '',
            '💰 Вторым предложением нашей компании является составление инвестпортфеля в криптовалюте с годовой доходностью от 100%. А также большое количество «сигналов» на покупку и продажу Bitcoin.'
        ]
    )

    thisusercity=get_user_city(call.from_user.id)
    aboutobj=get_partner_obj(thisusercity)
        

    inlinemenu=InlineKeyboardMarkup(row_width=2, inline_keyboard=[
        [
        InlineKeyboardButton(
            text='⁉️ Ответы на вопросы',
            callback_data='schutz_faq_about_us'
            )    
        ],
        [
        InlineKeyboardButton(
            text='💵 Открыть вклад в SCHUTZ',
            url=aboutobj['datatext']['schutz_link']
            )    
        ],
        [InlineKeyboardButton(
            text='📃 Узнать о фонде больше',
            url='https://invest80.ru'
            ),
        ],
        [InlineKeyboardButton(
            text='↩️ Назад',
            callback_data='userbacktorookie'
            )  
        ]])
    await call.message.delete()
    # await bot.send_video(chat_id=call.from_user.id, video=parse_video_by_tag_name('about_kk_square'), reply_markup=inlinemenu, caption=html_text)
    await bot.send_photo(chat_id=call.from_user.id, caption=html_text, parse_mode='HTML', photo=photoparser('schutz_photo_ad'), reply_markup=inlinemenu)


@dp.callback_query_handler(text='schutz_faq_about_us', state=[ProjectManage.menu])
async def schutz_faq_about_us_func(call: CallbackQuery):
    html_text="\n".join(
        [
            '<b>1) 80% за год? Почему так много?</b>',
            '',
            '<i>Для рынка криптовалют 80% — это нормально. Давайте посчитаем, откуда берутся такие проценты?',
            'В марте 2020 года биткойн стоил $3500, а в этом году ≈ $60 000. Это больше чем в 10 раз!',
            'Рынок криптовалют очень волатилен. Что это значит? Это значит, что цена активов сильно колеблется.',
            'На данных изменениях зарабатывает Фонд, покупая дешево, продавая дороже. Сравнивая с фондовым рынком, даже профессиональные трейдеры могут делать 200% в год, но они это делают для себя, предлагая клиентам меньше. Это называется безрисковые стратегии.',
            '',
            'Ещё одно доказательство, что Фонд делает такой % прибыли — это статистика отработки по бесплатным ежемесячным рекомендациям, начиная с 2017 года. Все сделки можно проверить в открытом канале Neutrino @neutrinofund.</i>'
        ]
    )

    inlinemenu=InlineKeyboardMarkup(row_width=2, inline_keyboard=[
        [
        InlineKeyboardButton(
            text='▶️',
            callback_data='schutz_faq_about_us_two'
            )    
        ],
        [InlineKeyboardButton(
            text='↩️ Назад',
            callback_data='earn_about_us'
            )  
        ]])
    await call.message.delete()
    await bot.send_photo(chat_id=call.from_user.id, caption=html_text, parse_mode='HTML', photo=photoparser('schutz_photo_ad'), reply_markup=inlinemenu)

@dp.callback_query_handler(text='schutz_faq_about_us_two', state=[ProjectManage.menu])
async def schutz_faq_about_us_two_func(call: CallbackQuery):
    html_text="\n".join(
        [
            '<b>2) Какие есть гарантии?</b>',
            '',
            '<i>Возможно, в 2021 году в международном праве появятся законы по которым финансовые регуляторы смогут выдавать страховки управляющим фондам, компаниям, занимающимся управлением криптовалютами (именно торговлей!). Сейчас таких не существует, поскольку только-только создаются прецеденты регулирования на основании которых пишутся законы. Регуляторы во всем мире еще не придумали, как регулировать деятельность криптофондов. Как только такая возможность станет реальной, в фонде сразу появятся такие лицензии, предоставляющие клиенту гарантии.  Сейчас гарантия фонда — это 4 года работы и 100% выплат всем инвесторам, что подтверждено блокчейном Ethereum. Это свидетельствует об устойчивости компании, о наличии долгосрочной стратегии. Основатель и руководитель Фонда также имеет проекты, которые уже зарегистрированы в 🇨🇭Швейцарии, 🇱🇮Лихтенштейне, 🇦🇪ОАЭ и 🇳🇿 Новой Зеландии.</i>'
        ]
    )

    inlinemenu=InlineKeyboardMarkup(row_width=2, inline_keyboard=[
        [
        InlineKeyboardButton(
            text='◀️',
            callback_data='schutz_faq_about_us_two'
            ), 
        InlineKeyboardButton(
            text='▶️',
            callback_data='schutz_faq_about_us_three'
            )    
        ],
        [InlineKeyboardButton(
            text='↩️ Назад',
            callback_data='earn_about_us'
            )  
        ]])
    await call.message.delete()
    await bot.send_photo(chat_id=call.from_user.id, caption=html_text, parse_mode='HTML', photo=photoparser('schutz_photo_ad'), reply_markup=inlinemenu)

@dp.callback_query_handler(text='schutz_faq_about_us_three', state=[ProjectManage.menu])
async def schutz_faq_about_us_three_func(call: CallbackQuery):
    html_text="\n".join(
        [
            '<b>3) Как обменять рубли на USDT, законен ли обмен?</b>',
            '',
            '<i>В соответствии с Федеральным законом «О цифровых финансовых активах, цифровой валюте и о внесении изменений в отдельные законодательные акты Российской Федерации», на территории РФ криптовалюта признана имуществом, и с доходов уже в скором времени нужно будет платить налог. Закон разрешает обмен криптовалют в РФ у лицензированных источников. Лицензии будут выдаваться летом 2021. Сейчас обмен можно делать на криптобиржах, где это доступно. Существуют специальные площадки для обмена, например, Bestchange.</i>'
        ]
    )
    inlinemenu=InlineKeyboardMarkup(row_width=2, inline_keyboard=[
        [
        InlineKeyboardButton(
            text='◀️',
            callback_data='schutz_faq_about_us_three'
            ), 
        InlineKeyboardButton(
            text='▶️',
            callback_data='schutz_faq_about_us_four'
            )    
        ],
        [InlineKeyboardButton(
            text='↩️ Назад',
            callback_data='earn_about_us'
            )  
        ]])
    await call.message.delete()

    await bot.send_photo(chat_id=call.from_user.id, caption=html_text, parse_mode='HTML', photo=photoparser('schutz_photo_ad'), reply_markup=inlinemenu)

@dp.callback_query_handler(text='schutz_faq_about_us_four', state=[ProjectManage.menu])
async def schutz_faq_about_us_four_func(call: CallbackQuery):
    html_text="\n".join(
        [
            '<b>4) Как Крипто Консалтинг гарантирует мне, что с моими деньгами будет все хорошо?</b>',
            '',
            '<i>💎 «Крипто Консалтинг» — консалтинговая компания оказывающая консультационные услуги. Подбираем проекты, авторитетные фонды и компании. У нас своя система критериев оценки проектов. Компании-партнеры с которыми мы работаем, оправдывают доверие. SСHUTZ — криптофонд, работающий 4 года и за это время никогда не было осечек, особенно по сравнению с другими публичными криптовалютными проектами. Все выплаты производятся в срок и в обещанном количестве. Ежеквартальные отчеты позволяют видеть картину целиком. Сумма выплат превышает сумму вкладов в фонд — это означает, что в нём нет пирамидальной составляющей.',
            '',
            'Мы не берем на себя обязательства каким-либо образом страховать вклады клиентов, показываем лучший опыт заработка в криптовалютной сфере. У нас нет ни одного клиента которого как-то обманули и он потерял деньги. Только положительный опыт и успешные примеры. Мы открыты, а наша деятельность прозрачна.</i>'
        ]
    )

    inlinemenu=InlineKeyboardMarkup(row_width=2, inline_keyboard=[
        [
        InlineKeyboardButton(
            text='◀️',
            callback_data='schutz_faq_about_us_four'
            ), 
        InlineKeyboardButton(
            text='▶️',
            callback_data='schutz_faq_about_us_five'
            )    
        ],
        [InlineKeyboardButton(
            text='↩️ Назад',
            callback_data='earn_about_us'
            )  
        ]])
    await call.message.delete()
    await bot.send_photo(chat_id=call.from_user.id, caption=html_text, parse_mode='HTML', photo=photoparser('schutz_photo_ad'), reply_markup=inlinemenu)

@dp.callback_query_handler(text='schutz_faq_about_us_five', state=[ProjectManage.menu])
async def schutz_faq_about_us_five_func(call: CallbackQuery):
    html_text="\n".join(
        [
            '<b>5) Если с проектом SСHUTZ что-то случится, куда мне обращаться? </b>',
            '',
            '<i>Если что-то случается, мы, как проводник информации, как консультационное агентство расскажем клиенту о произошедших событиях в фонде. Мы держим клиентов информированными. При этом стоит помнить, что ООО «Крипто Консалтинг» рекомендует вам воспользоваться теми или иными сервисами и проектами, а не обязывает или принуждает. Мы рекомендуем лучшие решения на рынке, а решение принимает клиент. Если вы не готовы брать на себя риски, вам не стоит заходить на рынок криптовалют.</i>'
        ]
    )

    inlinemenu=InlineKeyboardMarkup(row_width=2, inline_keyboard=[
        [
        InlineKeyboardButton(
            text='◀️',
            callback_data='schutz_faq_about_us_five'
            ), 
        InlineKeyboardButton(
            text='▶️',
            callback_data='schutz_faq_about_us_six'
            )    
        ],
        [InlineKeyboardButton(
            text='↩️ Назад',
            callback_data='earn_about_us'
            )  
        ]])
    await call.message.delete()
    await bot.send_photo(chat_id=call.from_user.id, caption=html_text, parse_mode='HTML', photo=photoparser('schutz_photo_ad'), reply_markup=inlinemenu)

@dp.callback_query_handler(text='schutz_faq_about_us_six', state=[ProjectManage.menu])
async def schutz_faq_about_us_six_func(call: CallbackQuery):
    html_text="\n".join(
        [
            '<b>6) Где зарегистрирован фонд SCHUTZ? Я подписываю с ними какой-то договор?</b>',
            '',
            '<i>Фонд будет зарегистрирован в 2021 году. Из-за того, что ещё не было сформировано международное законодательство позволяющее вести лицензированную деятельность, работа фонда происходит в представленном варианте. Многие большие зарубежные фонды после работы 2-3 лет также начинают регистрацию в определенных юрисдикциях. На данный момент клиент подписывает с фондом SСHUTZ электронное соглашение, в котором указано условие действия депозита с описанным ограничением ответственности и рисками.',
            '',
            'С компанией ООО «Крипто Консалтинг» клиент подписывает бумажный договор на оказание КОНСУЛЬТАЦИОНЫХ услуг. Наша задача провести клиента по всем этапам безопасной сделки: от помощи в переводе его криптовалют на кошелек, до консультаций по сохранению всех приватных ключей, паролей, доступов. Консультации по ведению счёта, комиссиям в сети блокчейн, по обращению со счетом, по выводу в выгодный для клиента момент из USDT в рубли.</i>'
        ]
    )

    inlinemenu=InlineKeyboardMarkup(row_width=2, inline_keyboard=[
        [
        InlineKeyboardButton(
            text='◀️',
            callback_data='schutz_faq_about_us_six'
            ), 
        InlineKeyboardButton(
            text='▶️',
            callback_data='schutz_faq_about_us_seven'
            )    
        ],
        [InlineKeyboardButton(
            text='↩️ Назад',
            callback_data='earn_about_us'
            )  
        ]])
    await call.message.delete()

    await bot.send_photo(chat_id=call.from_user.id, caption=html_text, parse_mode='HTML', photo=photoparser('schutz_photo_ad'), reply_markup=inlinemenu)

@dp.callback_query_handler(text='schutz_faq_about_us_seven', state=[ProjectManage.menu])
async def schutz_faq_about_us_seven_func(call: CallbackQuery):
    html_text="\n".join(
        [
            '<b>7) Я ищу в Google информацию про фонд SCHUTZ и ничего не могу найти. Почему?</b>',
            '',
            '<i>Фонд SCHUTZ до 2021 года ни разу не рекламировался в сети. Фонд не создавал рекламных кампаний, не привлекал блогеров или копирайтеров для разборов, потому что это просто было не нужно. Фонд существует с 2017 года, это можно проверить по открытому каналу @neutrinofund. Так же в канале возможно проследить, когда для инвесторов была открыта возможность инвестировать и получать с инвестиций процент. Ранее фонд назывался NTS 80, по количеству процентов, которые он увеличивает инвесторам за год (расшифровка Neutrino Token Standart). В 2021 году фонд произвел ребрендинг, и теперь он называется – SCHUTZ.</i>'
        ]
    )

    inlinemenu=InlineKeyboardMarkup(row_width=2, inline_keyboard=[
        [
        InlineKeyboardButton(
            text='◀️',
            callback_data='schutz_faq_about_us_six'
            ),
        ], 
        [InlineKeyboardButton(
            text='↩️ Назад',
            callback_data='earn_about_us'
            )  
        ]])
    await call.message.delete()

    await bot.send_photo(chat_id=call.from_user.id, caption=html_text, parse_mode='HTML', photo=photoparser('schutz_photo_ad'), reply_markup=inlinemenu)








@dp.callback_query_handler(text='consulting_about_us', state=[ProjectManage.menu])
async def consulting_about_us_func(call: CallbackQuery):
    html_text="\n".join(
        [
            'У нас вы можете получить полный и самый актуальный перечень информации по любым вопросам связанным с криптовалютой: от хранения, обмена, заработка до аналитики и юридических аспектов. Задавайте их нашему консультанту, нажав «🗣 Получить консультацию»‎.',
            '',
            '<b>Юридические услуги</b>',
            'Если вы хотите платить налоги с криптоактивов или открыть компанию с уставным капиталом в криптовалюте в той юрисдикции, которая это предусматривает (Швейцария, Лихтенштейн, ОАЭ), мы можем провести вас по всему пути от точки А до точки Б.'
        ]
    )

    inlinemenu=InlineKeyboardMarkup(row_width=2, inline_keyboard=[
        [InlineKeyboardButton(
            text='↩️ Назад',
            callback_data='userbacktorookie'
            )  
        ],
    ])
    await call.message.delete()
    await bot.send_video(chat_id=call.from_user.id, video=parse_video_by_tag_name('consulting_video_square'), reply_markup=inlinemenu, caption=html_text)




@dp.callback_query_handler(text='SIMBA_about_us', state=[ProjectManage.menu])
async def SIMBA_about_us_func(call: CallbackQuery):
    html_text="\n".join(
        [
            'Покупайте и храните биткоин в надежном и удобным хранилище 🦁 <b>SIMBA Storage</b>',
            '',
            'Хранилище объединяет в себе преимущества горячего и холодного кошелька с серверами в 4-х странах: в 🇨🇭Швейцарии, 🇱🇮Лихтенштейне, 🇦🇪ОАЭ и 🇳🇿 Новой Зеландии.',
            '',
            'Зачем это нужно? По статистике, каждые сутки в мире пользователи теряют около 1500 биткоинов! Хранилище 🦁SIMBA Storage решает эту проблему.'
        ]
            
    )
    thisusercity=get_user_city(call.from_user.id)
    aboutobj=get_partner_obj(thisusercity)
        
    inlinemenu=InlineKeyboardMarkup(row_width=2, inline_keyboard=[
        [InlineKeyboardButton(
            text='📃 Читать далее...',
            url='https://telegra.ph/Pokupajte-i-hranite-bitkoin-v-nadezhnom-i-udobnym-hranilishche--SIMBA-Storage-07-11'
            )  
        ],
        [InlineKeyboardButton(
            text='🔗 Купить биткоин с карты',
            url=aboutobj['datatext']['simba_link_landing']
            )  
        ],
        [InlineKeyboardButton(
            text='🔑 Зарегистрироваться',
            url=aboutobj['datatext']['simba_link_reg']
            )  
        ],

        [InlineKeyboardButton(
            text='↩️ Назад',
            callback_data='userbacktorookie'
            )  
        ],
    ])
    await call.message.delete()
    await bot.send_photo(chat_id=call.from_user.id, photo=photoparser('simba_photo_ad'), reply_markup=inlinemenu, caption=html_text)



@dp.callback_query_handler(about_team_call.filter(command='showaboutcard'), state=[ProjectManage.menu])
async def team_about_us_func(call: CallbackQuery,  callback_data:dict):
    thisusercity=get_user_city(call.from_user.id)
    aboutobj=get_partner_obj(thisusercity)
    team_cards=aboutobj['team_cards']
    
    page = callback_data.get("param1")
    page = int(page)

    if page==1:
        prevpage = page - 1
        nextpage = page + 1

        thiscard=team_cards[page-1]
        thiscardtext=thiscard['text']
        thiscardphoto=thiscard['photo']
    elif page==9999:
        prevpage = 1
        nextpage = 2

        thiscard=team_cards[0]
        thiscardtext=thiscard['text']
        thiscardphoto=thiscard['photo']
    else:
        prevpage = page - 1
        if prevpage == 1:
            prevpage = 9999
        nextpage = page + 1

        thiscard=team_cards[page-1]
        thiscardtext=thiscard['text']
        thiscardphoto=thiscard['photo']

    inlinekeys = InlineKeyboardMarkup(row_width=2)

    
    if prevpage < 1:
        prevtoadd=InlineKeyboardButton(
            text='◀️',
            callback_data=about_team_call.new(command='showaboutcard', param1=1, param2='none')
        )
    else:
        prevtoadd=InlineKeyboardButton(
            text='◀️',
            callback_data=about_team_call.new(command='showaboutcard', param1=prevpage, param2='none')
        )

    if  len(team_cards)==page:
        nexttoadd=InlineKeyboardButton(
            text='▶️',
            callback_data=about_team_call.new(command='showaboutcard', param1=page, param2='none')
        )      
    else:
        nexttoadd=InlineKeyboardButton(
            text='▶️',
            callback_data=about_team_call.new(command='showaboutcard', param1=nextpage, param2='none')
        )

    inlinekeys.add(prevtoadd,nexttoadd)
    
    # inlinekeys
    backbutton=InlineKeyboardButton(
        text='↩️ Назад',
        callback_data='userbacktorookie'
        ) 
    inlinekeys.add(backbutton)
    html_text="\n".join(
        [
            thiscardtext
        ]
    )
    await call.message.delete()
    # await call.message.answer(text='k')
    await bot.send_photo(chat_id=call.from_user.id, photo=thiscardphoto, reply_markup=inlinekeys, caption=html_text)







@dp.callback_query_handler(text='keep_about_us', state=[ProjectManage.menu])
async def keep_about_us_func(call: CallbackQuery):
    html_text="\n".join(
        [
            'Каждый день теряется и крадётся большое количество Биткоинов. Эта цифра достигает 1500 биткоинов в день. Многие люди забывают данные от своих кошельков и теряют доступ к активам, а у других крадут активы мошенники. Криптовалюта — ценный актив и его нужно хранить бережно, в защите от постороннего доступа.',
            'Наша компания может проконсультировать вас по действиям для организации безопасного хранения криптовалюты на любом кошельке. Во-вторых мы предоставим возможность взаимодействия с нашей компанией-партнёром Simba Storage, которая предоставляет услуги по холодному хранению Биткоина в четырех Юрисдикциях: Швейцария, Лихтенштейн, ОАЭ, Новая Зеландия.'
        ]
    )

    inlinemenu=InlineKeyboardMarkup(row_width=2, inline_keyboard=[
        [InlineKeyboardButton(
            text='↩️ Назад',
            callback_data='userbacktorookie'
            )  
        ],
    ])
    await call.message.delete()
    await bot.send_video(chat_id=call.from_user.id, video=parse_video_by_tag_name('about_kk_square'), reply_markup=inlinemenu, caption=html_text)


@dp.callback_query_handler(text='learn_about_us', state=[ProjectManage.menu])
async def learn_about_us_func(call: CallbackQuery):
    html_text="\n".join(
        [
            '🎞 Начните проходить открытый начальный курс от Крипто Консалтинг',
            '<a href="https://www.youtube.com/watch?v=Q9zbGI1Dox0&list=PLsP_YSfuJ2Xsk66Q-GhHnLoiCWbxsXvZn">👉 в нашем youtube канале 👈</a>',
            '',
            '📈 Проводим персональное обучение трейдингу на рынке криптовалют. Для записи нажмите кнопку "Получить консультацию".'
        ]
    )

    inlinemenu=InlineKeyboardMarkup(row_width=2, inline_keyboard=[
        [InlineKeyboardButton(
            text='↩️ Назад',
            callback_data='userbacktorookie'
            )  
        ],
    ])
    await call.message.delete()
    await bot.send_video(chat_id=call.from_user.id, video=parse_video_by_tag_name('about_kk_square'), reply_markup=inlinemenu, caption=html_text)


@dp.callback_query_handler(text='analytics_about_us', state=[ProjectManage.menu])
async def analytics_about_us_func(call: CallbackQuery):
    html_text="\n".join(
        [
            'Ежедневное тщательное изучение рынка позволяет понимать и прогнозировать возможный рост или падение выбранного актива, что в свою очередь ведет к заработку. Однако без должных знаний рынок криптовалют не принесет прибыли неопытному пользователю. Именно поэтому мы предлагает услуги нашего партнёра — закрытого клуба <b>🇨🇭 TRES</b>.',
            '',
            '<b>🇨🇭 TRES</b> — швейцарская консалтинговая компания в сфере криптовалют и блокчейн. Покупая подписку <b>🇨🇭 TRES</b>, вы получаете право находиться в закрытом клубе (закрытый чат Telegram), в котором участникам доступны торговые рекомендации по рынку криптовалют, а также еженедельная аналитика рынка криптовалют. ',
            '',
            '<b>❗️ За прошлый год в закрытом клубе было около 90% прибыльных рекомендаций. ❗️</b>',
            '',
            'Если вы хотите самостоятельно взаимодействовать с криптовалютными биржами, покупать и продавать криптовалюту по предлагаемым сигналам, тогда это идеальная возможность для вас. Годовая прибыль составит от 100%.',
        ]
    )

    inlinemenu=InlineKeyboardMarkup(row_width=2, inline_keyboard=[
        [InlineKeyboardButton(
            text='↩️ Назад',
            callback_data='userbacktorookie'
            )  
        ],
    ])
    await call.message.delete()
    await bot.send_video(chat_id=call.from_user.id, video=parse_video_by_tag_name('about_kk_square'), reply_markup=inlinemenu, caption=html_text)



@dp.callback_query_handler(text='investport_about_us', state=[ProjectManage.menu])
async def investport_about_us_func(call: CallbackQuery):
    html_text="\n".join(
        [
            'Инвестиционный портфель — подбор криптовалютных активов 1-2 раза в год, с целью увеличить прибыль более 100% годовых. Криптовалютный портфель подразумевает, что аналитик выдает клиенту список активов, который нужно купить (количество каждого актива) и когда их нужно продать. Все деньги хранятся на счетах клиента. 3-4 раза в год происходит ребалансировка этого портфеля. Мы сообщаем какие активы нужно зафиксировать (продать), чтобы получить прибыль и рост каких активов мы ожидаем дальше.',
            '',
            '<b>Мы предлагаем</b> инвестиционный портфель на выбор:',
            '',
            '1️⃣  Ситуативный — составляется компанией Крипто Консалтинг в любой момент на рынке. В этот портфель входит 3-4 криптовактива. Этот портфель не зависит от цикла рынка (падающий или растущий). Стоимость данной услуги 30 000 ₽.',
            '',
            '2️⃣  Второй инвестпортфель составляется в конкретное время 2 раза в год в момент готовности рынка (перед растущим рынком). Содержит в себе 12-15 активов. Стоимость 70 000 ₽.'
        ]
    )

    inlinemenu=InlineKeyboardMarkup(row_width=2, inline_keyboard=[
        [InlineKeyboardButton(
            text='📈 Cтатистика',
            callback_data='userbacktorookie'
            ),  
        InlineKeyboardButton(
            text='📣 Отзывы',
            callback_data='userbacktorookie'
            )  
        ],
        [InlineKeyboardButton(
            text='↩️ Назад',
            callback_data='userbacktorookie'
            )  
        ],
    ])
    await call.message.delete()
    await bot.send_video(chat_id=call.from_user.id, video=parse_video_by_tag_name('about_kk_square'), reply_markup=inlinemenu, caption=html_text)

@dp.callback_query_handler(text='legal_change_about_us', state=[ProjectManage.menu])
async def legal_change_about_us_func(call: CallbackQuery):
    html_text="\n".join(
        [
            'Цифровые финансовые активы — название криптовалют в правовом поле. Признаны имуществом на территории РФ в 2021 г. Летом 2021 наша компания ожидает получения агентской лицензии на сделки с криптовалютой. В наших офисах вы сможете легально купить и продать криптовалюту.',
            '',
            'А пока вы можете воспользоваться популярным агрегатором с информацией о разных обменниках купли/продажи криптовалют https://bestchange.ru/'  
        ]
    )

    inlinemenu=InlineKeyboardMarkup(row_width=2, inline_keyboard=[
        [InlineKeyboardButton(
            text='❓ Как купить на bestchange',
            callback_data='userbacktorookie'
            )  
        ],
        [InlineKeyboardButton(
            text='↩️ Назад',
            callback_data='userbacktorookie'
            )  
        ],
    ])
    await call.message.delete()
    await bot.send_video(chat_id=call.from_user.id, video=parse_video_by_tag_name('about_kk_square'), reply_markup=inlinemenu, caption=html_text)

@dp.callback_query_handler(text='another_about_us', state=[ProjectManage.menu])
async def another_about_us_func(call: CallbackQuery):
    html_text="\n".join(
        [
            '<b>💻 Blockchain разработка</b>',
            'Если вам нужен смарт-контракт или вы хотите создать свою криптовалюту, обращайтесь к нам. Наши специалисты проконсультируют вас, создадут roadmap, помогут составить техническое задание и исполнят его в лучшем качестве.',
            '',
            '<b>🔎 Аудит криптопроектов</b>',
            'Если вы решили принять участие в криптопроекте сторонней компании, но боитесь им довериться — вы можете заказать у нас аудит, в котором мы детально опишем весь код контракта и укажем на допущенные ошибки, бэкдоры и возможные проблемы.',

        ]
    )

    inlinemenu=InlineKeyboardMarkup(row_width=2, inline_keyboard=[
        [InlineKeyboardButton(
            text='↩️ Назад',
            callback_data='userbacktorookie'
            )  
        ],
    ])
    await call.message.delete()
    await bot.send_video(chat_id=call.from_user.id, video=parse_video_by_tag_name('about_kk_square'), reply_markup=inlinemenu, caption=html_text)


@dp.callback_query_handler(text='userbacktorookie', state=[ProjectManage.menu])
async def userbacktorookie_about_us_func(call: CallbackQuery):
    html_text="\n".join(
        [
            '<b>💎 «Крипто Консалтинг» — компания, предоставляющая консалтинговые услуги в сфере  криптовалют в России.</b>',
            '<b>Основной партнер — швейцарский холдинг TRES Group GmbH.</b>',
            ' ',
            '🧠 Опыт работы на рынке СНГ с 2017 года. Полностью отслеживаемая история становления компании и более 1000 отзывов клиентов и инвесторов.',
            ' ',
            '<b>🗣 Мы оказываем многопрофильную помощь по криптовалютам:</b>',
        ]
    )

    inlinemenu=InlineKeyboardMarkup(row_width=2, inline_keyboard=[
        [InlineKeyboardButton(
            text='👩🏻‍💻 О команде',
            callback_data=about_team_call.new(command='showaboutcard', param1=1, param2='none')
            ),
        InlineKeyboardButton(
            text='💎 Консалтинг',
            callback_data='consulting_about_us'
            )
        ],
        [InlineKeyboardButton(
            text='💰 80-101% годовых',
            callback_data='earn_about_us'
            ),
            InlineKeyboardButton(
            text='🦁 Купить биткоин',
            callback_data='SIMBA_about_us'
            ),
        ],
        [InlineKeyboardButton(
            text='📚 Обучение',
            callback_data='learn_about_us'
            ), 
            InlineKeyboardButton(
            text='📈 Аналитика',
            callback_data='analytics_about_us'
            ),      
        ],
        [InlineKeyboardButton(
            text='💼 Инвестпортфель',
            callback_data='investport_about_us'
            ),
            InlineKeyboardButton(
            text='💱 Легальный обмен',
            callback_data='legal_change_about_us'
            ), 
        ],
        [InlineKeyboardButton(
            text='↩️ Назад',
            callback_data='userbacktomenu'
            ),
            InlineKeyboardButton(
            text='🧩 Другие',
            callback_data='another_about_us'
            ),
        ],
    ])

    await call.message.delete()
    await bot.send_video(chat_id=call.from_user.id, video=parse_video_by_tag_name('about_kk_square'), reply_markup=inlinemenu, caption=html_text)



















#---------------------------about-----us-----end-----------------------------


@dp.message_handler(state=ProjectManage.menu, text='🗣 Получить консультацию')
async def initialize_ticket(message: types.Message):
    html_text="\n".join(
        [
            # '<b>Техническая поддержка клиентов</b>',
            # '💎 Крипто Консалтинг',
            # '',
            '❓ Задайте вопрос или подробно опишите возникшую проблему.'
        ]
    )
    backbutton=InlineKeyboardMarkup(row_width=1, inline_keyboard=[
        [InlineKeyboardButton(
            text='↩️ в меню',
            callback_data='userbacktomenu'
        )]
    ])
    await message.answer(text='_',parse_mode='HTML', reply_markup=ReplyKeyboardRemove())
    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id+1)
    await bot.send_message(chat_id=message.from_user.id,text=html_text,parse_mode='HTML', reply_markup=backbutton)
    await ProjectManage.initializingsup.set()

@dp.message_handler(state=ProjectManage.initializingsup)
async def initializing_support (message: types.Message):

    user=user_collection.find_one({"user_id": message.from_user.id})

    ticketid=user['citytag']+'-'+secrets.token_hex(4)+'-'+"{:03d}".format(secrets.randbelow(999))

    extradd={
        "side":"fromuser" ,
        "date": datetime.now(), 
        "text":'<b>❓Вопрос: </b>'+message.text,
        "from_id":message.from_user.id,
        "message_from_id":message.message_id,
        "type":"text",
        "mediaid":"none",
        "isread":True}


    if ticket_collection.count_documents({"ticketid": ticketid}) == 0 and message.from_user.is_bot==False:
        ticket_collection.insert_one(
        {"ticketid": ticketid,
        "date": datetime.now(), #.strftime("%d/%m/%Y %I:%M%p"),
        "isopen": "created",
        "operator": "none",
        "title": message.text,
        "userid":  message.from_user.id,
        "messagedata":"",
        "original_channel":"",
        "original_id":"",
        "original_channel_partner":"none",
        "original_id_partner":"none",
        "citytag":user['citytag'],
        'extrafield':[extradd]})
    
    html_text="\n".join(
        [
            '<b>Момент, на ваш вопрос ответит оператор, ищем свободного 😊</b>',
            'ID вашего обращения '+ticketid
        ]
    )
    
    await message.answer(text=html_text,parse_mode='HTML',reply_markup=userendsupport)
    await ProjectManage.awaitingsup.set()

    sups = staff_collection.find({"staffrole":"support","notified":"none","city_code":user['citytag'], 'isreverse':False})
    gotgot = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
        [InlineKeyboardButton(
            text='Окей',
            callback_data='ivegotit'
        )]
    ]) 
    for x in sups:
        await bot.send_photo(chat_id=x['user_id'],parse_mode='HTML', reply_markup=gotgot, photo=photoparser('new_question'))



@dp.callback_query_handler(text='userbacktomenu', state=[ProjectManage.preparingquest,ProjectManage.initializingsup,ProjectManage.menu])
async def user_come_to_menu(call:types.CallbackQuery):
    thisuser=user_collection.find_one({'user_id':call.from_user.id})
    html_text="\n".join(
        [
            
            system_text_parser('menu_system_text')
            
        ]
    )
    await call.message.delete()
    await ProjectManage.menu.set()


    userpartner=get_partner_obj(thisuser['citytag'])
    caption_attach="\n".join(
        [
            userpartner['datatext']['menu']      
        ]
    )
    await call.message.answer_photo(photo=photoparser('usermainmenu'), caption=html_text ,reply_markup=defaultmenu)
    await bot.send_photo(chat_id=call.from_user.id,photo=userpartner['menu_photo'], caption=caption_attach)

@dp.callback_query_handler(text='ivegotit', state=[SupportManage.menu, SupportManage.onair])
async def igotiwork(call:CallbackQuery):
    staff_collection.find_one_and_update(
        { "user_id":call.from_user.id, "notified":"none"},
        { "$set": { "notified": "notified" } }
    )
    await call.message.delete()
@dp.message_handler(state=ProjectManage.awaitingsup, text='✅ Завершить диалог')
async def end_support(message: types.Message):
    thisicket=ticket_collection.find_one({"userid": message.from_user.id, "$or":[{'isopen':'onair'},{'isopen':'onpause'}, {'isopen':'created'}]})
    if thisicket!=None:
        counttickets=ticket_collection.find().count()+1

        if thisicket['operator']!='none':
            operatornickname=staff_collection.find_one({'user_id':thisicket['operator']})

            operatorcallmeas=operatornickname['callmeas']
            operatornickname=operatornickname['username']
            if operatornickname=='none':
                operatornickname='Без ника'
            else:
                operatornickname="@"+operatornickname
        else:
            operatornickname='Без оператора'
            operatorcallmeas='клиент завершил диалог до подключения'

        clientnickname=user_collection.find_one({'user_id':thisicket['userid']})
        clientcallmeas=clientnickname['callmeas']
        clientnickname=clientnickname['username']

        

        if clientnickname=='none':
            clientnickname='Без ника'
        else:
            clientnickname="@"+clientnickname

        datamessagehere = "\n".join(
            [
                '<b>№'+str(counttickets)+' '+thisicket['citytag']+'</b>',
                '<b>'+thisicket['title']+'</b>',
                '🗣 '+clientnickname+' - '+clientcallmeas,
                '<i>'+thisicket['date'].strftime("%d.%m.%Y / %H:%M")+'</i>',
                '',
                '👨‍💻 '+operatornickname+' - '+operatorcallmeas,
                thisicket['ticketid'],
                '',
                '===',
                "🗣 Закрыт клиентом",
                "<i>"+datetime.now().strftime("%d.%m.%Y / %H:%M")+"</i>"
            ]
        )
        tomad= "\n".join([
            "Диалог закрыт клиентом ",
            "<i>"+datetime.now().strftime("%d.%m.%Y / %H:%M")+"</i>"
        ])
        extradd={
            "side":"fromuser" ,
            "date": datetime.now(),
            "text":tomad,
            "from_id":message.from_user.id,
            "message_from_id":message.message_id,
            "type":"text",
            "mediaid":"none",
            "isread":True}



        photos=await bot.get_user_profile_photos(user_id=thisicket['userid'], limit=1)

        if photos.total_count>0:
            photofinal=photos.photos[0][0].file_id

            mesid=await bot.send_photo(chat_id=channelid, caption=datamessagehere, photo=photofinal)   
            channelid_partner=get_partner_channel(thisicket['citytag'])
            if channelid_partner!='none':
                mesid_partner=await bot.send_photo(chat_id=channelid_partner, caption=datamessagehere, photo=photofinal)  
                ticket_collection.update({"userid": message.from_user.id, "$or":[{'isopen':'onair'},{'isopen':'onpause'}, {'isopen':'created'}]},{"$set":{"isopen":"closedbyclient", "messagedata":datamessagehere, 'original_id':mesid['message_id'], 'original_channel':mesid['sender_chat']['id'], 'original_id_partner':mesid_partner['message_id'], 'original_channel_partner':mesid_partner['sender_chat']['id']}, '$addToSet': { 'extrafield': extradd } })
            ticket_collection.update({"userid": message.from_user.id, "$or":[{'isopen':'onair'},{'isopen':'onpause'}, {'isopen':'created'}]},{"$set":{"isopen":"closedbyclient", "messagedata":datamessagehere, 'original_id':mesid['message_id'], 'original_channel':mesid['sender_chat']['id'], 'original_id_partner':'none', 'original_channel_partner':'none',}, '$addToSet': { 'extrafield': extradd } })

        else:
            mesid=await bot.send_message(chat_id=channelid, text=datamessagehere)   
            channelid_partner=get_partner_channel(thisicket['citytag'])
            if channelid_partner!='none':
                mesid_partner=await bot.send_message(chat_id=channelid_partner, text=datamessagehere)
                ticket_collection.update({"userid": message.from_user.id, "$or":[{'isopen':'onair'},{'isopen':'onpause'}, {'isopen':'created'}]},{"$set":{"isopen":"closedbyclient", "messagedata":datamessagehere, 'original_id':mesid['message_id'], 'original_channel':mesid['sender_chat']['id'], 'original_id_partner':mesid_partner['message_id'], 'original_channel_partner':mesid_partner['sender_chat']['id']}, '$addToSet': { 'extrafield': extradd } })
            ticket_collection.update({"userid": message.from_user.id, "$or":[{'isopen':'onair'},{'isopen':'onpause'}, {'isopen':'created'}]},{"$set":{"isopen":"closedbyclient", "messagedata":datamessagehere, 'original_id':mesid['message_id'], 'original_channel':mesid['sender_chat']['id'], 'original_id_partner':'none', 'original_channel_partner':'none',}, '$addToSet': { 'extrafield': extradd } })


        if thisicket['operator']!='none':
            html_text2="\n".join(
                [
                    '<b>🤖 Бот КриптоКонсалтинг:</b>',
                    '',
                    'Клиент завершил диалог, нажмите на ❌ Завершить'
                ]
            )
            endinline= InlineKeyboardMarkup(row_width=1, inline_keyboard=[
                [InlineKeyboardButton(
                    text='❌ Завершить',
                    callback_data='operator_end_inline_ticket'
                )]
            ]) 
            await bot.send_photo(chat_id=thisicket['operator'],parse_mode='HTML', photo=photoparser('clientfinished'), reply_markup=ReplyKeyboardRemove())
            await bot.send_message(chat_id=thisicket['operator'], text=html_text2,parse_mode='HTML',reply_markup=endinline)
        
         
    thisuser=user_collection.find_one({'user_id':message.from_user.id})
    html_text="\n".join(
        [
            system_text_parser('menu_system_text')
        ]
    )
    await message.answer_photo(photo=photoparser('operatorticketfinished') ,parse_mode='HTML')
    await message.answer_photo(photo=photoparser('usermainmenu'), caption=html_text,parse_mode='HTML',reply_markup=defaultmenu)
    await ProjectManage.menu.set()



@dp.callback_query_handler(state=SupportManage.onair, text='operator_end_inline_ticket')
async def end_supportbysupport(call: CallbackQuery):
    thisicket=ticket_collection.find_one({"operator": call.from_user.id,"isopen": "onair"}) 
    if thisicket!=None:
        ticket_collection.update({"operator": call.from_user.id, "isopen": "onair"},{"$set":{"isopen":"closedbyoperator"}})
        await bot.send_message(chat_id=channelid, text=thisicket['messagedata'])
        html_text2="\n".join(
            [
                ' ',
            ]
        )
        clientgotomenu= InlineKeyboardMarkup(row_width=1, inline_keyboard=[
            [InlineKeyboardButton(
                text='✅ Завершить и выйти в меню',
                callback_data='to_client_menu'
            )]
        ]) 
        await bot.send_photo(chat_id=thisicket['userid'],photo=photoparser('operatorticketfinished') ,caption=html_text2,parse_mode='HTML',reply_markup=ReplyKeyboardRemove())
        await bot.send_message(chat_id=thisicket['userid'],text='Оператор завершил диалог',parse_mode='HTML',reply_markup=clientgotomenu)
    html_text,supportmenubase=build_support_menu(call.from_user.id) 
   
    await bot.send_photo(chat_id=call.from_user.id,photo=photoparser("operatormainmenu"), caption=html_text,parse_mode='HTML',reply_markup=supportmenubase ) 
    await call.message.delete()
    await SupportManage.menu.set()   


@dp.callback_query_handler(state=SupportManage.onair, text='operator_end_inline_ticket_error')
async def end_supportbysupport_error(call: CallbackQuery):
    thisicket=ticket_collection.find_one({"operator": call.from_user.id,"isopen": "onair"}) 
    if thisicket!=None:
        

        counttickets=ticket_collection.find().count()+1

        operatornickname=staff_collection.find_one({'user_id':thisicket['operator']})
        operatorcallmeas=operatornickname['callmeas']
        operatornickname=operatornickname['username']

        clientnickname=user_collection.find_one({'user_id':thisicket['userid']})
        clientcallmeas=clientnickname['callmeas']
        clientnickname=clientnickname['username']

        if operatornickname=='none':
            operatornickname='Без ника'
        else:
            operatornickname="@"+operatornickname

        if clientnickname=='none':
            clientnickname='Без ника'
        else:
            clientnickname="@"+clientnickname
        datamessagehere = "\n".join(
            [

                '<b>№'+str(counttickets)+' '+thisicket['citytag']+'</b>',
                '<b>'+thisicket['title']+'</b>',
                '🗣 '+clientnickname+' - '+clientcallmeas,
                '<i>'+thisicket['date'].strftime("%d.%m.%Y / %H:%M")+'</i>',
                '',
                '👨‍💻 '+operatornickname+' - '+operatorcallmeas,
                thisicket['ticketid'],
                '',
                '===',
                "❌ Диалог закрыт с ошибкой:",
                "клиент забанил бота.",
                "<i>"+datetime.now().strftime("%d.%m.%Y / %H:%M")+"</i>"
                
            ]
        )
        tomad= "\n".join([
            "Диалог закрыт с ошибкой (клиент забанил бота) ",
            "<i>"+datetime.now().strftime("%d.%m.%Y / %H:%M")+"</i>"
        ])
        extradd={
            "side":"error",
            "date": datetime.now(),
            "text":tomad,
            "from_id":call.from_user.id,
            "message_from_id":call.message.message_id,
            "type":"text",
            "mediaid":"none",
            "isread":True}


        photos=await bot.get_user_profile_photos(user_id=thisicket['userid'], limit=1)

        if photos.total_count>0:
            photofinal=photos.photos[0][0].file_id

            mesid=await bot.send_photo(chat_id=channelid, caption=datamessagehere, photo=photofinal)
            channelid_partner=get_partner_channel(thisicket['citytag'])
            if channelid_partner!='none':
                mesid_partner=await bot.send_photo(chat_id=channelid_partner, caption=datamessagehere, photo=photofinal)
                ticket_collection.update({"ticketid": thisicket['ticketid'], "isopen": "onair"},{"$set":{"isopen":"botbanned","messagedata":datamessagehere, 'original_id':mesid['message_id'], 'original_channel':mesid['sender_chat']['id'], 'original_id_partner':mesid_partner['message_id'], 'original_channel_partner':mesid_partner['sender_chat']['id']}, '$addToSet': { 'extrafield': extradd }})
            ticket_collection.update({"ticketid": thisicket['ticketid'], "isopen": "onair"},{"$set":{"isopen":"botbanned","messagedata":datamessagehere, 'original_id':mesid['message_id'], 'original_channel':mesid['sender_chat']['id']}, '$addToSet': { 'extrafield': extradd }})

        else:
            mesid=await bot.send_message(chat_id=channelid, text=datamessagehere)
            channelid_partner=get_partner_channel(thisicket['citytag'])
            if channelid_partner!='none':
                mesid_partner=await bot.send_message(chat_id=channelid_partner, text=datamessagehere)
                ticket_collection.update({"ticketid": thisicket['ticketid'], "isopen": "onair"},{"$set":{"isopen":"botbanned","messagedata":datamessagehere, 'original_id':mesid['message_id'], 'original_channel':mesid['sender_chat']['id'], 'original_id_partner':mesid_partner['message_id'], 'original_channel_partner':mesid_partner['sender_chat']['id']}, '$addToSet': { 'extrafield': extradd }})
            ticket_collection.update({"ticketid": thisicket['ticketid'], "isopen": "onair"},{"$set":{"isopen":"botbanned","messagedata":datamessagehere, 'original_id':mesid['message_id'], 'original_channel':mesid['sender_chat']['id']}, '$addToSet': { 'extrafield': extradd }})

        
       

    html_text,supportmenubase=build_support_menu(call.from_user.id)   
   
    await bot.send_photo(chat_id=call.from_user.id,photo=photoparser("operatormainmenu"), caption=html_text,parse_mode='HTML',reply_markup=supportmenubase ) 
    await call.message.delete()
    await SupportManage.menu.set()  


@dp.message_handler(state=SupportManage.onair, text='❌ Завершить')
async def end_supportbysupport(message: types.Message):
    thisicket=ticket_collection.find_one({"operator": message.from_user.id,"isopen": "onair"}) 
    if thisicket!=None:
        counttickets=ticket_collection.find().count()+1

        operatornickname=staff_collection.find_one({'user_id':thisicket['operator']})
        operatorcallmeas=operatornickname['callmeas']
        operatornickname=operatornickname['username']

        clientnickname=user_collection.find_one({'user_id':thisicket['userid']})
        clientcallmeas=clientnickname['callmeas']
        clientnickname=clientnickname['username']

        if operatornickname=='none':
            operatornickname='Без ника'
        else:
            operatornickname="@"+operatornickname

        if clientnickname=='none':
            clientnickname='Без ника'
        else:
            clientnickname="@"+clientnickname

        datamessagehere = "\n".join(
            [
                '<b>№'+str(counttickets)+' '+thisicket['citytag']+'</b>',
                '<b>'+thisicket['title']+'</b>',
                '🗣 '+clientnickname+' - '+clientcallmeas,
                '<i>'+thisicket['date'].strftime("%d.%m.%Y / %H:%M")+'</i>',
                '',
                '👨‍💻 '+operatornickname+' - '+operatorcallmeas,
                thisicket['ticketid'],
                '',
                '===',
                "👨‍💻 Закрыт оператором",
                "<i>"+datetime.now().strftime("%d.%m.%Y / %H:%M")+"</i>"

            ]
        )
        
        
        html_text2="\n".join(
            [
                ' ',
            ]
        )
        clientgotomenu= InlineKeyboardMarkup(row_width=1, inline_keyboard=[
            [InlineKeyboardButton(
                text='✅ Завершить и выйти в меню',
                callback_data='to_client_menu'
            )]
        ]) 
        

        await bot.send_photo(chat_id=thisicket['userid'],photo=photoparser('operatorticketfinished') ,caption=html_text2,parse_mode='HTML',reply_markup=ReplyKeyboardRemove())
        await bot.send_message(chat_id=thisicket['userid'],text='Оператор завершил диалог',parse_mode='HTML',reply_markup=clientgotomenu)      

        tomad= "\n".join([
            "Диалог закрыт оператором ",
            "<i>"+datetime.now().strftime("%d.%m.%Y / %H:%M")+"</i>"
        ])
        extradd={
            "side":"fromoperator" ,
            "date": datetime.now(),
            "text":tomad,
            "from_id":message.from_user.id,
            "message_from_id":message.message_id,
            "type":"text",
            "mediaid":"none",
            "isread":True}


        photos=await bot.get_user_profile_photos(user_id=thisicket['userid'], limit=1)

        if photos.total_count>0:
            photofinal=photos.photos[0][0].file_id

            mesid=await bot.send_photo(chat_id=channelid, caption=datamessagehere, photo=photofinal)
            channelid_partner=get_partner_channel(thisicket['citytag'])
            if channelid_partner!='none':
                mesid_partner=await bot.send_photo(chat_id=channelid_partner, caption=datamessagehere, photo=photofinal)
                ticket_collection.update({"ticketid":thisicket['ticketid']},{"$set":{"isopen":"closedbyoperator","messagedata":datamessagehere,'original_id':mesid['message_id'], 'original_channel':mesid['sender_chat']['id'],'original_id_partner':mesid_partner['message_id'], 'original_channel_partner':mesid_partner['sender_chat']['id']},'$addToSet': { 'extrafield': extradd }})
            ticket_collection.update({"ticketid":thisicket['ticketid']},{"$set":{"isopen":"closedbyoperator","messagedata":datamessagehere,'original_id':mesid['message_id'], 'original_channel':mesid['sender_chat']['id']},'$addToSet': { 'extrafield': extradd }})
            

        else:
            mesid=await bot.send_message(chat_id=channelid, text=datamessagehere)
            channelid_partner=get_partner_channel(thisicket['citytag'])
            if channelid_partner!='none':
                mesid_partner=await bot.send_message(chat_id=channelid_partner, text=datamessagehere)
                ticket_collection.update({"ticketid":thisicket['ticketid']},{"$set":{"isopen":"closedbyoperator","messagedata":datamessagehere,'original_id':mesid['message_id'], 'original_channel':mesid['sender_chat']['id'],'original_id_partner':mesid_partner['message_id'], 'original_channel_partner':mesid_partner['sender_chat']['id']},'$addToSet': { 'extrafield': extradd }})
            ticket_collection.update({"ticketid":thisicket['ticketid']},{"$set":{"isopen":"closedbyoperator","messagedata":datamessagehere,'original_id':mesid['message_id'], 'original_channel':mesid['sender_chat']['id']},'$addToSet': { 'extrafield': extradd }})
            
    html_text,supportmenubase=build_support_menu(message.from_user.id)    
    await bot.send_message(chat_id=message.from_user.id,text='Диалог завершен',parse_mode='HTML',reply_markup=ReplyKeyboardRemove())
    await bot.send_photo(chat_id=message.from_user.id,photo=photoparser("operatormainmenu"), caption=html_text,parse_mode='HTML',reply_markup=supportmenubase ) 
    
    await SupportManage.menu.set()   

@dp.callback_query_handler(text='to_client_menu', state=ProjectManage.awaitingsup)
async def clientgogotomenucallback(call: CallbackQuery):
    thisuser=user_collection.find_one({'user_id':call.from_user.id})
    html_text="\n".join(
        [
            system_text_parser('menu_system_text')
        ]
    )
    await call.message.delete()
    await ProjectManage.menu.set()
    userpartner=get_partner_obj(thisuser['citytag'])
    caption_attach="\n".join(
        [
            userpartner['datatext']['menu']      
        ]
    )
    await call.message.answer_photo(photo=photoparser('usermainmenu'), caption=html_text ,reply_markup=defaultmenu)
    await bot.send_photo(chat_id=call.from_user.id,photo=userpartner['menu_photo'], caption=caption_attach)

@dp.callback_query_handler(text='tonewtickets', state=SupportManage.menu)
async def tonewticketsfunc(call:types.CallbackQuery):
    operator = staff_collection.find_one({"user_id":call.from_user.id})
    newticket=ticket_collection.find({"isopen":"created", "operator":"none", "citytag": {"$in": operator['city_code'][1:]}})
    opentickets = InlineKeyboardMarkup()
    if newticket.count()>0:
        for x in newticket:
            thisuser = user_collection.find_one({"user_id":x['userid']})
            thisbutton = InlineKeyboardButton(text=str(thisuser['callmeas'])+' ❓ '+x['title'], callback_data=ticket_callback.new("openticket",ticketid=x['ticketid'], operatorid=call.from_user.id)  )
            opentickets.add(thisbutton)
    opentickets.add(InlineKeyboardButton(text="⬅ Вернуться к обращениям",callback_data='to_tickets'))

    # await call.message.edit_text(text="<b>📛 Новые: 🗣"+str(newticket.count())+"</b>",reply_markup=opentickets)
    await call.message.edit_media(media=InputMediaPhoto(media=photoparser("waiting"), caption="<b>🔥 Новые: 🗣"+str(newticket.count())+"</b>"), reply_markup=opentickets) 

@dp.callback_query_handler(text='tourpaused', state=SupportManage.menu)
async def tourpausedticketsfunc(call:types.CallbackQuery):
    await call.answer(cache_time=0)
    operator = staff_collection.find_one({"user_id":call.from_user.id})
    pausedticket=ticket_collection.find({"isopen":"onpause", "operator":call.from_user.id,"citytag": {"$in": operator['city_code'][1:]}})
    opentickets = InlineKeyboardMarkup()
    if pausedticket.count()>0:
        for x in pausedticket:
            thisuser = user_collection.find_one({"user_id":x['userid']})
            thisbutton = InlineKeyboardButton(text=str(thisuser['callmeas'])+' ❓ '+x['title'], callback_data=ticket_callback.new("openticket",ticketid=x['ticketid'], operatorid=call.from_user.id)  )
            opentickets.add(thisbutton)
    opentickets.add(InlineKeyboardButton(text="⬅ Вернуться к обращениям",callback_data='to_tickets'))

    # await call.message.edit_text(text="<b>На паузе: 🗣"+str(pausedticket.count())+"</b>",reply_markup=opentickets)
    await call.message.edit_media(media=InputMediaPhoto(media=photoparser("waiting"), caption="<b>💭 Открытые: 🗣"+str(pausedticket.count())+"</b>"), reply_markup=opentickets) 


@dp.callback_query_handler(text='to_tickets', state=SupportManage.menu)
async def to_tickets_func(call:types.CallbackQuery):
    await call.answer(cache_time=0)
    inlinekeyb=InlineKeyboardMarkup(row_width=1)
    operator = staff_collection.find_one({"user_id":call.from_user.id})
    created=ticket_collection.count_documents({'isopen':'created', 'operator':'none', "citytag": {"$in": operator['city_code'][1:]}})
    paused=ticket_collection.count_documents({'isopen':'onpause', 'operator':call.from_user.id, "citytag": {"$in":operator['city_code'][1:]}}) 
    updatebutton=InlineKeyboardButton(
        text='🔄 Обновить',
        callback_data="to_tickets"
    )
    inlinekeyb.add(updatebutton)
    if created>0:
        createdbutton=InlineKeyboardButton(
            text='🔥 Новые',
            callback_data="tonewtickets"
        )
        inlinekeyb.add(createdbutton)
    if paused>0:
        pausedbutton=InlineKeyboardButton(
            text='💭 Открытые',
            callback_data="tourpaused"
        )
        inlinekeyb.add(pausedbutton)
    html_text="\n".join(
        [
            '<b>🔥 Новые: 🗣'+ str(created)+'</b>',
            '<b>💭 Открытые: 🗣'+str(paused)+'</b>'

        ]
    )
    
    inlinekeyb.add(InlineKeyboardButton(text="↩️ в меню",callback_data='supportbacktomenu'))
    if created == 0 and paused == 0:
       
        await call.message.edit_media(media=InputMediaPhoto(media=photoparser("silent"), caption=html_text), reply_markup=inlinekeyb) 
    else:
  
        await call.message.edit_media(media=InputMediaPhoto(media=photoparser("waiting"), caption=html_text), reply_markup=inlinekeyb) 
    
         

@dp.callback_query_handler(text='supportbacktomenu', state=SupportManage.menu)
async def supportbacktomenufunc(call:types.CallbackQuery):
    html_text,supportmenubase=build_support_menu(call.from_user.id)
    await call.message.edit_media(media=InputMediaPhoto(media=photoparser("operatormainmenu"), caption=html_text), reply_markup=supportmenubase) 

############################################admin_menu###########################################

@dp.callback_query_handler(text='to_admin_menu', state=SupportManage.menu)
async def adminmenustart(call: types.CallbackQuery):
    html_text="\n".join(
        [
            '<b>🔐 Доступ:</b>',
            'все администраторы.',
            '<b>⚜️ Возможности:</b>',
            '<i>· добавить/удалить оператора</i>',
            # '<i>· добавить/удалить город</i>',
            '<i>· добавить материалы </i>'
        ]
    )
    supportmenubase = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
        [InlineKeyboardButton(
            text='🗣 Операторы',
            callback_data='edit_support'
        )],
        # [InlineKeyboardButton(
        #     text='🌆 Города',
        #     callback_data=show_cities_pages.new("showcities",page=1)
        # )],
        [InlineKeyboardButton(
            text='📚 Новичку',
            callback_data=knowledge_list_call.new("show_faq",param1="main", param2="none")
        )],
        [InlineKeyboardButton(
            text='↩️ в меню',
            callback_data='supportbacktomenu'
        )],
    ])

    # await call.message.edit_text(text=html_text, reply_markup=supportmenubase)
    await call.message.edit_media(media=InputMediaPhoto(media=photoparser("adminpanel"), caption=html_text), reply_markup=supportmenubase) 




################################################Admin menu - support manage#########################################################
@dp.callback_query_handler(text='edit_support', state=SupportManage.menu)
async def admin_menu_edit_support(call: types.CallbackQuery):
    html_text="\n".join(
        [
            ' '
        ]
    )
    supportmenubase = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
        [InlineKeyboardButton(
            text='🗣 Все операторы',
            callback_data=show_support_pages.new("showsuppages",page=1)
        )],
        [InlineKeyboardButton(
            text='➕ Добавить',
            switch_inline_query='add_operator'
        )],
        [InlineKeyboardButton(
            text='◀️ назад',
            callback_data='to_admin_menu'
        )],
    ])
    # await call.message.edit_text(text=html_text, reply_markup=supportmenubase)
    await call.message.edit_media(media=InputMediaPhoto(photoparser('operatormanage'), caption=html_text), reply_markup=supportmenubase)







@dp.callback_query_handler(show_support_pages.filter(command='showsuppages'), state=SupportManage.menu)
async def system_operator_check_list_func(call: types.CallbackQuery, callback_data:dict):
    page = callback_data.get("page")
    page = int(page)
    prevpage = page - 1
    nextpage = page + 1

    inlinekeys = InlineKeyboardMarkup(row_width=2)
    x=staff_collection.find({"staffrole":"support"}).skip((page-1)*5).limit(5)

    for i in x:
        inlinekeys.add(InlineKeyboardButton(text=i["callmeas"]+' '+i["first_name"]+' ('+support_role_check(i['user_id'])+')', callback_data=show_support_pages.new("openoperator",page=i['user_id'])))
    
    
    if prevpage < 1:
        prevtoadd=InlineKeyboardButton(
            text='◀️',
            callback_data=show_support_pages.new("showsuppages",page=1)
        )
    else:
        prevtoadd=InlineKeyboardButton(
            text='◀️',
            callback_data=show_support_pages.new("showsuppages",page=prevpage)
        )

    if  math.ceil(x.count()/5)==page:
        nexttoadd=InlineKeyboardButton(
            text='▶️',
            callback_data=show_support_pages.new("showsuppages",page=page)
        )      
    else:
        nexttoadd=InlineKeyboardButton(
            text='▶️',
            callback_data=show_support_pages.new("showsuppages",page=nextpage)
        )  
    inlinekeys.add(prevtoadd,nexttoadd)
    inlinekeys.add(InlineKeyboardButton(text='Назад в админ-меню',callback_data='to_admin_menu'))
    # await call.message.edit_text(text='Вы на странице '+'<b>'+str(page)+'</b>', reply_markup=inlinekeys)   
    await call.message.edit_media(media=InputMediaPhoto(photoparser('operatorlist'), caption='Вы на странице '+'<b>'+str(page)+'</b>'), reply_markup=inlinekeys)
 


@dp.callback_query_handler(show_support_pages.filter(command='openoperator'), state=SupportManage.menu)
async def system_operator_open_func(call: types.CallbackQuery, callback_data:dict):
    x = staff_collection.find_one({"user_id" : int(callback_data.get("page"))})
    html_text="\n".join(
        [
            '🗣 Имя оператора: <a href="tg://user?id='+str(x['user_id'])+'">'+x["first_name"]+'</a>',
            '✏️ Имя для клиентов: '+x['callmeas'],
            '🔑 Права: '+str(support_role_check(x['user_id'])),
            '🌆 Партнеры: '+str(x["city_code"][1:])
        ]
    )
    operatorbuttons = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
        [InlineKeyboardButton(
            text='🗣 Изменить имя',
            callback_data=show_support_pages.new('operator_change_name',page=x["user_id"])
        )],
        [InlineKeyboardButton(
            text='🌆 Тэги городов',
            callback_data=show_support_pages.new("changecityoperator",page=x["user_id"])
        )],
        [InlineKeyboardButton(
            text='🔑 Права: '+str(support_role_check(x['user_id'])),
            callback_data=show_support_pages.new("changepassoperator",page=x["user_id"])
        )],
        [InlineKeyboardButton(
            text='🖼️ Изменить фотографию',
            callback_data=show_support_pages.new("ch_ph_oper",page=x["user_id"])
        )],
        [InlineKeyboardButton(
            text='❌ Удалить',
            callback_data=show_support_pages.new("deleteoperatorinit",page=x["user_id"])
        )],
        [InlineKeyboardButton(
            text='◀️ к списку операторов',
            callback_data=show_support_pages.new("showsuppages",page=1)
        )]
    ])
    phav=x['photo_avatar']
    if phav=='none':
        phav=photoparser('nameroletags')
    await call.message.edit_media(media=InputMediaPhoto(phav, caption=html_text, parse_mode='HTML'), reply_markup=operatorbuttons)


@dp.callback_query_handler(show_support_pages.filter(command='deleteoperatorinit'), state=SupportManage.menu)
async def delete_operator_init(call: types.CallbackQuery, callback_data:dict):
    await call.answer(cache_time=1)
    x = staff_collection.find_one({"user_id" : int(callback_data.get("page"))}) 
    html_text="\n".join(
        [
            ' '
        ]
    )
    operatorbuttons = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
        [InlineKeyboardButton(
            text='❌ Да, удалить',
            callback_data=show_support_pages.new('deleteoperatoryes',page=x["user_id"])
        )],
        [InlineKeyboardButton(
            text='↩️ Нет, оставить',
            callback_data=show_support_pages.new("openoperator",page=x["user_id"])
        )]
    ])

    await call.message.edit_media(media=InputMediaPhoto(photoparser('deleteoperatorask'), caption=html_text), reply_markup=operatorbuttons)


@dp.callback_query_handler(show_support_pages.filter(command='deleteoperatoryes'), state=SupportManage.menu)
async def delete_operator_done(call: types.CallbackQuery, callback_data:dict):
    await call.answer(cache_time=1)
    staff_collection.remove({"user_id" : int(callback_data.get("page"))}) 

    states_collection.find_one_and_update(
        { "user":int(callback_data.get("page")) },
        {"$set":{ "state":'ProjectManage:menu' }}
    )

    html_text="\n".join(
        [
            ' '
        ]
    )
    operatorbuttons = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
        [InlineKeyboardButton(
            text='↩️ назад к списку операторов',
            callback_data=show_support_pages.new('showsuppages',page=1)
        )],
    ])

    await call.message.edit_media(media=InputMediaPhoto(photoparser('deleteoperatorask'), caption=html_text), reply_markup=operatorbuttons)


@dp.callback_query_handler(show_support_pages.filter(command='changepassoperator'), state=SupportManage.menu)
async def system_change_role(call: types.CallbackQuery, callback_data:dict):
    await call.answer(cache_time=1)
    x = staff_collection.find_one({"user_id" : int(callback_data.get("page"))})

    if x["role"] == "1":
        staff_collection.find_and_modify( 
            query={"user_id":x["user_id"]}, 
            update={ "$set": { 'role': "2"} }
            )
    elif x["role"] == "2":
        staff_collection.find_and_modify( 
            query={"user_id":x["user_id"]}, 
            update={ "$set": { 'role': "1"}}
            )        
    x = staff_collection.find_one({"user_id" : int(callback_data.get("page"))})


    
    html_text="\n".join(
        [
            '🗣 Имя оператора: <a href="tg://user?id='+str(x['user_id'])+'">'+x["first_name"]+'</a>',
            '✏️ Имя для клиентов: '+x['callmeas'],
            '🔑 Права: '+str(support_role_check(x['user_id'])),
            '🌆 Партнеры: '+str(x["city_code"][1:])
        ]
    )
    operatorbuttons = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
        [InlineKeyboardButton(
            text='🗣 Изменить имя',
            callback_data=show_support_pages.new('operator_change_name',page=x["user_id"])
        )],
        [InlineKeyboardButton(
            text='🌆 Тэги городов',
            callback_data=show_support_pages.new("changecityoperator",page=x["user_id"])
        )],
        [InlineKeyboardButton(
            text='🔑 Права: '+str(support_role_check(x['user_id'])),
            callback_data=show_support_pages.new("changepassoperator",page=x["user_id"])
        )],
        [InlineKeyboardButton(
            text='🖼️ Изменить фотографию',
            callback_data=show_support_pages.new("ch_ph_oper",page=x["user_id"])
        )],
        [InlineKeyboardButton(
            text='❌ Удалить',
            callback_data=show_support_pages.new("deleteoperatorinit",page=x["user_id"])
        )],
        [InlineKeyboardButton(
            text='◀️ к списку операторов',
            callback_data=show_support_pages.new("showsuppages",page=1)
        )]
    ])
    phav=x['photo_avatar']
    if phav=='none':
        phav=photoparser('nameroletags')
    await call.message.edit_media(media=InputMediaPhoto(phav, caption=html_text, parse_mode='HTML'), reply_markup=operatorbuttons)



#======Operator_change_photo

@dp.callback_query_handler(show_support_pages.filter(command='ch_ph_oper'), state=SupportManage.menu)
async def system_operator_photochange_func(call: types.CallbackQuery, callback_data:dict, state: FSMContext): 
    await call.answer(cache_time=1)
    html_text="\n".join(
        [
            'Пришлите новое фото оператора.'
        ]
    )
    operatorbuttons = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
        [InlineKeyboardButton(
            text='◀️ Отменить и вернуться',
            callback_data=show_support_pages.new('op_ch_ph_canc',page=int(callback_data.get("page")))
        )]
    ])

    await SupportManage.changeoperatorphoto.set()
    await state.update_data(operph=int(callback_data.get("page")))
    await call.message.edit_media(media=InputMediaPhoto(photoparser('operatormainmenu'), caption=html_text, parse_mode='HTML'), reply_markup=operatorbuttons)


@dp.callback_query_handler(show_support_pages.filter(command='op_ch_ph_canc'), state=SupportManage.changeoperatorphoto)
async def system_operator_photochange_canc_func(call: types.CallbackQuery, callback_data:dict, state: FSMContext): 
    x = staff_collection.find_one({"user_id" : int(callback_data.get("page"))})


    
    html_text="\n".join(
        [
            '🗣 Имя оператора: <a href="tg://user?id='+str(x['user_id'])+'">'+x["first_name"]+'</a>',
            '✏️ Имя для клиентов: '+x['callmeas'],
            '🔑 Права: '+str(support_role_check(x['user_id'])),
            '🌆 Партнеры: '+str(x["city_code"][1:])
        ]
    )
    operatorbuttons = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
        [InlineKeyboardButton(
            text='🗣 Изменить имя',
            callback_data=show_support_pages.new('operator_change_name',page=x["user_id"])
        )],
        [InlineKeyboardButton(
            text='🌆 Тэги городов',
            callback_data=show_support_pages.new("changecityoperator",page=x["user_id"])
        )],
        [InlineKeyboardButton(
            text='🔑 Права: '+str(support_role_check(x['user_id'])),
            callback_data=show_support_pages.new("changepassoperator",page=x["user_id"])
        )],
        [InlineKeyboardButton(
            text='🖼️ Изменить фотографию',
            callback_data=show_support_pages.new("ch_ph_oper",page=x["user_id"])
        )],
        [InlineKeyboardButton(
            text='❌ Удалить',
            callback_data=show_support_pages.new("deleteoperatorinit",page=x["user_id"])
        )],
        [InlineKeyboardButton(
            text='◀️ к списку операторов',
            callback_data=show_support_pages.new("showsuppages",page=1)
        )]
    ])
    phav=x['photo_avatar']
    if phav=='none':
        phav=photoparser('nameroletags')
    await SupportManage.menu.set()
    await call.message.edit_media(media=InputMediaPhoto(phav, caption=html_text, parse_mode='HTML'), reply_markup=operatorbuttons)


@dp.message_handler(content_types=['photo'],state=SupportManage.changeoperatorphoto)
async def system_operator_photoget_func(message: types.Message, state: FSMContext):
    data = await state.get_data()
    operatorid = data.get("operph")
    thisphoto=message.photo[0].file_id

    staff_collection.find_one_and_update(
        { "user_id":operatorid },
        {"$set":{ "photo_avatar":thisphoto }}
    )

    x = staff_collection.find_one({"user_id" : operatorid})


    
    html_text="\n".join(
        [
            '🗣 Имя оператора: <a href="tg://user?id='+str(x['user_id'])+'">'+x["first_name"]+'</a>',
            '✏️ Имя для клиентов: '+x['callmeas'],
            '🔑 Права: '+str(support_role_check(x['user_id'])),
            '🌆 Партнеры: '+str(x["city_code"][1:])
        ]
    )
    operatorbuttons = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
        [InlineKeyboardButton(
            text='🗣 Изменить имя',
            callback_data=show_support_pages.new('operator_change_name',page=x["user_id"])
        )],
        [InlineKeyboardButton(
            text='🌆 Тэги городов',
            callback_data=show_support_pages.new("changecityoperator",page=x["user_id"])
        )],
        [InlineKeyboardButton(
            text='🔑 Права: '+str(support_role_check(x['user_id'])),
            callback_data=show_support_pages.new("changepassoperator",page=x["user_id"])
        )],
        [InlineKeyboardButton(
            text='🖼️ Изменить фотографию',
            callback_data=show_support_pages.new("ch_ph_oper",page=x["user_id"])
        )],
        [InlineKeyboardButton(
            text='❌ Удалить',
            callback_data=show_support_pages.new("deleteoperatorinit",page=x["user_id"])
        )],
        [InlineKeyboardButton(
            text='◀️ к списку операторов',
            callback_data=show_support_pages.new("showsuppages",page=1)
        )]
    ])
    phav=x['photo_avatar']
    if phav=='none':
        phav=photoparser('nameroletags')
    await SupportManage.menu.set()
    # await message.answer_photo(photo=InputMediaPhoto(phav, caption=html_text, parse_mode='HTML'), reply_markup=operatorbuttons)
    await message.answer_photo(photo=phav, caption=html_text, reply_markup=operatorbuttons, parse_mode='HTML')







#======Operator_change_photo_end







#=======Operator_change_cities_array

@dp.callback_query_handler(show_support_pages.filter(command='changecityoperator'), state=SupportManage.menu)
async def system_operator_city_change_func(call: types.CallbackQuery, callback_data:dict):
    x = staff_collection.find_one({"user_id" : int(callback_data.get("page"))})
    inlinekeys = InlineKeyboardMarkup(row_width=2)
    cities = x["city_code"]
    
    cities_in_sys = partner_collection.find({})
    for i in cities_in_sys:
        galka=""
        deleteoradd="1"
        if i['system_tag'] in cities:
            galka="✔️"
            deleteoradd="0"
        inlinekeys.add(InlineKeyboardButton(text=galka+i["city_name"]+' : '+i["system_tag"], callback_data=edit_something_admin.new('ecu',i["system_tag"],deleteoradd,int(callback_data.get("page")) )))
    inlinekeys.add(InlineKeyboardButton(text='Назад к оператору',callback_data=show_support_pages.new("openoperator",page=int(callback_data.get("page")))))
    await call.message.edit_media(media=InputMediaPhoto(photoparser('operatorcitiesaccess'), caption=' '), reply_markup=inlinekeys)

@dp.callback_query_handler(edit_something_admin.filter(command='ecu'), state=SupportManage.menu)
async def system_operator_city_change_and_update_func(call: types.CallbackQuery, callback_data:dict):
    await call.answer(cache_time=1)
    if callback_data.get("deleteoradd") == "1":
        
        staff_collection.find_and_modify( 
            query={"user_id":int(callback_data.get("userid"))}, 
            update={ "$push": { 'city_code': callback_data.get("something") }}
            )
    elif callback_data.get("deleteoradd") == "0":
       
        staff_collection.find_and_modify( 
            query={"user_id":int(callback_data.get("userid"))}, 
            update={ "$pull": { 'city_code': callback_data.get("something") }}
            )
    x = staff_collection.find_one({"user_id" : int(callback_data.get("userid"))})
    inlinekeys = InlineKeyboardMarkup(row_width=2)
    cities = x["city_code"]
    
    cities_in_sys = partner_collection.find({})

    for i in cities_in_sys:
        galka=""
        deleteoradd="1"
        if i['system_tag'] in cities:
            galka="✔️"
            deleteoradd="0"
        inlinekeys.add(InlineKeyboardButton(text=galka+i["city_name"]+' : '+i["system_tag"], callback_data=edit_something_admin.new('ecu',i["system_tag"],deleteoradd,int(callback_data.get("userid")) )))
    inlinekeys.add(InlineKeyboardButton(text='Назад к оператору',callback_data=show_support_pages.new("openoperator",page=int(callback_data.get("userid")))))

    await call.message.edit_media(media=InputMediaPhoto(photoparser('operatorcitiesaccess'), caption=' '), reply_markup=inlinekeys)

#=======Operator_change_cities_array_end



@dp.callback_query_handler(show_support_pages.filter(command='operator_change_name'), state=SupportManage.menu)
async def operator_change_name_support(call: types.CallbackQuery,state: FSMContext, callback_data:dict):
    html_text="\n".join(
        [
            ' '
        ]
    )
    await SupportManage.changeoperatorname.set()
    await state.update_data(operatorid=int(callback_data.get("page")))
    # await call.message.edit_text(text=html_text, parse_mode='HTML', reply_markup=None) 
    await call.message.edit_media(media=InputMediaPhoto(photoparser('operatorchangename'), caption=html_text), reply_markup=None)

@dp.message_handler(state=SupportManage.changeoperatorname)
async def operator_write_new_name_support(message: types.Message, state: FSMContext):
    data = await state.get_data()
    operid = data.get("operatorid")
    staff_collection.find_and_modify( 
            query={"user_id":operid}, 
            update={ "$set": { 'callmeas':message.text }}
            )
    await state.reset_state()
    await SupportManage.menu.set()
    inlinekeys = InlineKeyboardMarkup(row_width=2)
    inlinekeys.add(InlineKeyboardButton(text='Назад к оператору',callback_data=show_support_pages.new("openoperator",page=operid)))
    # await message.answer(text="Новое имя '"+message.text+"' успешно сохранено", parse_mode='HTML', reply_markup=inlinekeys)
    await message.answer_photo(photo=photoparser("operatornameupdated"), caption=" ", reply_markup=inlinekeys)
  
# ----------------здесь инлайн функции-----------------------
@dp.inline_handler(text="add_operator", state=SupportManage.menu)
async def initialize_adding_operator_tosys(query: types.InlineQuery):
    if isadmin(query.from_user.id)==False:
        await query.answer(
            results=[],
            switch_pm_text='Вы не являетесь админом бота',
            cache_time=0
           
        )
        return  
    supportmenubase = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
        [InlineKeyboardButton(
            text='Я в деле!',
            callback_data=add_operator_callback.new("addoperatorfactory",operator_role='1')
        )]
    ])
    await query.answer(
        results=[
            types.InlineQueryResultArticle(
                id="1",
                title='Сделать этот контакт оператором',
                input_message_content=types.InputMessageContent(message_text="Вам предлагают стать оператором в компании КриптоКонсалтинг, пожалуйста, подтвердите свое согласие."),
                reply_markup=supportmenubase
            )
        ],
        cache_time=0
    )  

@dp.inline_handler(text="invite", state='*')
async def generate_agent_button(query: types.InlineQuery):


    this_agent=staff_collection.find_one({'user_id':query.from_user.id})
    this_agent_partners=links_collection.find({'citycode': {'$in': this_agent['city_code'][1:]}, 'additional':'default'})
    results_arr=[]
    i=1
    if this_agent!=None and this_agent_partners!=None:
        for x in this_agent_partners: 
            supportmenubase = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
                [InlineKeyboardButton(
                    text='Перейти в бота',
                    url='https://t.me/cryptoconsbot?start='+x['uniquename']
                )]
            ])
            toadd=types.InlineQueryResultArticle(
                    id=i,
                    title=x['uniquename'],
                    description=x['citycode']+'-'+x['city'],
                    input_message_content=types.InputMessageContent(message_text="<b>💎 ООО «Крипто Консалтинг»</b> — \nпроводник в мир криптовалют", parse_mode='HTML'),
                    reply_markup=supportmenubase,
                    
                )
            results_arr.append(toadd)
            i=i+1


        await query.answer(
            results=results_arr,
            cache_time=0
        )





# ----------------здесь инлайн функции конец-----------------------
@dp.callback_query_handler(add_operator_callback.filter(command='addoperatorfactory'), state=[ProjectManage.menu, None])
async def providing_adding_operator_tosys(call:types.CallbackQuery, callback_data:dict):
    
    getoperator=staff_collection.find_one({"user_id":call.from_user.id})
    if getoperator==None:
        staff_collection.insert_one(
        {"user_id": call.from_user.id,
        "first_name":xstr(call.from_user.first_name),
        "last_name":xstr(call.from_user.last_name),
        "username": xstr(call.from_user.username),
        "staffrole": "support",
        "notified": "none",
        "city_code":['none'],
        "callmeas":'none',
        "role":callback_data.get("operator_role"),
        'photo_avatar':'none',
        'isreverse':False})
        html_text="\n".join(
            [
                'Вы успешно зарегистрированы в системе как оператор!',
                ' ',
                'Пожалуйста, свяжитесь с пригласившим вас администратором для заверешения настройки вашего профиля'
            ]
        ) 
        await bot.edit_message_text(inline_message_id=call.inline_message_id,text=html_text, parse_mode='HTML', reply_markup=None)
    else:
        html_text="\n".join(
            [
                'Вы уже являетесь оператором'
            ]
        ) 
        await bot.edit_message_text(inline_message_id=call.inline_message_id,text=html_text, parse_mode='HTML', reply_markup=None)
    




######################################################talksupport##########################################
@dp.callback_query_handler(ticket_callback.filter(command='openticket'), state=SupportManage.menu)
async def showcard(call:types.CallbackQuery, callback_data:dict):
    await call.answer(cache_time=1)
    thisicket=ticket_collection.find_one({"ticketid":callback_data.get("ticketid")})
    thisuser = user_collection.find_one({"user_id":thisicket['userid']})
    x=''
    if thisuser['username']!='none':
        x=' (@'+thisuser['username']+')'
    html_text="\n".join(
        [
            '<b>ID тикета: '+thisicket["ticketid"]+'</b> ',
            '<b>'+thisuser['callmeas']+x+':</b> '+thisicket['title'],
            '<b>Город: </b>'+thisuser['city']
        ]
    )        
    inlinekeyb=InlineKeyboardMarkup(row_width=1, inline_keyboard=[
        [InlineKeyboardButton(
            text='Перейти к диалогу 💬',
            callback_data=ticket_callback.new("jumptoclient",ticketid=thisicket['ticketid'], operatorid=callback_data.get("operatorid"))
        )],
        [
        InlineKeyboardButton(
            text='↩️ назад',
            callback_data='tonewtickets'
        ),]
    ])
    photos=await bot.get_user_profile_photos(user_id=thisicket['userid'], limit=1)

    if photos.total_count>0:
        photofinal=photos.photos[0][0].file_id
    else:
        photofinal=thisuser['user_photo']
    
    await call.message.edit_media(media=InputMediaPhoto(media=photofinal, caption=html_text), reply_markup=inlinekeyb)


@dp.callback_query_handler(ticket_callback.filter(command='jumptoclient'), state=SupportManage.menu)
async def jumptothis(call:types.CallbackQuery, callback_data:dict):
    thisicket=ticket_collection.find_one({"ticketid":callback_data.get("ticketid")})
    thisoperator = staff_collection.find_one({"user_id":call.from_user.id})
    thisuser = user_collection.find_one({"user_id":thisicket['userid']})
    html_text="\n".join(
        [
            'Вы начали диалог с клиентом'
            ' ',
            '<b>🗣️ '+thisuser['callmeas']+'</b> ',
            '<b>Обращение: </b>'+thisicket['title'],
        ]
    )

    tomsas="\n".join(
            [
                "Оператор подключился <i>("+datetime.now().strftime("%d.%m.%Y / %H:%M")+")</i>"
            ]
        )
    extradd={
        "side":"fromoperator" ,
        "date": datetime.now(), 
        "text":tomsas,
        "from_id":call.from_user.id,
        "message_from_id":call.message.message_id,
        "type":"text",
        "mediaid":"none",
        "isread":True}


    if thisicket["isopen"]=="created":
        if thisoperator['photo_avatar']!='none':
            try:
                
                await bot.send_photo(chat_id=thisicket['userid'],caption='👨‍💻 <b>'+thisoperator['callmeas']+'</b> подключился к диалогу',parse_mode='HTML', photo=thisoperator['photo_avatar'])
            except:
                error_ticket= await check_error_ticket(thisicket['ticketid'])
                await call.answer(text=error_ticket, cache_time=0, show_alert=True)
                await call.message.delete()
                opentickets = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
                    [
                    InlineKeyboardButton(text="⬅ Вернуться к обращениям",callback_data='to_tickets')]
                ])
                
                #проверка на билет
                await bot.send_photo(chat_id=call.from_user.id,parse_mode='HTML', photo=photoparser('clientfinished'), reply_markup=opentickets)
                raise CancelHandler()
        else:    
            try:
               
                await bot.send_message(chat_id=thisicket['userid'],text='👨‍💻 <b>'+thisoperator['callmeas']+'</b> подключился к диалогу',parse_mode='HTML')
            except:
                error_ticket= await check_error_ticket(thisicket['ticketid'])
               
                await call.answer(text=error_ticket, cache_time=0, show_alert=True)
                await call.message.delete()
                opentickets = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
                    [
                    InlineKeyboardButton(text="⬅ Вернуться к обращениям",callback_data='to_tickets')]
                ])
                
                #проверка на билет
                await bot.send_photo(chat_id=call.from_user.id,parse_mode='HTML', photo=photoparser('clientfinished'), reply_markup=opentickets)
                #проверка на билет
                raise CancelHandler()
    elif thisicket["isopen"]=="onair":

        await call.answer(text='Другой оператор уже начал диалог', cache_time=0, show_alert=True)
        await call.message.delete()
        opentickets = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
            [
            InlineKeyboardButton(text="⬅ Вернуться к обращениям",callback_data='to_tickets')]
        ])
        
        #проверка на билет
        await bot.send_photo(chat_id=call.from_user.id,parse_mode='HTML', photo=photoparser('clientfinished'), reply_markup=opentickets)
        raise CancelHandler()

    
    #чееее
    await call.message.delete()
    
    
    await bot.send_photo(chat_id=call.from_user.id,caption=html_text,parse_mode='HTML', reply_markup=operatorcontrol,photo=photoparser('changed'))
    
    
    msgs=ticket_collection.find_one({"ticketid":callback_data.get("ticketid"),"$or":[{'isopen':'created'},{'isopen':'onpause'}]})
    lostmsgs=msgs['extrafield']
    for lm in lostmsgs:
        if lm['isread']==False:


            if lm['type']=='voice':
                await bot.send_voice(chat_id=call.from_user.id, voice=lm['mediaid'])
            elif lm['type']=='photo':
                await bot.send_photo(chat_id=call.from_user.id, photo=lm['mediaid'], caption=lm['text'])
            elif lm['type']=='video':
                await bot.send_video(chat_id=call.from_user.id, video=lm['mediaid'], caption=lm['text'])
            elif lm['type']=='video_note':
                await bot.send_video_note(chat_id=call.from_user.id, video_note=lm['mediaid'])
            elif lm['type']=='document':
                await bot.send_document(chat_id=call.from_user.id, document=lm['mediaid'], caption=lm['text'])
            else:
                await bot.send_message(chat_id=call.from_user.id, text=lm['text'], parse_mode='HTML')
            

    ticket_collection.find_one_and_update(
        filter={"ticketid":callback_data.get("ticketid"), "$or":[{'isopen':'created'},{'isopen':'onpause'}]},
        update={"$set":{"extrafield.$[].isread": True}  }
    )
    ticket_collection.find_one_and_update(
        filter={"ticketid":callback_data.get("ticketid"), "$or":[{'isopen':'created'},{'isopen':'onpause'}]},
        update={"$set":{"isopen":"onair","operator":call.from_user.id,},'$addToSet': { 'extrafield': extradd }  }
    )
    
    await SupportManage.onair.set()
    await call.answer(cache_time=0)

@dp.message_handler(state=SupportManage.onair, text='🗣 Переключиться')
async def changeticket_supportbysupport(message: types.Message):     
    datamessagehere = "\n".join(
        [
            "Оператор приостановил диалог <i>("+datetime.now().strftime("%d.%m.%Y / %H:%M")+")</i>"
        ]
    ) 
    extradd={
            "side":"fromoperator" ,
            "date": datetime.now(), 
            "text":datamessagehere,
            "from_id":message.from_user.id,
            "message_from_id":message.message_id,
            "type":"text",
            "mediaid":"none",
            "isread":True}

    ticket_collection.find_and_modify(
        query={"operator": message.from_user.id, "isopen":"onair"},
        update={"$set":{"isopen":"onpause"},'$addToSet': { 'extrafield': extradd }}
    )
    html_text,supportmenubase=build_support_menu(message.from_user.id)

    await message.answer_photo(caption='Вы поставили обращение на паузу - не заставляйте клиента ждать!',parse_mode='HTML',reply_markup=ReplyKeyboardRemove(), photo=photoparser('paused') )
    await message.answer_photo(photo=photoparser('operatormainmenu'), caption=html_text,parse_mode='HTML',reply_markup=supportmenubase ) 
    await SupportManage.menu.set()

##################################
##################################
###################################ВСЕ ЧТО НИЖЕ ДОЛЖНО БЫТЬ В КОНЦЕ ДОКУМЕНТА########################################################
@dp.message_handler(state=SupportManage.onair)
async def currenttalk(message: types.Message):
    thisoperator =  staff_collection.find_one({"user_id":message.from_user.id})
    html_text="\n".join(
        [
            '<b>👨‍💻 '+thisoperator["callmeas"]+':</b>',
            message.text
        ]
    ) 
    thisicket=ticket_collection.find_one({"operator":message.from_user.id, "isopen":"onair"})
    try:
        await bot.send_message(chat_id=thisicket['userid'],text=html_text,parse_mode='HTML')
    except:
        datamessagehere="\n".join(
            [
                '<b>‼️Ошибка, похоже клиент забанил бота‼️</b> <i>('+datetime.now().strftime("%d.%m.%Y / %H:%M")+')</i>',
            ]
        )
        extradd={
            "side":"error" ,
            "date": datetime.now(), 
            "text":datamessagehere,
            "from_id":message.from_user.id,
            "message_from_id":message.message_id,
            "type":"text",
            "mediaid":"none",
            "isread":True}

        ticket_collection.find_and_modify(
            query={"ticketid":thisicket["ticketid"]},
            update={'$addToSet': { 'extrafield': extradd }}
        )
        html_text2="\n".join(
            [
                '<b>🤖 Бот КриптоКонсалтинг:</b>',
                '',
                'Клиент завершил диалог, нажмите на ❌ Завершить'
            ]
        )
        endinline= InlineKeyboardMarkup(row_width=1, inline_keyboard=[
            [InlineKeyboardButton(
                text='❌ Завершить',
                callback_data='operator_end_inline_ticket_error'
            )]
        ]) 
        await bot.send_photo(chat_id=thisicket['operator'],parse_mode='HTML', photo=photoparser('clientfinished'), reply_markup=ReplyKeyboardRemove())
        await bot.send_message(chat_id=thisicket['operator'], text=html_text2,parse_mode='HTML',reply_markup=endinline)

        #проверка на билет
        raise CancelHandler()       

    
    tomsas="\n".join(
            [
                '<b>👨‍💻 '+thisoperator["callmeas"]+':</b> <i>('+datetime.now().strftime("%d.%m.%Y / %H:%M")+')</i>',
                message.text
            ]
        )
    extradd={
        "side":"fromoperator" ,
        "date": datetime.now(), 
        "text":tomsas,
        "from_id":message.from_user.id,
        "message_from_id":message.message_id,
        "type":"text",
        "mediaid":"none",
        "isread":True}


    ticket_collection.find_and_modify(
        query={"ticketid":thisicket["ticketid"]},
        update={'$addToSet': { 'extrafield': extradd }}
    )
@dp.message_handler(state=ProjectManage.awaitingsup)
async def usercurrenttalk(message: types.Message, state: FSMContext):
    thisicket=ticket_collection.find_one({"userid":message.from_user.id, "$or":[{'isopen':'onair'},{'isopen':'onpause'},{'isopen':'created'}]})
    thisuser = user_collection.find_one({"user_id":message.from_user.id})
    if thisicket["isopen"]=="onair":
        html_text="\n".join(
            [
                '<b>🗣️ '+thisuser["callmeas"]+':</b>',
                message.text
            ]
        ) 
        await bot.send_message(chat_id=thisicket['operator'],text=html_text,parse_mode='HTML')
        tomsas="\n".join(
            [
                '<b>🗣️ '+thisuser["callmeas"]+':</b> <i>('+datetime.now().strftime("%d.%m.%Y / %H:%M")+')</i>',
                message.text
            ]
        )
        extradd={
            "side":"fromuser" ,
            "date": datetime.now(), 
            "text":tomsas,
            "from_id":message.from_user.id,
            "message_from_id":message.message_id,
            "type":"text",
            "mediaid":"none",
            "isread":True}

        ticket_collection.find_and_modify(
            query={"ticketid":thisicket["ticketid"]},
            update={'$addToSet': { 'extrafield': extradd }}
        )
    elif thisicket["isopen"]=="onpause" or thisicket["isopen"]=="created":
        tomsas="\n".join(
            [
                '<b>🗣️ '+thisuser["callmeas"]+':</b> <i>('+datetime.now().strftime("%d.%m.%Y / %H:%M")+')</i>',
                message.text
            ]
        )
        extradd={
            "side":"fromuser" ,
            "date": datetime.now(), 
            "text":tomsas,
            "from_id":message.from_user.id,
            "message_from_id":message.message_id,
            "type":"text",
            "mediaid":"none",
            "isread":False}

        ticket_collection.find_and_modify(
            query={"ticketid":thisicket["ticketid"]},
            update={'$addToSet': { 'extrafield': extradd }}
        )
  



###################################БЛОК ОТПРАВКИ ГОЛОСОВЫХ########################################################

@dp.message_handler( content_types=['voice'], state=SupportManage.onair)
async def currenttalk_voice(message: types.Message):
    thisoperator =  staff_collection.find_one({"user_id":message.from_user.id})
    tomsas="\n".join(
        [
            '<b>👨‍💻 '+thisoperator["callmeas"]+':</b> <i>('+datetime.now().strftime("%d.%m.%Y / %H:%M")+')</i>',
        ]
    )
    thisicket=ticket_collection.find_one({"operator":message.from_user.id, "isopen":"onair"})
    try:
        await bot.send_voice(chat_id=thisicket['userid'], voice=message.voice.file_id)
    except:
        datamessagehere="\n".join(
            [
                '<b>‼️Ошибка, похоже клиент забанил бота‼️</b> <i>('+datetime.now().strftime("%d.%m.%Y / %H:%M")+')</i>',
            ]
        )
        extradd={
            "side":"error" ,
            "date": datetime.now(), 
            "text":datamessagehere,
            "from_id":message.from_user.id,
            "message_from_id":message.message_id,
            "type":"text",
            "mediaid":"none",
            "isread":True}

        ticket_collection.find_and_modify(
            query={"ticketid":thisicket["ticketid"]},
            update={'$addToSet': { 'extrafield': extradd }}
        )
        html_text2="\n".join(
            [
                '<b>🤖 Бот КриптоКонсалтинг:</b>',
                '',
                'Клиент завершил диалог, нажмите на ❌ Завершить'
            ]
        )
        endinline= InlineKeyboardMarkup(row_width=1, inline_keyboard=[
            [InlineKeyboardButton(
                text='❌ Завершить',
                callback_data='operator_end_inline_ticket_error'
            )]
        ]) 
        await bot.send_photo(chat_id=thisicket['operator'],parse_mode='HTML', photo=photoparser('clientfinished'), reply_markup=ReplyKeyboardRemove())
        await bot.send_message(chat_id=thisicket['operator'], text=html_text2,parse_mode='HTML',reply_markup=endinline)

        #проверка на билет
        raise CancelHandler()       

    extradd={
        "side":"fromoperator" ,
        "date": datetime.now(), 
        "text":tomsas,
        "from_id":message.from_user.id,
        "message_from_id":message.message_id,
        "type":"voice",
        "mediaid":message.voice.file_id,
        "isread":True}

    ticket_collection.find_and_modify(
        query={"ticketid":thisicket["ticketid"]},
        update={'$addToSet': { 'extrafield': extradd }}
    )

@dp.message_handler(content_types=['voice'],state=ProjectManage.awaitingsup)
async def usercurrenttalk_voice(message: types.Message, state: FSMContext):


    thisicket=ticket_collection.find_one({"userid":message.from_user.id, "$or":[{'isopen':'onair'},{'isopen':'onpause'},{'isopen':'created'}]})
    thisuser = user_collection.find_one({"user_id":message.from_user.id})
    if thisicket["isopen"]=="onair":
    
        await bot.send_voice(chat_id=thisicket['operator'], voice=message.voice.file_id)
        tomsas="\n".join(
            [
                '<b>🗣️ '+thisuser["callmeas"]+':</b> <i>('+datetime.now().strftime("%d.%m.%Y / %H:%M")+')</i>',
            ]
        )
        extradd={
            "side":"fromuser" ,
            "date": datetime.now(), 
            "text":tomsas,
            "from_id":message.from_user.id,
            "message_from_id":message.message_id,
            "type":"voice",
            "mediaid":message.voice.file_id,
            "isread":True}

        ticket_collection.find_and_modify(
            query={"ticketid":thisicket["ticketid"]},
            update={'$addToSet': { 'extrafield': extradd }}
        )
    elif thisicket["isopen"]=="onpause" or thisicket["isopen"]=="created":
        tomsas="\n".join(
            [
                '<b>🗣️ '+thisuser["callmeas"]+':</b> <i>('+datetime.now().strftime("%d.%m.%Y / %H:%M")+')</i>',
            ]
        )
        extradd={
            "side":"fromuser" ,
            "date": datetime.now(), 
            "text":tomsas,
            "from_id":message.from_user.id,
            "message_from_id":message.message_id,
            "type":"voice",
            "mediaid":message.voice.file_id,
            "isread":False}

        ticket_collection.find_and_modify(
            query={"ticketid":thisicket["ticketid"]},
            update={'$addToSet': { 'extrafield': extradd }}
        )


###################################БЛОК ОТПРАВКИ фоточчек########################################################

@dp.message_handler( content_types=['photo'], state=SupportManage.onair)
async def currenttalk_photo(message: types.Message):

    thisoperator =  staff_collection.find_one({"user_id":message.from_user.id})
    if message.caption==None:
        message.caption=''
    tomsas="\n".join(
        [
            '<b>👨‍💻 '+thisoperator["callmeas"]+':</b> <i>('+datetime.now().strftime("%d.%m.%Y / %H:%M")+')</i>',
            message.caption
        ]
    )
    thisicket=ticket_collection.find_one({"operator":message.from_user.id, "isopen":"onair"})
    try:
        # await bot.send_voice(chat_id=thisicket['userid'], voice=message.voice.file_id)
       
        await bot.send_photo(chat_id=thisicket['userid'], photo=message.photo[0].file_id, caption=message.caption)
    except:
        datamessagehere="\n".join(
            [
                '<b>‼️Ошибка, похоже клиент забанил бота‼️</b> <i>('+datetime.now().strftime("%d.%m.%Y / %H:%M")+')</i>',
            ]
        )
        extradd={
            "side":"error" ,
            "date": datetime.now(), 
            "text":datamessagehere,
            "from_id":message.from_user.id,
            "message_from_id":message.message_id,
            "type":"text",
            "mediaid":"none",
            "isread":True}

        ticket_collection.find_and_modify(
            query={"ticketid":thisicket["ticketid"]},
            update={'$addToSet': { 'extrafield': extradd }}
        )
        html_text2="\n".join(
            [
                '<b>🤖 Бот КриптоКонсалтинг:</b>',
                '',
                'Клиент завершил диалог, нажмите на ❌ Завершить'
            ]
        )
        endinline= InlineKeyboardMarkup(row_width=1, inline_keyboard=[
            [InlineKeyboardButton(
                text='❌ Завершить',
                callback_data='operator_end_inline_ticket_error'
            )]
        ]) 
        await bot.send_photo(chat_id=thisicket['operator'],parse_mode='HTML', photo=photoparser('clientfinished'), reply_markup=ReplyKeyboardRemove())
        await bot.send_message(chat_id=thisicket['operator'], text=html_text2,parse_mode='HTML',reply_markup=endinline)

        #проверка на билет
        raise CancelHandler()       

    extradd={
        "side":"fromoperator" ,
        "date": datetime.now(), 
        "text":tomsas,
        "from_id":message.from_user.id,
        "message_from_id":message.message_id,
        "type":"photo",
        "mediaid":message.photo[0].file_id,
        "isread":True}

    ticket_collection.find_and_modify(
        query={"ticketid":thisicket["ticketid"]},
        update={'$addToSet': { 'extrafield': extradd }}
    )

@dp.message_handler(content_types=['photo'],state=ProjectManage.awaitingsup)
async def usercurrenttalk_photo(message: types.Message, state: FSMContext):
    if message.caption==None:
        message.caption=''

    thisicket=ticket_collection.find_one({"userid":message.from_user.id, "$or":[{'isopen':'onair'},{'isopen':'onpause'},{'isopen':'created'}]})
    thisuser = user_collection.find_one({"user_id":message.from_user.id})
    if thisicket["isopen"]=="onair":
    
        await bot.send_photo(chat_id=thisicket['operator'], photo=message.photo[0].file_id, caption=message.caption)
        tomsas="\n".join(
            [
                '<b>🗣️ '+thisuser["callmeas"]+':</b> <i>('+datetime.now().strftime("%d.%m.%Y / %H:%M")+')</i>',
                message.caption
            ]
        )
        extradd={
            "side":"fromoperator" ,
            "date": datetime.now(), 
            "text":tomsas,
            "from_id":message.from_user.id,
            "message_from_id":message.message_id,
            "type":"photo",
            "mediaid":message.photo[0].file_id,
            "isread":True}

        ticket_collection.find_and_modify(
            query={"ticketid":thisicket["ticketid"]},
            update={'$addToSet': { 'extrafield': extradd }}
        )
    elif thisicket["isopen"]=="onpause" or thisicket["isopen"]=="created":
        tomsas="\n".join(
            [
                '<b>🗣️ '+thisuser["callmeas"]+':</b> <i>('+datetime.now().strftime("%d.%m.%Y / %H:%M")+')</i>',
                message.caption
            ]
        )
        extradd={
            "side":"fromoperator" ,
            "date": datetime.now(), 
            "text":tomsas,
            "from_id":message.from_user.id,
            "message_from_id":message.message_id,
            "type":"photo",
            "mediaid":message.photo[0].file_id,
            "isread":False}

        ticket_collection.find_and_modify(
            query={"ticketid":thisicket["ticketid"]},
            update={'$addToSet': { 'extrafield': extradd }}
        )



###################################БЛОК ОТПРАВКИ Видюшшеччекк########################################################

@dp.message_handler( content_types=['video'], state=SupportManage.onair)
async def currenttalk_video(message: types.Message):

    thisoperator =  staff_collection.find_one({"user_id":message.from_user.id})
    if message.caption==None:
        message.caption=''
    tomsas="\n".join(
        [
            '<b>👨‍💻 '+thisoperator["callmeas"]+':</b> <i>('+datetime.now().strftime("%d.%m.%Y / %H:%M")+')</i>',
            message.caption
        ]
    )
    thisicket=ticket_collection.find_one({"operator":message.from_user.id, "isopen":"onair"})
    try:
        await bot.send_video(chat_id=thisicket['userid'], video=message.video.file_id, caption=message.caption)
    except:
        datamessagehere="\n".join(
            [
                '<b>‼️Ошибка, похоже клиент забанил бота‼️</b> <i>('+datetime.now().strftime("%d.%m.%Y / %H:%M")+')</i>',
            ]
        )
        extradd={
            "side":"error" ,
            "date": datetime.now(), 
            "text":datamessagehere,
            "from_id":message.from_user.id,
            "message_from_id":message.message_id,
            "type":"text",
            "mediaid":"none",
            "isread":True}

        ticket_collection.find_and_modify(
            query={"ticketid":thisicket["ticketid"]},
            update={'$addToSet': { 'extrafield': extradd }}
        )
        html_text2="\n".join(
            [
                '<b>🤖 Бот КриптоКонсалтинг:</b>',
                '',
                'Клиент завершил диалог, нажмите на ❌ Завершить'
            ]
        )
        endinline= InlineKeyboardMarkup(row_width=1, inline_keyboard=[
            [InlineKeyboardButton(
                text='❌ Завершить',
                callback_data='operator_end_inline_ticket_error'
            )]
        ]) 
        await bot.send_photo(chat_id=thisicket['operator'],parse_mode='HTML', photo=photoparser('clientfinished'), reply_markup=ReplyKeyboardRemove())
        await bot.send_message(chat_id=thisicket['operator'], text=html_text2,parse_mode='HTML',reply_markup=endinline)

        #проверка на билет
        raise CancelHandler()       

    extradd={
        "side":"fromoperator" ,
        "date": datetime.now(), 
        "text":tomsas,
        "from_id":message.from_user.id,
        "message_from_id":message.message_id,
        "type":"video",
        "mediaid":message.video.file_id,
        "isread":True}

    ticket_collection.find_and_modify(
        query={"ticketid":thisicket["ticketid"]},
        update={'$addToSet': { 'extrafield': extradd }}
    )

@dp.message_handler(content_types=['video'],state=ProjectManage.awaitingsup)
async def usercurrenttalk_video(message: types.Message, state: FSMContext):
    if message.caption==None:
        message.caption=''

    thisicket=ticket_collection.find_one({"userid":message.from_user.id, "$or":[{'isopen':'onair'},{'isopen':'onpause'},{'isopen':'created'}]})
    thisuser = user_collection.find_one({"user_id":message.from_user.id})
    if thisicket["isopen"]=="onair":
    
        await bot.send_video(chat_id=thisicket['operator'], video=message.video.file_id, caption=message.caption)
        tomsas="\n".join(
            [
                '<b>🗣️ '+thisuser["callmeas"]+':</b> <i>('+datetime.now().strftime("%d.%m.%Y / %H:%M")+')</i>',
                message.caption
            ]
        )
        extradd={
            "side":"fromuser" ,
            "date": datetime.now(), 
            "text":tomsas,
            "from_id":message.from_user.id,
            "message_from_id":message.message_id,
            "type":"video",
            "mediaid":message.video.file_id,
            "isread":True}

        ticket_collection.find_and_modify(
            query={"ticketid":thisicket["ticketid"]},
            update={'$addToSet': { 'extrafield': extradd }}
        )
    elif thisicket["isopen"]=="onpause" or thisicket["isopen"]=="created":
        tomsas="\n".join(
            [
                '<b>🗣️ '+thisuser["callmeas"]+':</b> <i>('+datetime.now().strftime("%d.%m.%Y / %H:%M")+')</i>',
                message.caption
            ]
        )
        extradd={
            "side":"fromuser" ,
            "date": datetime.now(), 
            "text":tomsas,
            "from_id":message.from_user.id,
            "message_from_id":message.message_id,
            "type":"video",
            "mediaid":message.video.file_id,
            "isread":False}

        ticket_collection.find_and_modify(
            query={"ticketid":thisicket["ticketid"]},
            update={'$addToSet': { 'extrafield': extradd }}
        )


###################################БЛОК ОТПРАВКИ Видевоквужочков########################################################

@dp.message_handler( content_types=['video_note'], state=SupportManage.onair)
async def currenttalk_video_note(message: types.Message):
    thisoperator =  staff_collection.find_one({"user_id":message.from_user.id})
    tomsas="\n".join(
        [
            '<b>👨‍💻 '+thisoperator["callmeas"]+':</b> <i>('+datetime.now().strftime("%d.%m.%Y / %H:%M")+')</i>',
        ]
    )
    thisicket=ticket_collection.find_one({"operator":message.from_user.id, "isopen":"onair"})
    try:
        await bot.send_video_note(chat_id=thisicket['userid'], video_note=message.video_note.file_id)
    except:
        datamessagehere="\n".join(
            [
                '<b>‼️Ошибка, похоже клиент забанил бота‼️</b> <i>('+datetime.now().strftime("%d.%m.%Y / %H:%M")+')</i>',
            ]
        )
        extradd={
            "side":"error" ,
            "date": datetime.now(), 
            "text":datamessagehere,
            "from_id":message.from_user.id,
            "message_from_id":message.message_id,
            "type":"text",
            "mediaid":"none",
            "isread":True}

        ticket_collection.find_and_modify(
            query={"ticketid":thisicket["ticketid"]},
            update={'$addToSet': { 'extrafield': extradd }}
        )
        html_text2="\n".join(
            [
                '<b>🤖 Бот КриптоКонсалтинг:</b>',
                '',
                'Клиент завершил диалог, нажмите на ❌ Завершить'
            ]
        )
        endinline= InlineKeyboardMarkup(row_width=1, inline_keyboard=[
            [InlineKeyboardButton(
                text='❌ Завершить',
                callback_data='operator_end_inline_ticket_error'
            )]
        ]) 
        await bot.send_photo(chat_id=thisicket['operator'],parse_mode='HTML', photo=photoparser('clientfinished'), reply_markup=ReplyKeyboardRemove())
        await bot.send_message(chat_id=thisicket['operator'], text=html_text2,parse_mode='HTML',reply_markup=endinline)

        #проверка на билет
        raise CancelHandler()       

    extradd={
        "side":"fromoperator" ,
        "date": datetime.now(), 
        "text":tomsas,
        "from_id":message.from_user.id,
        "message_from_id":message.message_id,
        "type":"video_note",
        "mediaid":message.video_note.file_id,
        "isread":True}

    ticket_collection.find_and_modify(
        query={"ticketid":thisicket["ticketid"]},
        update={'$addToSet': { 'extrafield': extradd }}
    )

@dp.message_handler(content_types=['video_note'],state=ProjectManage.awaitingsup)
async def usercurrenttalk_video_note(message: types.Message, state: FSMContext):


    thisicket=ticket_collection.find_one({"userid":message.from_user.id, "$or":[{'isopen':'onair'},{'isopen':'onpause'},{'isopen':'created'}]})
    thisuser = user_collection.find_one({"user_id":message.from_user.id})
    if thisicket["isopen"]=="onair":
    
        await bot.send_video_note(chat_id=thisicket['operator'], voice=message.video_note.file_id)
        tomsas="\n".join(
            [
                '<b>🗣️ '+thisuser["callmeas"]+':</b> <i>('+datetime.now().strftime("%d.%m.%Y / %H:%M")+')</i>',
            ]
        )
        extradd={
            "side":"fromuser" ,
            "date": datetime.now(), 
            "text":tomsas,
            "from_id":message.from_user.id,
            "message_from_id":message.message_id,
            "type":"video_note",
            "mediaid":message.video_note.file_id,
            "isread":True}

        ticket_collection.find_and_modify(
            query={"ticketid":thisicket["ticketid"]},
            update={'$addToSet': { 'extrafield': extradd }}
        )
    elif thisicket["isopen"]=="onpause" or thisicket["isopen"]=="created":
        tomsas="\n".join(
            [
                '<b>🗣️ '+thisuser["callmeas"]+':</b> <i>('+datetime.now().strftime("%d.%m.%Y / %H:%M")+')</i>',
            ]
        )
        extradd={
            "side":"fromuser" ,
            "date": datetime.now(), 
            "text":tomsas,
            "from_id":message.from_user.id,
            "message_from_id":message.message_id,
            "type":"video_note",
            "mediaid":message.video_note.file_id,
            "isread":False}

        ticket_collection.find_and_modify(
            query={"ticketid":thisicket["ticketid"]},
            update={'$addToSet': { 'extrafield': extradd }}
        )


###################################БЛОК ОТПРАВКИ Файликов########################################################

@dp.message_handler( content_types=['document'], state=SupportManage.onair)
async def currenttalk_doc(message: types.Message):

    thisoperator =  staff_collection.find_one({"user_id":message.from_user.id})
    if message.caption==None:
        message.caption=''
    tomsas="\n".join(
        [
            '<b>👨‍💻 '+thisoperator["callmeas"]+':</b> <i>('+datetime.now().strftime("%d.%m.%Y / %H:%M")+')</i>',
            message.caption
        ]
    )
    thisicket=ticket_collection.find_one({"operator":message.from_user.id, "isopen":"onair"})
    try:
        await bot.send_document(chat_id=thisicket['userid'], document=message.document.file_id, caption=message.caption)
    except:
        datamessagehere="\n".join(
            [
                '<b>‼️Ошибка, похоже клиент забанил бота‼️</b> <i>('+datetime.now().strftime("%d.%m.%Y / %H:%M")+')</i>',
            ]
        )
        extradd={
            "side":"error" ,
            "date": datetime.now(), 
            "text":datamessagehere,
            "from_id":message.from_user.id,
            "message_from_id":message.message_id,
            "type":"text",
            "mediaid":"none",
            "isread":True}

        ticket_collection.find_and_modify(
            query={"ticketid":thisicket["ticketid"]},
            update={'$addToSet': { 'extrafield': extradd }}
        )
        html_text2="\n".join(
            [
                '<b>🤖 Бот КриптоКонсалтинг:</b>',
                '',
                'Клиент завершил диалог, нажмите на ❌ Завершить'
            ]
        )
        endinline= InlineKeyboardMarkup(row_width=1, inline_keyboard=[
            [InlineKeyboardButton(
                text='❌ Завершить',
                callback_data='operator_end_inline_ticket_error'
            )]
        ]) 
        await bot.send_photo(chat_id=thisicket['operator'],parse_mode='HTML', photo=photoparser('clientfinished'), reply_markup=ReplyKeyboardRemove())
        await bot.send_message(chat_id=thisicket['operator'], text=html_text2,parse_mode='HTML',reply_markup=endinline)

        #проверка на билет
        raise CancelHandler()       

    extradd={
        "side":"fromoperator" ,
        "date": datetime.now(), 
        "text":tomsas,
        "from_id":message.from_user.id,
        "message_from_id":message.message_id,
        "type":"document",
        "mediaid":message.document.file_id,
        "isread":True}

    ticket_collection.find_and_modify(
        query={"ticketid":thisicket["ticketid"]},
        update={'$addToSet': { 'extrafield': extradd }}
    )

@dp.message_handler(content_types=['document'],state=ProjectManage.awaitingsup)
async def usercurrenttalk_doc(message: types.Message, state: FSMContext):
    if message.caption==None:
        message.caption=''

    thisicket=ticket_collection.find_one({"userid":message.from_user.id, "$or":[{'isopen':'onair'},{'isopen':'onpause'},{'isopen':'created'}]})
    thisuser = user_collection.find_one({"user_id":message.from_user.id})
    if thisicket["isopen"]=="onair":
    
        await bot.send_document(chat_id=thisicket['operator'], document=message.document.file_id, caption=message.caption)
        tomsas="\n".join(
            [
                '<b>🗣️ '+thisuser["callmeas"]+':</b> <i>('+datetime.now().strftime("%d.%m.%Y / %H:%M")+')</i>',
                message.caption
            ]
        )
        extradd={
            "side":"fromuser" ,
            "date": datetime.now(), 
            "text":tomsas,
            "from_id":message.from_user.id,
            "message_from_id":message.message_id,
            "type":"document",
            "mediaid":message.document.file_id,
            "isread":True}

        ticket_collection.find_and_modify(
            query={"ticketid":thisicket["ticketid"]},
            update={'$addToSet': { 'extrafield': extradd }}
        )
    elif thisicket["isopen"]=="onpause" or thisicket["isopen"]=="created":
        tomsas="\n".join(
            [
                '<b>🗣️ '+thisuser["callmeas"]+':</b> <i>('+datetime.now().strftime("%d.%m.%Y / %H:%M")+')</i>',
                message.caption
            ]
        )
        extradd={
            "side":"fromuser" ,
            "date": datetime.now(), 
            "text":tomsas,
            "from_id":message.from_user.id,
            "message_from_id":message.message_id,
            "type":"document",
            "mediaid":message.document.file_id,
            "isread":False}

        ticket_collection.find_and_modify(
            query={"ticketid":thisicket["ticketid"]},
            update={'$addToSet': { 'extrafield': extradd }}
        )




#-------------------------------------инлайн ответы---------------------------
@dp.message_handler( text='/creatematerial', state=SupportManage.menu)
async def generatematerial(message: types.Message):
    xs=secrets.token_hex(4)+'MATERIAL'+"{:03d}".format(secrets.randbelow(999))
    await message.answer(xs)


@dp.inline_handler(state='*')
async def show_inline_materials(query: types.InlineQuery):
   
    if len(query.query)<1:
        raise CancelHandler() 
    elif query.query.startswith('#'):
        string_modified=query.query.replace('#', '')
        materials_arr=inline_materials_collection.find({'category':{'$regex':string_modified}})
        results_arr=[]

        for mat_obj in materials_arr:

            toadd=types.InlineQueryResultArticle(
                id=mat_obj['material_id'],
                title=mat_obj['title'],
                description=mat_obj['description'],
                input_message_content=types.InputMessageContent(message_text=mat_obj['text'], parse_mode='HTML'),
                thumb_url=mat_obj['thumb']
            )

            results_arr.append(toadd)
            
        await query.answer(
            results=results_arr,
            cache_time=0,
            is_personal=True
        )
    else:
        materials_arr=inline_materials_collection.find(
            { "$text": { "$search": query.query}},
            { "score": { "$meta": "textScore" } }
            ).sort([('score', {'$meta': 'textScore'})])
        results_arr=[]

        for mat_obj in materials_arr:

            toadd=types.InlineQueryResultArticle(
                id=mat_obj['material_id'],
                title=mat_obj['title'],
                description=mat_obj['description'],
                input_message_content=types.InputMessageContent(message_text=mat_obj['text'], parse_mode='HTML'),
                thumb_url=mat_obj['thumb']
            )

            results_arr.append(toadd)
            
        await query.answer(
            results=results_arr,
            cache_time=0,
            is_personal=True
        )


#-------------------------------------инлайн ответы конец---------------------------