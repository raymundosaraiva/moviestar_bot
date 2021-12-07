from telegram.ext import CallbackContext
from telegram import ParseMode

from helpers.movie_helper import *
from helpers.genres import genres
from wrappers import send_typing_action
from markups import *
from helpers.keywords import keywords_list, get_keyword_name
from context_bandit import policy

from database import *


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
    context.user_data['candidates'] = get_candidates(telegram_id, genre, keyword)
    recommend_movie(telegram_id, query, context, True)


def get_candidate_from_context(candidates, user_context, exploit):
    actions = list(candidates)
    context_to_predict = [1] * len(user_context)
    if len(user_context) == 0:
        exploit = False
    X_context, y_context, r_context = [], [], []
    if exploit:
        X_context, y_context, r_context = get_all_context_binarized(actions, user_context)
    action = policy(actions, context_to_predict, X_context, y_context, r_context, exploit)
    state = 'no_context' if not X_context else ('exploit' if exploit else 'explore')
    return candidates[action], state


def recommend_movie(telegram_id, query, context, exploit=True):
    candidates = context.user_data.get('candidates')
    # TODO: If candidates < n discover more candidates
    candidates_id = list(candidates)

    if len(candidates) < 1:
        query.edit_message_text(text=f'\U0001F603 Desculpe! Não temos recommendações para os parâmetros informados.'
                                     f'\nDigite /start para informar novos parâmetros.')
        return

    context_ids = get_context_ids(telegram_id)
    context.user_data['context_to_predict'] = context_ids

    movie_bandit, state = get_candidate_from_context(candidates, context_ids, exploit)
    label = candidates_id.index(movie_bandit.get('_id'))

    query.edit_message_text(text=f'{movie_card(movie_bandit)}'
                                 f'\n\n\n<b>Avalie a recomendação:</b>\n',
                            reply_markup=feedback_markup, parse_mode=ParseMode.HTML, disable_web_page_preview=False)

    context.user_data['recommended'] = {'id': movie_bandit.get('_id'),
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
    if not recommended:
        return
    reward = int('feedback_liked' in feedback)
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
    # Get feedback in each 5 interactions
    if get_recommended_count(telegram_id) % 10 == 0:
        query.message.reply_text('Você ficou satisfeito com as primeiras recomendações?',
                                reply_markup=InlineKeyboardMarkup([
                                    [InlineKeyboardButton(text='\U0001F44D Sim', callback_data='extra_0_yes'),
                                     InlineKeyboardButton(text='\U0001F44E Não', callback_data='extra_0_no')]
                                ]))
    else:
        query.message.reply_text(text=f'\U0001F603 Obrigado pela sua avaliação!',
                                 reply_markup=after_feedback_markup)


def after_feedback_answer(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    if 'recommend_next' in query.data:
        query.edit_message_text(
            'Deseja ter recommendações baseadas no seu histórico ou deseja explorar diversificadas?',
            reply_markup=bandit_feedback_markup)
    elif 'recommend_end' in query.data:
        query.edit_message_text('\U0001F603 Obrigado!\nCaso queira uma nova recomendação digite ou pressione /start')


def bandit_answer(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    telegram_id = update.effective_user.id
    genre_id = int(context.user_data.get('iterative').get('genre'))
    keyword = context.user_data.get('iterative').get('keyword')
    if 'bandit_exploit' in query.data:
        context.user_data['candidates'] = None
        context.user_data['candidates'] = get_candidates(telegram_id, genre_id, keyword)
        recommend_movie(telegram_id, query, context, exploit=True)
    elif 'bandit_explore' in query.data:
        context.user_data['candidates'] = None
        context.user_data['candidates'] = get_candidates(telegram_id, genre_id, None)
        recommend_movie(telegram_id, query, context, exploit=False)
