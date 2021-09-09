import random

from telegram.ext import CallbackContext
from telegram import ParseMode

from helpers.movie_helper import *
from wrappers import send_typing_action
from markups import *
from helpers.keywords import keywords_list
from context_bandit import policy

from database import *


def welcome(update):
    update.message.reply_text(
        'Bem vindo ao \U0001F3AC MovieStar! '
        '\n\nEscolha um gênero abaixo',
        reply_markup=genre_markup
    )


def genre_buttons_reply(update):
    update.message.reply_text(
        'Escolha um gênero abaixo',
        reply_markup=genre_markup
    )


def genre_buttons_edit(query):
    query.edit_message_text(
        'Escolha um gênero abaixo',
        reply_markup=genre_markup
    )


def genre_answer(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    genre_code = get_code(query.data)
    context.user_data['iterative'] = None
    context.user_data['iterative'] = {'genre': genre_code}
    keyword_markup, markup_line, line_count = [], [], 1
    for keyword, code in keywords_list.get(genre_code).items():
        if line_count <= 2:
            markup_line.append(InlineKeyboardButton(keyword, callback_data=f'keyword_{code}'))
            line_count += 1
        else:
            keyword_markup.append(markup_line)
            markup_line, line_count = [], 1
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
    context.user_data['candidates'] = get_n_candidates(context, genre, keyword, 3)
    recommend_movie(telegram_id, query, context)


def remove_recommended(telegram_id, candidates):
    for recommended in get_recommended(telegram_id):
        if recommended in candidates:
            candidates.pop(recommended)


def recommend_movie(telegram_id, query, context, exploit=False):
    add_current_round(context)

    candidates = context.user_data.get('candidates')
    remove_recommended(telegram_id, candidates)
    # TODO: If candidates < n discover more candidates
    candidates_id = list(candidates)

    if len(candidates) < 1:
        query.edit_message_text(text=f'\U0001F629 Desculpe! Não temos recommendações no momento.'
                                     f'\nDigite /filme para informar novos parâmetros.')

    context_ids = get_context_ids(telegram_id)
    context_binarized = binarize_context(context_ids)
    context.user_data['context_to_predict'] = get_context_ids(telegram_id)

    movie_bandit = get_candidate_from_context(candidates, context_binarized, exploit)
    label = candidates_id.index(movie_bandit.get('id'))

    movie_baseline = get_candidate_from_baseline(candidates)
    while movie_baseline.get('id') == movie_bandit.get('id'):
        movie_baseline = get_candidate_from_baseline(candidates)

    movie_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(text=movie_bandit.get('title'), callback_data='selected_bandit')],
        [InlineKeyboardButton(text=movie_baseline.get('title'), callback_data='selected_baseline')]
    ])

    query.edit_message_text(text=f'\U0001F50D Filmes recomendados:\n\n'
                                 f'1 - {movie_card(movie_bandit)}\n\n\n'
                                 f'2 - {movie_card(movie_baseline)}'
                                 f'\n\n\n<b>Selecione a melhor recomendação:</b>\n',
                            reply_markup=movie_markup, parse_mode=ParseMode.HTML, disable_web_page_preview=True)

    context.user_data['recommended'] = {'bandit': {'id': movie_bandit.get('id'),
                                                   'context': context_ids,
                                                   'labels': label},
                                        'baseline': {'id': movie_baseline.get('id')}
                                        }


def feedback_answer(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    feedback = query.data
    telegram_id = update.effective_user.id
    recommended = context.user_data.get('recommended')
    reward = int('selected_bandit' in feedback)
    candidates = list(context.user_data.get('candidates'))
    context_to_predict = context.user_data.get('context_to_predict') or []

    # Experiment result to save on DB
    movie_bandit_id = recommended['bandit']['id']
    movie_baseline_id = recommended['baseline']['id']
    selected_movie_id = movie_bandit_id if reward else movie_baseline_id
    experiment = {'bandit': movie_bandit_id,
                  'baseline': movie_baseline_id,
                  'selected': get_code(feedback),
                  'user': telegram_id
                  }
    save_experiment(experiment)
    save_recommended(movie_bandit_id, movie_baseline_id, telegram_id)
    save_round(telegram_id, context_to_predict, candidates, movie_bandit_id, reward)
    save_selected(telegram_id, selected_movie_id)

    print(f'# REC > {update.effective_user.first_name}[{telegram_id}] > SELECTED[{get_code(feedback)}] > ID[{selected_movie_id}]')

    context.user_data['recommended'] = None
    query.edit_message_text(text=f'\U0001F44D Obrigado pela sua avaliação!',
                            reply_markup=after_feedback_markup)


def after_feedback_answer(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    if 'recommend_next' in query.data:
        query.edit_message_text(text=f'Está satisfeito com os filmes atuais ou deseja explorar novas opções?',
                                reply_markup=bandit_feedback_markup)
    elif 'recommend_end' in query.data:
        genre_buttons_edit(query)


def bandit_answer(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    telegram_id = update.effective_user.id
    genre_id = int(context.user_data.get('iterative').get('genre'))
    keyword = context.user_data.get('iterative').get('keyword')
    if 'bandit_exploit' in query.data:
        context.user_data['candidates'] = None
        context.user_data['candidates'] = get_n_candidates(context, genre_id, keyword, 3)
        recommend_movie(telegram_id, query, context, exploit=True)
    elif 'bandit_explore' in query.data:
        context.user_data['candidates'] = None
        context.user_data['candidates'] = get_n_candidates(context, genre_id, None, 3)
        recommend_movie(telegram_id, query, context, exploit=False)


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
    return candidates[action]


def get_candidate_from_baseline(candidates):
    actions = list(candidates)
    action = random.choice(actions)
    return candidates[action]
