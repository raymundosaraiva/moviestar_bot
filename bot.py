#  MIT License (MIT) (c) 2021
#  This software was created by ICMC Recommendation Group
#  Supervisor: Raymundo Saraiva
#
import logging
import os

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

from config import DefaultConfig
from commands import *


CONFIG = DefaultConfig()

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def connect_to_telegram():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(CONFIG.TELEGRAM_TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("filme", filme))
    dp.add_handler(CommandHandler("help", help))

    # CallbackQuery Handlers
    dp.add_handler(CallbackQueryHandler(genre_answer, pattern='genre_*'))
    dp.add_handler(CallbackQueryHandler(keyword_answer, pattern='keyword_*'))
    dp.add_handler(CallbackQueryHandler(feedback_answer, pattern='selected_*'))
    dp.add_handler(CallbackQueryHandler(after_feedback_answer, pattern='recommend_*'))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, text))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    if CONFIG.APP_NAME:
        PORT = int(os.environ.get('PORT', 8433))
        updater.start_webhook(listen="0.0.0.0",
                              port=PORT,
                              url_path=CONFIG.TELEGRAM_TOKEN)

        updater.bot.set_webhook(CONFIG.APP_NAME + CONFIG.TELEGRAM_TOKEN)
    else:
        updater.start_polling()
    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == "__main__":
    try:
        connect_to_telegram()
    except Exception as error:
        raise error
