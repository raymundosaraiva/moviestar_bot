import random
from telegram.ext import CallbackContext
from telegram import ParseMode

from helpers.movie_helper import *
from database import update_feedback_on_db
from wrappers import send_typing_action
from markups import *
from helpers.keywords import keywords_list
from bandit import Bandit, epsilon_greedy_agent, update_payoff
from context_bandit import policy
from helpers.features import Features

# For Online Bandit Agent
pay_offs, X_global, y_global, r_global = [], [], [], []


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
    candidates = dict()
    for i in range(1, 3):
        for movie in discover(genre, keyword, i):
            candidates[movie.get('id')] = movie
    context.user_data['candidates'] = candidates
    recommend_movie(telegram_id, query, context)


def recommend_movie(telegram_id, query, context):
    add_current_round(context)
    candidates = context.user_data.get('candidates')

    if len(candidates) < 1:
        query.edit_message_text(text=f'\U0001F629 Desculpe! Não temos recommendações no momento.'
                                     f'\nDigite /filme para informar novos parâmetros.')

    genre_id = int(context.user_data.get('iterative').get('genre'))
    keyword = context.user_data.get('iterative').get('keyword')
    context_to_predict = Features(genre_id).get()
    # TODO: Watched movies as context?
    # TODO: UserId as context?
    # TODO: Should we ask questions to be used
    # TODO: Keep meaning for context actions features and rewards and just binarize them?
    movie_bandit = get_candidate_from_context(candidates, context_to_predict)
    label = list(candidates).index(movie_bandit.get('id'))

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

    # Remove the movie just recommended from candidates
    candidates.pop(movie_bandit.get('id'))
    # TODO: Should we remove both movies?

    context.user_data['recommended'] = {'bandit': {'id': movie_bandit.get('id'),
                                                   'context': context_to_predict,
                                                   'labels': label},
                                        'baseline': {'id': movie_baseline.get('id')}
                                        }


def feedback_answer(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    feedback = query.data
    telegram_id = update.effective_user.id
    recommended = context.user_data.get('recommended')
    add_candidate_reward(telegram_id, recommended, feedback)

    context.user_data['recommended'] = None
    query.edit_message_text(text=f'\U0001F44D Obrigado pela sua avaliação!',
                            reply_markup=after_feedback_markup)


def after_feedback_answer(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    if 'recommend_next' in query.data:
        telegram_id = update.effective_user.id
        recommend_movie(telegram_id, query, context)
    elif 'recommend_end' in query.data:
        genre_buttons_edit(query)


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


def get_candidate_from_context(candidates, context_to_predict):
    actions = list(candidates)
    action = policy(actions, context_to_predict, X_global, y_global, r_global)
    return candidates[action]


def get_candidate_from_baseline(candidates):
    actions = list(candidates)
    action = random.choice(actions)
    return candidates[action]


def get_candidate(candidates, context):
    current_round = get_current_round(context)
    bandit = Bandit(candidates.keys())
    candidate = epsilon_greedy_agent(bandit, pay_offs, current_round)
    add_current_round(context)
    return candidates[candidate]


def add_candidate_reward(telegram_id, recommended, reward):
    reward = int('selected_bandit' in reward)
    action = recommended.get('bandit').get('id')
    context = recommended.get('bandit').get('context')
    labels = recommended.get('bandit').get('labels')
    # pay_offs.append({'telegram_id': telegram_id, 'action': action, 'reward': reward})
    X_global.append(context)
    y_global.append(labels)
    r_global.append(reward)
