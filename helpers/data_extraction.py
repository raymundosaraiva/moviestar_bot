import csv
import pandas as pd
import threading

from database import save_movie
from helpers.movie_helper import get_one_movie_resource_pt, get_one_movie_resource_en


def merge_links_movies():
    # First we merge links and movies to have access to external TMDB API
    links = pd.read_csv("../movie_data/links.csv", dtype=str)
    movies = pd.read_csv("../movie_data/movies.csv", dtype=str)
    result = pd.merge(links, movies, how="inner")
    # There are 107 missing tmdbIds and we need to drop those movies
    na = result[result['tmdbId'].isna()]
    na[['movieId']].to_csv("../movie_data/remove_by_movieId.csv", index=False)
    result = result.dropna()
    # We are dropping 5061 movies with genre '(no genres listed)'
    no_genres_index = result[result['genres'] == '(no genres listed)'].index

    no_genre = result[result['genres'] == '(no genres listed)']
    not_found = pd.read_csv("../movie_data/movies_not_found.csv", dtype=str)
    removed = pd.concat([no_genre[['tmdbId']], not_found], ignore_index=True)
    removed.to_csv("../movie_data/remove_by_tmdbId.csv", index=False)

    result.drop(no_genres_index, inplace=True)
    result.to_csv("../movie_data/dataset.csv", index=False)


def check_missing_movies():
    complete = pd.read_csv("../movie_data/movie_details_complete.csv", dtype=str, lineterminator='\n')[['tmdbId']]
    dataset = pd.read_csv("../movie_data/movie_details_1.csv", dtype=str)[['tmdbId']]
    # not_found = pd.read_csv("../movie_data/movies_not_found.csv", dtype=str)
    missing1 = pd.concat([dataset, complete]).drop_duplicates(keep=False)
    # missing2 = pd.concat([not_found, missing1]).drop_duplicates(keep=False)
    missing1.to_csv("../movie_data/missing_on_count.csv", index=False)


def merge_detail_files():
    files = []
    for i in range(1, 59):
        file = pd.read_csv(f"../movie_details/movie_details_{i}.csv", dtype=str)
        files.append(file)
    missing = pd.read_csv(f"../movie_details/movie_details_missing.csv", dtype=str)
    files.append(missing)
    result = pd.concat(files, ignore_index=True)
    # result[['movieId', 'tmdbId']].to_csv("../movie_data/movie_details_tmdbids.csv", index=False)
    result.to_csv("../movie_data/movie_details.csv", index=False)


def get_missing_movies():
    details = pd.read_csv(f"../movie_data/movie_details_tmdbids.csv",  dtype=str)
    dataset = pd.read_csv("../movie_data/dataset.csv", dtype=str)
    movie_details = details[['movieId', 'tmdbId']]
    all_movies = dataset[['movieId', 'tmdbId']]
    missing = pd.concat([all_movies, movie_details]).drop_duplicates(keep=False)
    missing.to_csv("../movie_details/missing.csv", index=False)


def get_movie_details(start, end, num):
    print(f"----Thread {num}: starting")
    with open('../movie_data/dataset.csv', mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        with open(f'../movie_data/movie_details_{num}.csv', mode='w') as csv_file_write:
            fieldnames = ['movieId', 'tmdbId', 'title', 'release_date', 'genres', 'overview', 'popularity',
                          'runtime', 'tagline', 'vote_average', 'vote_count', 'original_language', 'backdrop_path',
                          'poster_path']
            writer = csv.DictWriter(csv_file_write, fieldnames=fieldnames)
            writer.writeheader()
            index = 0
            for row in csv_reader:
                index += 1
                if not (start <= index <= end):
                    continue
                tmdb_id = row['tmdbId']
                movie = get_one_movie_resource_pt(tmdb_id)
                if movie.get('overview') == '':
                    # If do not have in PT get in EN
                    movie = get_one_movie_resource_en(tmdb_id)
                if movie.get('status_code'):
                    print(f'#### ------------------ Removed movie #{row["movieId"]}')
                    continue
                writer.writerow({'movieId': row['movieId'],
                                 'tmdbId': tmdb_id,
                                 'title': movie['title'],
                                 'release_date': movie['release_date'].split('-')[0],
                                 'genres': '|'.join([genre['name'] for genre in movie['genres']]),
                                 'overview': movie['overview'],
                                 'popularity': movie['popularity'],
                                 'runtime': movie['runtime'],
                                 'tagline': movie['tagline'],
                                 'vote_average': movie['vote_average'],
                                 'vote_count': movie['vote_count'],
                                 'original_language': movie['original_language'],
                                 'backdrop_path': movie['backdrop_path'],
                                 'poster_path': movie['poster_path']})
    print(f"$----Thread {num}: finishing")


def get_missing():
    with open('../movie_data/missing.csv', mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        with open(f'../movie_details/movie_details_missing.csv', mode='w') as csv_file_write:
            fieldnames = ['movieId', 'tmdbId', 'title', 'release_date', 'genres', 'overview', 'popularity',
                          'runtime', 'tagline', 'vote_average', 'vote_count', 'original_language', 'backdrop_path',
                          'poster_path']
            writer = csv.DictWriter(csv_file_write, fieldnames=fieldnames)
            writer.writeheader()
            not_found = []
            for row in csv_reader:
                tmdb_id = row['tmdbId']
                movie = get_one_movie_resource_pt(tmdb_id)
                if movie.get('overview') == '':
                    # If do not have in PT get in EN
                    movie = get_one_movie_resource_en(tmdb_id)
                if movie.get('status_code'):
                    not_found.append(row['tmdbId'])
                    print(f'#### ------------------ Removed movie #{row["movieId"]}')
                    continue
                writer.writerow({'movieId': row['movieId'],
                                 'tmdbId': tmdb_id,
                                 'title': movie['title'],
                                 'release_date': movie['release_date'].split('-')[0],
                                 'genres': '|'.join([genre['name'] for genre in movie['genres']]),
                                 'overview': movie['overview'],
                                 'popularity': movie['popularity'],
                                 'runtime': movie['runtime'],
                                 'tagline': movie['tagline'],
                                 'vote_average': movie['vote_average'],
                                 'vote_count': movie['vote_count'],
                                 'original_language': movie['original_language'],
                                 'backdrop_path': movie['backdrop_path'],
                                 'poster_path': movie['poster_path']})
            print(f'Not found on TMDB: {len(not_found)}')


def run_parallel():
    step = 1000
    file_seq = 0
    for val in range(1, 57236, step):
        start = val
        end = val + (step - 1)
        file_seq += 1
        # get_movie_details(start, end, file_seq)
        threading.Thread(target=get_movie_details, args=(start, end, file_seq)).start()


def load_movies_to_db():
    movies_df = pd.read_csv("../movie_data/movie_details_1.csv", lineterminator='\n', dtype=str)
    movies_df = movies_df.rename(columns={'tmdbId': '_id', 'movieId': 'ml_id'})
    movies_dict = movies_df.to_dict('records')
    for movie in movies_dict:
        save_movie(movie)
        print(f'Saved movie {movie["_id"]}')


if __name__ == "__main__":
    try:
        merge_links_movies()
        # check_missing_movies()
        # get_missing()
        # run_parallel()
    except Exception as error:
        raise error
