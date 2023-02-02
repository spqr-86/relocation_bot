import os

import time

import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, constants
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
)

from dotenv import load_dotenv

from pages import MENU, EDUCATION_MENU, JOB_MENU
from utils import get_notion_page, retrieve_database, usd_course

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()

TOKEN = os.getenv('TOKEN')

MAX_LENGTH = 4050

# Shortcut for ConversationHandler.END
END = ConversationHandler.END

# State definitions conversation
SELECTING_ACTION, START_OVER = map(chr, range(2))

(
    EDUCATION,
    JOB,
    EDUCATION_FEATURE,
    VACANCIES,
    BUDGET,
    STOPPING,
    JOB_FEATURE,
) = map(chr, range(4, 11))


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Select an action"""
    context.user_data['MENU'] = MENU
    text = (
        "Добро пожаловать! "
        "Чтобы начать, выбери один из следующих вариантов:"
    )
    buttons = [
        [
            InlineKeyboardButton(text='💰Наш Бюджет', callback_data=BUDGET),
        ],
        [
            InlineKeyboardButton(text='🛂 Визы и ВНЖ', callback_data='visa'),
            InlineKeyboardButton(text='🛌 Жилье', callback_data='apartment'),
        ],
        [
            InlineKeyboardButton(text='🎓 Образование', callback_data='education'),
            InlineKeyboardButton(text='🧒 Детям', callback_data='children'),
        ],
        [
            InlineKeyboardButton(text='📈 Бизнес и финансовый сектор ', callback_data='business'),
            InlineKeyboardButton(text='🛍️ Стоимость жизни', callback_data='coast'),
        ],
        [
            InlineKeyboardButton(text='💼 Трудоустройство', callback_data='job'),
            InlineKeyboardButton(text='💊 Медицина', callback_data='medical_care'),
        ],
        [
            InlineKeyboardButton(text='💻 Обучение IT и не только. Начало карьеры', callback_data=EDUCATION),
        ],
        [
            InlineKeyboardButton(text='💼 Вакансии и Резюме', callback_data=JOB),
        ],
        [
            InlineKeyboardButton(text='📌 Прочее (язык, транспорт и т.д.)', callback_data='other'),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    if context.user_data.get(START_OVER):
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    else:
        await update.message.reply_text(text=text, reply_markup=keyboard)
    context.user_data[START_OVER] = False
    return SELECTING_ACTION


async def budget(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    database_id = '6b8943a4-28c8-49f0-bee4-e5bffb5e7d7d'
    database = retrieve_database(database_id)
    text = ''
    usd_sum = 0
    eur_sum = 0
    kzt_sum = 0
    rub_sum = 0
    for item in database:
        card = item['Card']['title'][0]['text']['content']
        text += f'<b>{card}</b>: '
        usd = item['🇺🇸 $']['number']
        if usd:
            usd_sum += usd
            text += f'{usd}$    '
        eur = item['🇪🇺 Euro']['number']
        if eur:
            eur_sum += eur
            text += f'{eur}€    '
        rub = item['🇷🇺 Rub']['number']
        if rub:
            rub_sum += rub
            text += f'{rub}₽    '
        kzt = item['🇰🇿 KZT']['number']
        if kzt:
            kzt_sum += kzt
            text += f'{kzt}₸'
        text += '\n\n'
    text += f'<b>Итого</b>: {usd_sum}$    {eur_sum}€    {round(rub_sum)}₽    {kzt_sum}₸\n\n'
    course_usd = usd_course()[0]
    course_eur = usd_course()[1]
    text += f'Курс: $ {course_usd}    €{course_eur}\n\n'
    total_usd = usd_sum + rub_sum/course_usd + (eur_sum * course_eur)/usd_sum
    total_euro = (usd_sum * course_usd)/course_eur + rub_sum/course_eur + eur_sum
    total_rub = usd_sum * course_usd + eur_sum * course_eur + rub_sum
    text += f'По текущему курсу у нас: {round(total_usd)}$ ИЛИ {round(total_euro)}€ ИЛИ {round(total_rub)}₽\n\n'
    notion_url = 'https://www.notion.so/Cards-835134304a624705a6607de0e51ea581'
    text += f'<a href=\'{notion_url}\'><b>Таблица в Notion</b></a>'
    buttons = [[InlineKeyboardButton(text="Back", callback_data=str(END))]]
    keyboard = InlineKeyboardMarkup(buttons)
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        text=text,
        reply_markup=keyboard,
        parse_mode=constants.ParseMode.HTML,
    )
    context.user_data[START_OVER] = True
    return START_OVER


async def print_block(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Print chosen block."""
    user_data = context.user_data
    user_input = update.callback_query.data
    page_id = user_data['MENU'][user_input]
    text = get_notion_page(page_id)
    await update.callback_query.answer()
    while len(text) > 0:
        if len(text) > MAX_LENGTH:
            chunks = text[:MAX_LENGTH].rsplit('<a', 1)[0]
            text = text[len(chunks):]
        else:
            chunks = text
            text = ""
        await context.bot.send_message(
            chat_id=update.callback_query.message.chat_id,
            text=chunks,
            parse_mode=constants.ParseMode.HTML,
            disable_web_page_preview=True,
        )
        time.sleep(1)
    buttons = [[InlineKeyboardButton(text="Back", callback_data=str(END))]]
    keyboard = InlineKeyboardMarkup(buttons)
    await context.bot.send_message(chat_id=update.callback_query.message.chat_id, text='-end-', reply_markup=keyboard)
    user_data[START_OVER] = True
    return START_OVER


async def education_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Education menu."""
    context.user_data['MENU'] = EDUCATION_MENU
    text = 'Обучение IT и не только. Начало карьеры'
    buttons = []
    for key, value in EDUCATION_MENU.items():
        buttons.append([InlineKeyboardButton(text=key, callback_data=key)])
    buttons.append([InlineKeyboardButton(text="Back", callback_data=str(END))])
    keyboard = InlineKeyboardMarkup(buttons)
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    context.user_data[START_OVER] = True
    return EDUCATION_FEATURE


async def job_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """job menu."""
    context.user_data['MENU'] = JOB_MENU
    text = 'Вакансии и Резюме'
    buttons = []
    for key, value in JOB_MENU.items():
        buttons.append([InlineKeyboardButton(text=key, callback_data=key)])
    buttons.append([InlineKeyboardButton(text="Back", callback_data=str(END))])
    keyboard = InlineKeyboardMarkup(buttons)
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    context.user_data[START_OVER] = True
    return JOB_FEATURE


async def end_second_level(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Return to top level conversation."""
    context.user_data[START_OVER] = True
    await start(update, context)
    return END


async def stop_nested(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Completely end conversation from within nested conversation."""
    await update.message.reply_text("Okay, bye.")
    return STOPPING


def main() -> None:
    """Run the bot."""
    application = Application.builder().token(TOKEN).build()

    job_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                job_menu, pattern="^" + str(JOB) + "$"
            ),
        ],
        states={
            JOB_FEATURE: [
                CallbackQueryHandler(print_block, pattern="^(?!" + str(END) + ").*$"),
            ],
            START_OVER: [
                CallbackQueryHandler(job_menu, pattern="^" + str(END) + "$"),
            ]
        },
        fallbacks=[
            CallbackQueryHandler(end_second_level, pattern="^" + str(END) + "$"),
            CommandHandler("stop", stop_nested),
        ],
    )
    education_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                education_menu, pattern="^" + str(EDUCATION) + "$"
            ),
        ],
        states={
            EDUCATION_FEATURE: [
                CallbackQueryHandler(print_block, pattern="^(?!" + str(END) + ").*$"),
            ],
            START_OVER: [
                CallbackQueryHandler(education_menu, pattern="^" + str(END) + "$"),
            ]
        },
        fallbacks=[
            CallbackQueryHandler(end_second_level, pattern="^" + str(END) + "$"),
            CommandHandler("stop", stop_nested),
        ],
    )
    selection_handlers = [
        education_conv,
        job_conv,
        CallbackQueryHandler(budget, pattern="^" + str(BUDGET) + "$"),
        CallbackQueryHandler(
            print_block,
            pattern="^(?!" + str(EDUCATION) + "|" + str(START_OVER) + "|" + str(JOB) + "|" + str(BUDGET) + ").*$"
        ),
    ]
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SELECTING_ACTION: selection_handlers,
            START_OVER: [
                CommandHandler("start", start),
                CallbackQueryHandler(start, pattern="^" + str(END) + "$")
            ],
            STOPPING: [CommandHandler("start", start)],
        },
        fallbacks=[CommandHandler("stop", start)],
    )
    application.add_handler(conv_handler)
    application.run_polling()


if __name__ == "__main__":
    main()
