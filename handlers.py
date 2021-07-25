from telegram.ext import CallbackContext
from telegram import ParseMode

from helpers.movie_helper import *
from database import update_feedback_on_db

from wrappers import send_typing_action
from markups import *
from helpers.keywords import keywords_list
from bandit import Bandit, epsilon_greedy_agent, update_payoff

# For Online Bandit Agent
pay_offs = dict()
epsilon, initial_rounds, decay = 0.2, 1, 0.999


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


def feedback_answer(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    telegram_id = update.effective_user.id
    movie_id = context.user_data.get('recommended').get('id')
    movie_title = context.user_data.get('recommended').get('title')
    source = context.user_data.get('recommended').get('source')
    feedback = query.data
    add_candidate_reward(movie_id, feedback)
    update_feedback_on_db(telegram_id, source, movie_id, movie_title, feedback)
    context.user_data['recommended'] = None
    query.edit_message_text(text=f'\U0001F44D Obrigado por avaliar o filme: {movie_title}!',
                            reply_markup=after_feedback_markup)


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
    candidates = {}
    for i in range(1, 3):
        for movie in discover(genre, keyword, i):
            candidates[movie.get('id')] = movie
    context.user_data['candidates'] = candidates
    recommend_movie(telegram_id, query, context)


def recommend_movie(telegram_id, query, context):
    candidates = context.user_data.get('candidates')
    if len(candidates) < 1:
        query.edit_message_text(text=f'\U0001F629 Desculpe! Não temos recommendações no momento. '
                                     f'\nDigite /filme para informar novos parâmetros.')
    movie = get_candidate(candidates, context)
    genre = context.user_data.get('iterative').get('genre')
    keyword = context.user_data.get('iterative').get('keyword')
    query.edit_message_text(text=f'\U0001F50D Filme recomendado:\n\n{movie_card(movie)}',
                            reply_markup=feedback_markup, parse_mode=ParseMode.HTML)
    source = f'iterative_{genre}_{keyword}'
    # Remove the movie just recommended from candidates
    candidates.pop(movie.get('id'))
    update_feedback_on_db(telegram_id, source, movie.get('id'), movie.get('title'))
    context.user_data['recommended'] = {'id': movie.get('id'),
                                        'title': movie.get('title'),
                                        'source': source}


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


def get_candidate(candidates, context):
    current_round = get_current_round(context)
    bandit = Bandit(candidates.keys())
    candidate = epsilon_greedy_agent(bandit, pay_offs, current_round)
    add_current_round(context)
    return candidates[candidate]


def add_candidate_reward(action, reward):
    reward = 1 if 'feedback_liked' in reward else 0
    update_payoff(pay_offs, action, reward)
