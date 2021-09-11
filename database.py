from bot import CONFIG
import datetime
from pymongo import MongoClient

client = MongoClient(CONFIG.DB_HOST)
db = client.movie_star


def save_user_info(telegram_id, name, username):
    if not CONFIG.DB_SAVE:
        return True

    users = db.users
    if users.find_one({'telegram_id': telegram_id}):
        query = {'telegram_id': telegram_id}
        last_access = {'$set': {'last_access': datetime.datetime.utcnow()}}
        users.update_one(query, last_access)
        return True
    else:
        user = {'telegram_id': telegram_id,
                'name': name,
                'username': username,
                'created': datetime.datetime.utcnow()}
        users.insert_one(user)
        return True


def save_experiment(experiment):
    if not CONFIG.DB_SAVE:
        return True

    experiments = db.experiments
    experiment['created'] = datetime.datetime.utcnow()
    experiments.insert_one(experiment)
    return True


def save_recommended(bandit_id, baseline_id, telegram_id):
    if not CONFIG.DB_SAVE:
        return True

    users = db.users
    users.find_one_and_update({'telegram_id': telegram_id},
                              {'$addToSet': {'recommended': {'$each': [bandit_id, baseline_id]}}}
                              )
    return True


def get_recommended(telegram_id):
    users = db.users
    recommended = users.find_one({'telegram_id': telegram_id}).get('recommended')
    return recommended


def save_selected(telegram_id, movie_id):
    if not CONFIG.DB_SAVE:
        return True

    users = db.users
    users.find_one_and_update({'telegram_id': telegram_id},
                              {'$addToSet': {'selected': movie_id}}
                              )
    return True


def get_context_ids(telegram_id):
    users = db.users
    return users.find_one({'telegram_id': telegram_id}).get('selected')


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
