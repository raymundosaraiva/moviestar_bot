from user_handler import *
from database import *

from wrappers import send_typing_action


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
@send_typing_action
def start(update, context: CallbackContext):
    """Send a message when the command /start is issued."""
    context.user_data['opinion'] = None
    telegram_id, name, username = update.effective_user.id, update.effective_user.first_name, update.effective_user.name
    if has_user(telegram_id):
        update_user_last_access(telegram_id)
        if not user_has_info(telegram_id, 'consent'):
            welcome(update)
        elif not user_has_info(telegram_id, 'sex'):
            sex_buttons_edit(update)
        elif not user_has_info(telegram_id, 'age'):
            age_buttons_edit(update)
        else:
            genre_buttons_edit(update)
    else:
        create_user(telegram_id, name, username)
        welcome(update)


@send_typing_action
def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Favor entrar em contato com https://t.me/raysaraiva')


@send_typing_action
def text(update, context):
    if context.user_data.get('opinion'):
        telegram_id, message = update.effective_user.id, update.message.text
        save_review(telegram_id, message)
        update.message.reply_text('\U0001F603 Obrigado pela sua participação!'
                                  '\nCaso queira uma nova recomendação digite /start')
        context.user_data['opinion'] = None
    else:
        update.message.reply_text('\U0001F622 Desculpe!\nVocê deve iteragir nas opções informadas!'
                                  '\n Para recomeçar digite ou pressione /start')
