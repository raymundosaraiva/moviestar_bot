import requests
from requests.exceptions import HTTPError, ConnectionError
from bot import CONFIG


def save_user_info(telegram_id, name, username):
    if not CONFIG.DB_SAVE:
        return True
    try:
        response = requests.get(url=f'{CONFIG.DB_HOST}/telegram_user_info',
                                params={'telegram_id': telegram_id,
                                        'name': name,
                                        'username': username})
        if response.status_code < 300:
            print(f'Success on save_user_info() [{telegram_id}]')
            return response
        else:
            print(f'Error<{response.status_code}> on save_user_info() [{telegram_id}] - {response.reason}')
    except HTTPError as error:
        print(f'On save_user_info() [{telegram_id}] - HTTP error occurred: {error}')
    except ConnectionError as error:
        print(f'On save_user_info() [{telegram_id}] - CONNECTION ERROR error occurred: {error}')
    else:
        print(f'ERROR on save_user_info() [{telegram_id}]')


def save_user_chat(telegram_id, user_input, wit_output, bot_output, feedback=''):
    if not CONFIG.DB_SAVE:
        return True
    try:
        response = requests.get(url=f'{CONFIG.DB_HOST}/telegram_chat_history',
                                params={'telegram_id': telegram_id,
                                        'user_input': user_input,
                                        'wit_output': wit_output,
                                        'bot_output': bot_output,
                                        'feedback': feedback})
        if response.status_code < 300:
            print(f'Success on save_user_chat() [{telegram_id}]')
            return response
        else:
            print(f'Error<{response.status_code}> on save_user_chat() [{telegram_id}] - {response.reason}')
    except HTTPError as error:
        print(f'On save_user_chat() [{telegram_id}] - HTTP error occurred: {error}')
    except ConnectionError as error:
        print(f'On save_user_chat() [{telegram_id}] - CONNECTION ERROR error occurred: {error}')
    else:
        print(f'ERROR on save_user_chat() [{telegram_id}]')


def update_feedback_on_db(telegram_id, source, movie_id, movie_title='', feedback=''):
    if not CONFIG.DB_SAVE:
        return True
    try:
        response = requests.get(url=f'{CONFIG.DB_HOST}/update_recommendation',
                                params={'telegram_id': telegram_id,
                                        'source': source,
                                        'movie_id': movie_id,
                                        'movie_title': movie_title,
                                        'feedback': feedback})
        if response.status_code < 300:
            print(f'Success on update_feedback() [{telegram_id}]')
            return response
        else:
            print(f'Error<{response.status_code}> on update_feedback() [{telegram_id}] - {response.reason}')
    except HTTPError as error:
        print(f'On update_feedback() [{telegram_id}] - HTTP error occurred: {error}')
    except ConnectionError as error:
        print(f'On update_feedback() [{telegram_id}] - CONNECTION ERROR error occurred: {error}')
    else:
        print(f'ERROR on update_feedback() [{telegram_id}]')
