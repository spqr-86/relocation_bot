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

from utils import get_notion_page, usd_course

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()

TOKEN = os.getenv('TOKEN')

# State definitions conversation
SELECTING_ACTION, START_OVER, END = map(chr, range(3))

MENU = {
    'visa': 'b7e80c5d-eb4a-409f-8482-0a0884781cdb',
    'apartment': 'cb8484ac-a18e-4c15-9972-9443576ff5dc',
    'education': '40a2dce3-2d5c-4450-b0b6-3acff70921a6',
    'children': 'c4daaddf-0ff0-4e2d-8405-0a89393562c7',
    'business': '545ddc27-e749-4918-b579-2505890babb8',
    'coast': 'feb4585d-2144-43a6-ae61-eda791fceb91',
    'job': '4db02f87-51a2-48d0-b743-a87a01281ce6',
    'medical_care': '32dcdf74-97f4-4bba-8607-94013ec17058',
    'other': 'dd7b552a-50ca-4f87-b25d-e13915b3428d'
}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Select an action"""
    text = (
        "Добро пожаловать в наш бот помощи при переезде! "
        "Бот создан твоим мужем чтобы помочь нам сориентироваться в процессе переезда в Португаию. "
        "Чтобы начать, выбери один из следующих вариантов:"
    )
    buttons = [
        [
            InlineKeyboardButton(text='🛂 Визы и ВНЖ', callback_data='visa'),
            InlineKeyboardButton(text='🏠🛌 Жилье', callback_data='apartment'),
        ],
        [
            InlineKeyboardButton(text='🎓 Образование', callback_data='education'),
            InlineKeyboardButton(text='🧒 Детям', callback_data='children'),
        ],
        [
            InlineKeyboardButton(text='👨‍💼💼 Бизнес и финансовый сектор ', callback_data='business'),
            InlineKeyboardButton(text='💰🛍️ Стоимость жизни', callback_data='coast'),
        ],
        [
            InlineKeyboardButton(text='👨‍💼💼 Трудоустройство', callback_data='job'),
            InlineKeyboardButton(text='💊 Медицина', callback_data='medical_care'),
        ],

        [
            InlineKeyboardButton(text='📌 Прочее (язык, транспорт и т.д.)', callback_data='other'),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    await update.message.reply_text(text=text, reply_markup=keyboard)
    return SELECTING_ACTION


async def print_block(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Print chosen block."""
    user_input = update.callback_query.data
    max_length = 4050
    page_id = MENU[user_input]
    text = get_notion_page(page_id)
    text += 'Нажми /start чтобы вернуться в главное меню.'
    await update.callback_query.answer()
    while len(text) > 0:
        if len(text) > max_length:
            chunks = text[:max_length].rsplit('<a', 1)[0]
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
    return START_OVER


def main() -> None:
    """Run the bot."""
    application = Application.builder().token(TOKEN).build()

    selection_handlers = [
        CallbackQueryHandler(print_block, pattern="^(?!" + str(END) + ").*$"),
    ]
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SELECTING_ACTION: selection_handlers,
            START_OVER: [CommandHandler("start", start)],
        },
        fallbacks=[CommandHandler("stop", start)],
    )
    application.add_handler(conv_handler)
    application.run_polling()


if __name__ == "__main__":
    main()
