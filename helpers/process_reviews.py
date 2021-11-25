import pandas as pd
import threading

from database import save_round


def get_tmdb_ids():
    movies = pd.read_csv("../movie_data/movies_in_2016.csv", lineterminator='\n')
    map_dict = dict(zip(movies['movieId'], movies['tmdbId']))

    reviews = pd.read_csv("../movie_data/reviews_movies_in_2016.csv")
    users = reviews.groupby(reviews.userId)
    user_ids = reviews[['userId']].drop_duplicates()

    for idx, row in user_ids.iterrows():
        user = users.get_group(row['userId'])
        user_reviews = convert_user_data(user, map_dict)
        add_user_round_to_db(user_reviews)


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


def get_movies_after(year=2000):
    movies = pd.read_csv("../movie_data/movie_details_complete.csv", lineterminator='\n')
    movies_2000 = movies[movies['release_date'] > year]
    movies_2000.to_csv("../movie_data/movie_details_after_2000.csv", index=False)


def get_movie_id():
    links = pd.read_csv("../movie_data/links.csv", dtype=str)
    by_tmdb = pd.read_csv("../movie_data/remove_by_tmdbId.csv", dtype=str)
    movie_id = links.loc[links['tmdbId'].isin(by_tmdb['tmdbId'].tolist())]
    movie_id = movie_id[['movieId']]
    movie_id.to_csv("../movie_data/remove_by_movieId2.csv", index=False)


def remove_deleted_movies():
    reviews = pd.read_csv("../movie_data/ratings.csv",
                          dtype={'userId': str, 'movieId': str, 'rating': str, 'timestamp': int})

    by_id = pd.read_csv("../movie_data/remove_by_movieId.csv", dtype=str)
    by_tmdb = pd.read_csv("../movie_data/remove_by_movieId2.csv", dtype=str)
    removed = pd.concat([by_id, by_tmdb], ignore_index=True)
    # Fri Jan 01 2010 00:00:00 GMT+0000 == 1262304000
    reviews = reviews[~reviews['movieId'].isin(removed['movieId'].tolist())]
    reviews = reviews[reviews['timestamp'] > 1262304000]

    movies_2000 = pd.read_csv("../movie_data/movie_details_after_2000.csv", lineterminator='\n', dtype=str)
    reviews = reviews[reviews['movieId'].isin(movies_2000['movieId'].tolist())]

    reviews.to_csv("../movie_data/ratings_complete.csv", index=False)


def get_reviews_by_movie_year(year):
    reviews = pd.read_csv("../movie_data/ratings_after_2010.csv",
                          dtype={'userId': str, 'movieId': int, 'rating': str, 'timestamp': int})

    movies = pd.read_csv("../movie_data/movie_details_after_2000.csv", lineterminator='\n',
                         dtype={'release_date': int, 'movieId': int})

    movies_by_year = movies[movies['release_date'] == year]

    reviews_by_year = reviews[reviews['movieId'].isin(movies_by_year['movieId'])]

    reviews_by_year.to_csv(f"../movie_data/reviews_movies_in_{year}.csv", index=False)
    movies_by_year.to_csv(f"../movie_data/movies_in_{year}.csv", index=False)


if __name__ == "__main__":
    try:
        get_tmdb_ids()
        # get_reviews_by_movie_year(2016)
        pass
    except Exception as error:
        raise error
