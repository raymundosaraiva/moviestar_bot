from handlers import *
from database import save_user_info, save_user_chat

from wrappers import send_typing_action


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
@send_typing_action
def start(update, _: CallbackContext):
    """Send a message when the command /start is issued."""
    user_id, name, username = update.effective_user.id, update.effective_user.first_name, update.effective_user.name
    if user_id and name:
        if save_user_info(user_id, name, username):
            welcome(update)
        else:
            update.message.reply_text('Erro ao salvar dados! Digite /help para ajuda')
    else:
        print('Error: Missing user Data!')
        update.message.reply_text('Erro ao carregar dados! Digite /help para ajuda')


@send_typing_action
def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Favor entrar em contato com https://t.me/raysaraiva')


@send_typing_action
def filme(update, context):
    """Send a message when the command /filme is issued."""
    genre_buttons_reply(update)


@send_typing_action
def text(update, context):
    genre_buttons_reply(update)
