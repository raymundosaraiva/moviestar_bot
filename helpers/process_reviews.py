import pandas as pd
import threading

from database import save_round

movies = pd.read_csv("../data/movie_details_after_2010.csv", lineterminator='\n')
ratings = pd.read_csv("../data/simple_ratings_after_2010.csv")

map_dict = dict(zip(movies['movieId'], movies['tmdbId']))
users = ratings.groupby(ratings.userId)
user_ids = ratings[['userId']].drop_duplicates()
pass

def process_users():
    for idx, row in user_ids.iterrows():
        user_id = row['userId'].item()
        process_user(user_id)
        # threading.Thread(target=process_user, args=(user_id,)).start()


def process_user(user_id):
    print(f"User = {user_id}")
    user = users.get_group(user_id)
    user_reviews = convert_user_data(user, map_dict)
    add_user_round_to_db(user_reviews)


def filter_ratings_by_movies():
    movies = pd.read_csv("../data/movie_details_after_2010.csv", lineterminator='\n')['movieId']
    ratings = pd.read_csv("../movie_data/ratings_after_2010.csv",
                          dtype={'userId': int, 'movieId': int, 'rating': float, 'timestamp': int})
    # Only get ratings for selected movies
    ratings = ratings[ratings['movieId'].isin(movies.tolist())]
    ratings.to_csv("../data/simple_ratings_after_2010.csv", index=False)


def convert_user_data(user, map_dict):
    user['tmdbId'] = user['movieId']
    user = user.replace({'tmdbId': map_dict})
    user = user.sort_values('timestamp')
    user['rating'] = user['rating'].mask(user['rating'] < 3, 0)
    user['rating'] = user['rating'].mask(user['rating'] >= 3, 1)
    return user


def add_user_round_to_db(user):
    user_context = []
    for idx, row in user.iterrows():
        reward, selected, userId = int(row['rating']), int(row['tmdbId']), int(row['userId'])
        save_round(userId, user_context, [], selected, reward)
        if reward == 1:
            user_context.append(selected)


if __name__ == "__main__":
    try:
        process_users()
    except Exception as error:
        raise error
