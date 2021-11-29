#  MIT License (MIT) (c) 2021
#  This software was created by ICMC Recommendation Group
#  Supervisor: Raymundo Saraiva
#
import logging
import os

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

from commands import *
from movie_handler import *
from admin import users, experiments, responses, reviews, populate_db

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def error(update, context):
    # telegram_id, name = (update.effective_user.id), (update.effective_user.first_name or '')
    # save_error(telegram_id, str(context.error))
    """Log Errors caused by Updates."""
    # logger.warning('Update on user %s caused error "%s"', telegram_id, context.error)
    logger.warning('Error "%s"',  context.error)
    # update.callback_query.edit_message_text(
    #     '\n\U0001F622 Desculpe mas tivemos um erro! '
    #     '\nPressione /start para recomeçar...'
    # )


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
    dp.add_handler(CommandHandler("help", help))

    # admin commands - needs 'admin' attribute on user
    dp.add_handler(CommandHandler("users", users))
    dp.add_handler(CommandHandler("experiments", experiments))
    dp.add_handler(CommandHandler("responses", responses))
    dp.add_handler(CommandHandler("reviews", reviews))
    dp.add_handler(CommandHandler("populate_db", populate_db))

    # CallbackQuery Handlers
    dp.add_handler(CallbackQueryHandler(consent_answer, pattern='consent_*'))
    dp.add_handler(CallbackQueryHandler(sex_answer, pattern='sex_*'))
    dp.add_handler(CallbackQueryHandler(age_answer, pattern='age_*'))
    dp.add_handler(CallbackQueryHandler(genre_answer, pattern='genre_*'))
    dp.add_handler(CallbackQueryHandler(keyword_answer, pattern='keyword_*'))
    dp.add_handler(CallbackQueryHandler(feedback_answer, pattern='feedback_*'))
    dp.add_handler(CallbackQueryHandler(after_feedback_answer, pattern='recommend_*'))
    dp.add_handler(CallbackQueryHandler(bandit_answer, pattern='bandit_*'))
    dp.add_handler(CallbackQueryHandler(extra_questions, pattern='extra_*'))

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
