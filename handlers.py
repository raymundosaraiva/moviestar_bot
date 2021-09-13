import random

from telegram.ext import CallbackContext
from telegram import ParseMode

from helpers.movie_helper import *
from helpers.genres import genres
from wrappers import send_typing_action
from markups import *
from helpers.keywords import keywords_list, get_keyword_name
from context_bandit import policy


from database import *


def welcome(update):
    update.message.reply_text(
        '\U0001F3AC Bem vindo!'
        '\n\nEste é um experimento controlado.'
        '\n\nDesenvolvido para um projeto de mestrado da USP '
        'com o intuito de avaliar um modelo de recomendação de filmes em tempo real.'
        '\n\n Os seus dados não serão expostos e tem uso apenas nesta pesquisa.'
        '\n\n Ao selecionar a opção "Desejo participar" você concorda com os nossos termos e deve:'
        '\n  - Informar seu sexo e faixa etária;'
        '\n  - Receber no mínimo 5 recomendações;'
        '\n  - Avaliar todas as recomendações;'
        '\n  - Responder sobre a sua satisfação final.;'
        '\n\n Obrigado desde já pela participação',
        reply_markup=consent_markup, parse_mode=ParseMode.HTML
    )


def genre_buttons_edit(option, reply=False):
    if reply:
        option.edit_message_text(
            'Escolha um gênero abaixo',
            reply_markup=genre_markup
        )
    else:
        option.message.reply_text(
            'Escolha um gênero abaixo',
            reply_markup=genre_markup
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


def genre_answer(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    genre_code = get_code(query.data)
    context.user_data['iterative'] = None
    context.user_data['iterative'] = {'genre': genre_code}
    keyword_markup, markup_line = [], []
    for keyword, code in keywords_list.get(genre_code).items():
        markup_line.append(InlineKeyboardButton(keyword, callback_data=f'keyword_{code}'))
        if (len(markup_line) % 2) == 0:
            keyword_markup.append(markup_line)
            markup_line = []
    if len(markup_line) > 0:
        markup_line.append(InlineKeyboardButton(keyword, callback_data=f'keyword_{code}'))
    keyword_markup.append([InlineKeyboardButton('Qualquer tipo', callback_data='keyword_any')])
    query.edit_message_text(text=f"Escolha o que mais te interessa:",
                            reply_markup=InlineKeyboardMarkup(keyword_markup))


@send_typing_action
def keyword_answer(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    keyword = '' if ('any' in get_code(query.data)) else get_code(query.data)
    context.user_data['iterative']['keyword'] = keyword
    genre = context.user_data.get('iterative').get('genre')
    telegram_id = update.effective_user.id
    context.user_data['candidates'] = None
    context.user_data['candidates'] = get_n_candidates(context, genre, keyword)
    recommend_movie(telegram_id, query, context)


def remove_recommended(telegram_id, candidates):
    for recommended in get_recommended(telegram_id):
        if recommended in candidates:
            candidates.pop(recommended)


def recommend_movie(telegram_id, query, context, exploit=False):
    candidates = context.user_data.get('candidates')
    remove_recommended(telegram_id, candidates)
    # TODO: If candidates < n discover more candidates
    candidates_id = list(candidates)

    if len(candidates) < 1:
        query.edit_message_text(text=f'\U0001F629 Desculpe! Não temos recommendações no momento.'
                                     f'\nDigite /filme para informar novos parâmetros.')

    context_ids = get_context_ids(telegram_id)
    context_binarized = binarize_context(context_ids)
    context.user_data['context_to_predict'] = context_ids

    movie_bandit, state = get_candidate_from_context(candidates, context_binarized, exploit)
    label = candidates_id.index(movie_bandit.get('id'))

    query.edit_message_text(text=f'{movie_card(movie_bandit)}'
                                 f'\n\n\n<b>Avalie a recomendação:</b>\n',
                            reply_markup=feedback_markup, parse_mode=ParseMode.HTML, disable_web_page_preview=False)

    context.user_data['recommended'] = {'id': movie_bandit.get('id'),
                                        'title': movie_bandit.get('title'),
                                        'context': context_ids,
                                        'state': state,
                                        'labels': label}


def feedback_answer(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    feedback = query.data
    telegram_id = update.effective_user.id
    recommended = context.user_data.get('recommended')
    reward = int('feedback_liked' in feedback)
    if not reward:
        count_negative_feedback(context)
    candidates = list(context.user_data.get('candidates'))
    context_to_predict = context.user_data.get('context_to_predict') or []

    # Experiment result to save on DB
    movie_id = recommended['id']
    movie_title = recommended['title']
    state = recommended['state']
    genre_id = context.user_data.get('iterative').get('genre')
    keyword_id = context.user_data.get('iterative').get('keyword')
    experiment = {'genre': genres.get(int(genre_id)),
                  'keyword': get_keyword_name(genre_id, keyword_id) if keyword_id else '',
                  'movie_id': movie_id,
                  'movie_title': movie_title,
                  'feedback': get_code(feedback),
                  'state': state,
                  'user': telegram_id
                  }
    save_experiment(experiment)
    save_round(telegram_id, context_to_predict, candidates, movie_id, reward)
    update_user_column_array(telegram_id, movie_id, 'recommended')
    update_user_column_array(telegram_id, movie_id, 'selected' if reward else 'not_selected')

    print(f'#REC > {update.effective_user.first_name}[{telegram_id}] > {movie_title}[{movie_id}] {get_code(feedback)}')

    context.user_data['recommended'] = None
    query.message.reply_text(text=f'\U0001F603 Obrigado pela sua avaliação!',
                             reply_markup=after_feedback_markup)


def after_feedback_answer(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    if 'recommend_next' in query.data:
        negative_feedback_count = context.user_data.get('negative_feedback') or 0
        # Ask if user give n negative feedback
        if negative_feedback_count >= CONFIG.BANDIT_NEGATIVE_FEEDBACK:
            query.edit_message_text(text=f'Quer manter o padrão de recomendação atual ou deseja explorar novas opções?',
                                    reply_markup=bandit_feedback_markup)
            context.user_data['negative_feedback'] = 0
        else:
            context.user_data['negative_feedback'] = 0
            telegram_id = update.effective_user.id
            recommend_movie(telegram_id, query, context)
    elif 'recommend_param' in query.data:
        genre_buttons_edit(query, True)
    elif 'recommend_end' in query.data:
        query.edit_message_text(
            'Como você avalia as recomendações que tem recebido?',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton('Estou Muito Satisfeito', callback_data='final_5')],
                [InlineKeyboardButton('Estou Satisfeito', callback_data='final_4')],
                [InlineKeyboardButton('Estou Pouco Satisfeito', callback_data='final_3')],
                [InlineKeyboardButton('Estou Insatisfeito', callback_data='final_2')],
                [InlineKeyboardButton('Estou Muito Insatisfeito', callback_data='final_1')]
            ])
        )


def bandit_answer(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    telegram_id = update.effective_user.id
    genre_id = int(context.user_data.get('iterative').get('genre'))
    keyword = context.user_data.get('iterative').get('keyword')
    if 'bandit_exploit' in query.data:
        context.user_data['candidates'] = None
        context.user_data['candidates'] = get_n_candidates(context, genre_id, keyword)
        recommend_movie(telegram_id, query, context, exploit=True)
    elif 'bandit_explore' in query.data:
        context.user_data['candidates'] = None
        context.user_data['candidates'] = get_n_candidates(context, genre_id, None)
        recommend_movie(telegram_id, query, context, exploit=False)


def final_answer(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    telegram_id = update.effective_user.id
    code = int(get_code(query.data))
    print(f'[{telegram_id}] Final response > {code}')
    query.edit_message_text('Obrigado!\nCaso queira uma nova recomendação digite /start')


def get_current_round(context):
    iterative = context.user_data.get('iterative')
    genre, keyword = iterative.get('genre'), iterative.get('keyword')
    rounds = context.user_data.get('round')
    if rounds and rounds.get(genre) and rounds.get(genre).get(keyword):
        return rounds.get(genre).get(keyword)
    return 1


def add_current_round(context):
    iterative = context.user_data.get('iterative')
    genre, keyword = iterative.get('genre'), iterative.get('keyword')
    rounds = context.user_data.get('round')
    if rounds and rounds.get(genre) and rounds.get(genre).get(keyword):
        context.user_data['round'][genre][keyword] += 1
    else:
        context.user_data['round'] = {genre: {keyword: 1}}


def get_candidate_from_context(candidates, context_to_predict, exploit):
    actions = list(candidates)
    X_context, y_context, r_context = get_all_context_binarized(actions)
    action = policy(actions, context_to_predict, X_context, y_context, r_context, exploit)
    state = 'no_context' if not X_context else ('exploit' if exploit else 'explore')
    return candidates[action], state


def get_candidate_from_baseline(candidates):
    actions = list(candidates)
    action = random.choice(actions)
    return candidates[action]


def count_negative_feedback(context):
    if context.user_data.get('negative_feedback'):
        context.user_data['negative_feedback'] += 1
    else:
        context.user_data['negative_feedback'] = 1
