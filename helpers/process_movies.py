import pandas as pd
import threading

from helpers.keywords import keywords_list
from helpers.movie_helper import get_movie_keywords


def get_keywords():
    movies = pd.read_csv("../movie_data/movies_sample.csv", lineterminator='\n')
    movie_groups = movies.groupby(movies.release_date)
    years = movies[['release_date']].drop_duplicates()

    for idx, row in years.iterrows():
        movies_by_year = movie_groups.get_group(row['release_date'])
        add_keywords(movies_by_year)
        # threading.Thread(target=add_keywords, args=(movies_by_year)).start()


def add_keywords(movies):
    movies_updated = pd.DataFrame()
    for idx, movie in movies.iterrows():
        tmdb_id = movie['_id']
        keywords = get_movie_keywords(tmdb_id)
        movie['keywords'] = keywords
        movies_updated = movies_updated.append(movie, ignore_index=True)
    movies_updated.to_csv("../movie_details/1995.csv", index=False)


def get_unique_keywords():
    keywords = set()
    for genre in keywords_list:
        for keyword in keywords_list[genre]:
            keywords.add(keywords_list[genre][keyword])
    result = list(keywords)


if __name__ == "__main__":
    try:
        get_keywords()
    except Exception as error:
        raise error