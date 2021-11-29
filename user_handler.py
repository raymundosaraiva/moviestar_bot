from telegram.ext import CallbackContext
from telegram import ParseMode

from database import *
from markups import *
from helpers.movie_helper import get_code
from movie_handler import genre_buttons_edit


def welcome(update):
    update.message.reply_text(
        '\U0001F3AC <b>Bem vindo!</b>'
        '\n\nEste é um experimento controlado.'
        '\n\nDesenvolvido para um projeto de mestrado da USP '
        'com o intuito de avaliar um modelo de recomendação de filmes em tempo real.'
        '\n\nOs seus dados não serão expostos e tem uso apenas nesta pesquisa.'
        '\n\n<b>Ao selecionar a opção "Desejo participar" você concorda com os nossos termos e deve:</b>'
        '\n - Informar seu sexo e faixa etária;'
        '\n - Receber no mínimo 5 recomendações;'
        '\n - Avaliar todas as recomendações;'
        '\n - Responder sobre a sua satisfação final.'
        '\n\n<b>A cada interação você deverá optar entre:</b>'
        '\n\U0001F503 Receber recomendações pelo histórico '
        '(baseadas no gênero, palavra-chave e filmes que você e outros avaliaram)'
        '\n\U0001F50D Explorar recomendações diversificadas '
        '(baseadas apenas no gênero e palavra-chave selecionados)'
        '\n\n<b>Agradecemos desde já pela participação</b>',
        reply_markup=consent_markup, parse_mode=ParseMode.HTML
    )


def age_buttons_edit(option, reply=False):
    if reply:
        option.edit_message_text(
            'Qual a sua faixa etária?',
            reply_markup=age_markup
        )
    else:
        option.message.reply_text(
            'Qual a sua faixa etária?',
            reply_markup=age_markup
        )


def sex_buttons_edit(option, reply=False):
    if reply:
        option.edit_message_text(
            'Qual o seu sexo?',
            reply_markup=sex_markup
        )
    else:
        option.message.reply_text(
            'Qual o seu sexo?',
            reply_markup=sex_markup
        )


def consent_answer(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    consent_code = get_code(query.data)
    telegram_id = update.effective_user.id
    save_user_info(telegram_id, 'consent', consent_code)
    if consent_code == 'agree':
        sex_buttons_edit(query, True)
    else:
        update.message.reply_text(
            ':( Entendemos que você não concorda em participar no momento.'
            '\nCaso mude de ideia basta digitar /start'
        )


def sex_answer(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    sex_code = get_code(query.data)
    telegram_id = update.effective_user.id
    save_user_info(telegram_id, 'sex', sex_code)
    if not user_has_info(telegram_id, 'age'):
        age_buttons_edit(query, True)
    else:
        genre_buttons_edit(query, True)


def age_answer(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    age_code = get_code(query.data)
    telegram_id = update.effective_user.id
    save_user_info(telegram_id, 'age', age_code)
    genre_buttons_edit(query, True)


def extra_questions(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    telegram_id = update.effective_user.id
    data = query.data
    resp = get_code(get_code(data))
    if '_0_' in data:
        save_response(telegram_id, '0', resp)
        query.edit_message_text(
            'Em geral, como você avalia as recomendações que tem recebido?',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton('Muito Satisfeito', callback_data='extra_1_5')],
                [InlineKeyboardButton('Satisfeito', callback_data='extra_1_4')],
                [InlineKeyboardButton('Indiferente', callback_data='extra_1_3')],
                [InlineKeyboardButton('Insatisfeito', callback_data='extra_1_2')],
                [InlineKeyboardButton('Muito Insatisfeito', callback_data='extra_1_1')]
            ])
        )
    elif '_1_' in data:
        save_response(telegram_id, '1', resp)
        query.edit_message_text(
            'Percebeu mudanças nas recomendações recebidas quando alternou entre '
            'receber recomendações pelo histórico ou explorar recomendações diversificadas?',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton('Sempre', callback_data='extra_2_5')],
                [InlineKeyboardButton('Muitas', callback_data='extra_2_4')],
                [InlineKeyboardButton('Indiferente', callback_data='extra_2_3')],
                [InlineKeyboardButton('Poucas', callback_data='extra_2_2')],
                [InlineKeyboardButton('Nunca', callback_data='extra_2_1')]
            ]))
    elif '_2_' in data:
        save_response(telegram_id, '2', resp)
        query.edit_message_text(
            'Deseja dar mais detalhes sobre a sua percepção ao alternar entre '
            'recomendações pelo histórico e explorar recomendações diversificadas?',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(text='\U0001F44E Não, podemos pular', callback_data='extra_3_no')],
                [InlineKeyboardButton(text='\U0001F44D Sim, quero escrever', callback_data='extra_3_yes')]
            ])
        )
    elif '_3_' in data:
        save_response(telegram_id, '3', resp)
        if 'no' == resp:
            query.edit_message_text('Obrigado!\nCaso queira uma nova recomendação digite /start')
        elif 'yes' == resp:
            context.user_data['opinion'] = True
            query.edit_message_text('Digite a sua avaliação, caso tenha desistido digite /start')
