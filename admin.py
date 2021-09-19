from database import *
from wrappers import send_typing_action
from telegram.ext import CallbackContext
from telegram import ParseMode


@send_typing_action
def users(update, context: CallbackContext):
    list_not_include = ['_id', 'recommended', 'selected', 'not_selected', 'last_access']
    show_admin_data(update, 'USERS', get_users(), list_not_include)


@send_typing_action
def experiments(update, context: CallbackContext):
    list_not_include = ['_id']
    show_admin_data(update, 'EXPERIMENTS', get_experiments(), list_not_include)


@send_typing_action
def grades(update, context: CallbackContext):
    list_not_include = ['_id']
    show_admin_data(update, 'GRADES', get_grades(), list_not_include)


@send_typing_action
def reviews(update, context: CallbackContext):
    list_not_include = ['_id']
    show_admin_data(update, 'REVIEWS', get_reviews(), list_not_include)


def show_admin_data(update, title, data_list, list_not_include):
    telegram_id = update.effective_user.id
    # if has_user(telegram_id) and user_has_info(telegram_id, 'admin'):
    if has_user(telegram_id):
        data_html = f'\n------------ {title} [{data_list.count()}] ------------\n'
        for data in data_list:
            for key, value in data.items():
                if key not in list_not_include:
                    data_html += f'\n<b>{key}</b>: <i>{value}</i>'
            data_html += '\n\n----'
        update.message.reply_text(data_html, parse_mode=ParseMode.HTML)
    else:
        update.message.reply_text('Desculpe! Acesso não permitido!',
                                  parse_mode=ParseMode.HTML)