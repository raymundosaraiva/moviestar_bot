import pandas as pd
import threading

from helpers.keywords import keywords_list
from helpers.movie_helper import get_movie_keywords
from database import save_movie

# movies = pd.read_csv("../data/movie_details_after_2010.csv", lineterminator='\n')
# movie_groups = movies.groupby(movies.release_date)


def get_keywords():
    years = movies[['release_date']].drop_duplicates()
    for idx, row in years.iterrows():
        year = row['release_date'].item()
        # add_keywords(year)
        threading.Thread(target=add_keywords, args=(year,)).start()


def add_keywords(year):
    movies_by_year = movie_groups.get_group(year)
    movies_updated = pd.DataFrame()
    for idx, movie in movies_by_year.iterrows():
        tmdb_id = movie['tmdbId']
        try:
            keywords = get_movie_keywords(tmdb_id)
        except Exception as error:
            print(f'## Error movie = {tmdb_id}')
            raise error
        movie['keywords'] = keywords
        movies_updated = movies_updated.append(movie, ignore_index=True)
        print(f'{year} - {tmdb_id}')
    movies_updated.to_csv(f"../data/movies_{year}_keywords.csv", index=False)


def get_movies_after(year=2010):
    movies = pd.read_csv("../movie_details/movie_details_after_2000.csv",
                         lineterminator='\n', dtype={'release_date': int})
    # Drop movies without defined genre or overview
    movies.dropna(inplace=True, subset=['genres', 'overview'])
    # Only consider movies with original language en or pt
    movies = movies[movies['original_language'].isin(['en', 'pt'])]
    # Filter Year
    movies = movies[movies['release_date'] >= year]
    # Drop movies with less than 2 ratings
    movies = movies[movies['vote_count'] >= 2]
    movies.to_csv(f"../movie_details/movie_details_after_{year}.csv", index=False)


def get_movie_id():
    links = pd.read_csv("../movie_data/links.csv", dtype=str)
    by_tmdb = pd.read_csv("../movie_data/remove_by_tmdbId.csv", dtype=str)
    movie_id = links.loc[links['tmdbId'].isin(by_tmdb['tmdbId'].tolist())]
    movie_id = movie_id[['movieId']]
    movie_id.to_csv("../movie_data/remove_by_movieId2.csv", index=False)


def load_movies_to_db():
    for year in range(2019, 2020):
        movies_df = pd.read_csv(f"../data/movies_{year}_keywords.csv", lineterminator='\n',
                                dtype={'tmdbId': int, 'release_date': int, 'movieId': str,}, keep_default_na=False)
        movies_df = movies_df.rename(columns={'tmdbId': '_id', 'movieId': 'ml_id'})
        movies_dict = movies_df.to_dict('records')
        for movie in movies_dict:
            save_movie(movie)
            print(f'Saved movie {movie["_id"]}')


if __name__ == "__main__":
    try:
        load_movies_to_db()
    except Exception as error:
        raise error