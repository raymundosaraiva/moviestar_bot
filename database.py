from bot import CONFIG
import datetime
from pymongo import MongoClient

client = MongoClient(CONFIG.DB_HOST)
db = client.movie_star


def has_user(telegram_id):
    users = db.users
    if users.find_one({'telegram_id': telegram_id}):
        return True
    else:
        return False


def update_user_last_access(telegram_id):
    if not CONFIG.DB_SAVE:
        return True

    users = db.users
    if users.find_one({'telegram_id': telegram_id}):
        query = {'telegram_id': telegram_id}
        last_access = {'$set': {'last_access': datetime.datetime.utcnow()}}
        users.update_one(query, last_access)
        return True


def create_user(telegram_id, name, username):
    if not CONFIG.DB_SAVE:
        return True

    users = db.users
    user = {'telegram_id': telegram_id,
            'name': name,
            'username': username,
            'created': datetime.datetime.utcnow(),
            'last_access': datetime.datetime.utcnow()
            }
    users.insert_one(user)
    return True


def save_user_info(telegram_id, info, value):
    if not CONFIG.DB_SAVE:
        return True

    users = db.users
    query = {'telegram_id': telegram_id}
    to_update = {'$set': {f'{info}': value}}
    users.update_one(query, to_update)
    return True


def user_has_info(telegram_id, info):
    users = db.users
    query = {'telegram_id': telegram_id}
    return users.find_one(query).get(info) or False


def save_experiment(experiment):
    if not CONFIG.DB_SAVE:
        return True

    experiments = db.experiments
    experiment['created'] = datetime.datetime.utcnow()
    experiments.insert_one(experiment)
    return True


def get_recommended(telegram_id):
    users = db.users
    recommended = users.find_one({'telegram_id': telegram_id}).get('recommended') or []
    return recommended


def update_user_column_array(telegram_id, movie_id, column):
    if not CONFIG.DB_SAVE:
        return True

    users = db.users
    users.find_one_and_update({'telegram_id': telegram_id},
                              {'$addToSet': {column: movie_id}}
                              )
    return True


def get_context_ids(telegram_id):
    users = db.users
    return users.find_one({'telegram_id': telegram_id}).get('selected') or []


def binarize_context(context_ids):
    rounds = db.rounds
    selected_all = [_round.get('selected') for _round in rounds.find()]
    context = [1 if i in context_ids else 0 for i in selected_all]
    return context


def get_all_context_binarized(candidates):
    rounds = db.rounds
    X, y, r = [], [], []
    for _round in rounds.find():
        if _round.get('selected') in candidates:
            X.append(binarize_context(_round.get('context')))
            y.append(candidates.index(_round.get('selected')))
            r.append(_round.get('reward'))
    return X, y, r


def save_round(telegram_id, context, actions, selected, reward):
    if not CONFIG.DB_SAVE:
        return True

    rounds = db.rounds
    this_round = {'telegram_id': telegram_id,
                  'context': context,
                  'actions': actions,
                  'selected': selected,
                  'reward': reward
                  }
    rounds.insert_one(this_round)
    return True


def save_error(telegram_id, message):
    if not CONFIG.DB_SAVE:
        return True

    errors = db.errors
    error = {'telegram_id': telegram_id,
             'message': message,
             'created': datetime.datetime.utcnow()
             }
    errors.insert_one(error)
    return True


def save_grade(telegram_id, grade):
    if not CONFIG.DB_SAVE:
        return True

    grades = db.grades
    data = {'telegram_id': telegram_id,
            'grade': grade,
            'created': datetime.datetime.utcnow()
            }
    grades.insert_one(data)
    return True


def save_review(telegram_id, review):
    if not CONFIG.DB_SAVE:
        return True

    reviews = db.reviews
    data = {'telegram_id': telegram_id,
            'review': review,
            'created': datetime.datetime.utcnow()
            }
    reviews.insert_one(data)
    return True
