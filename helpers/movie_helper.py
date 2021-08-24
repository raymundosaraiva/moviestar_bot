import requests
import datetime

from config import DefaultConfig

CONFIG = DefaultConfig()

imgURL = 'https://image.tmdb.org/t/p/'
posterURL = f'{imgURL}w342'
backdropURL = f'{imgURL}w300'

MOVIE_CARD_INDEXES = {'title',
                      'backdrop_path',
                      'overview',
                      'release_date',
                      'vote_average'}

IMG_TYPE = ((1, 'backdrops'), (2, 'posters'))

LANGUAGES = ((1, 'en-US'), (2, 'pt-BR'),)


def get_movie_card_data(movie, extra=True):
    movie_data = {}
    movie = update_movie_info(movie)
    for key in MOVIE_CARD_INDEXES:
        movie_data.update({key: movie.get(key, '')})
    if extra:
        movie_data.update(get_movie_card_extra(movie))
    return movie_data


def update_movie_info(movie):
    movie = update_movie_image_path(movie)
    movie = convert_movie_dates(movie)
    return movie


def get_movie_card_extra(movie):
    movie_id = movie.get('id')
    backdrop = movie.get("backdrop_path")
    poster = movie.get("poster_path")
    trailer = get_trailer_url(movie_id)
    extra_data = {'detailsUrl': f"https://www.themoviedb.org/movie/{movie_id}?language={CONFIG.TMDB_LANGUAGE}"}
    if trailer:
        extra_data['trailerUrl'] = trailer
    if backdrop:
        extra_data['backdropUrl'] = backdrop
    if poster:
        extra_data['posterUrl'] = poster
    return extra_data


def update_movie_image_path(movie):
    movie['backdrop_path'] = f"{backdropURL}{movie['backdrop_path']}"
    movie['poster_path'] = f"{posterURL}{movie['poster_path']}"
    return movie


def get_resource(movie_num, url='', page=1):
    url = f"{CONFIG.TMDB_URL}movie/{str(movie_num)}{url}?api_key={CONFIG.TMDB_KEY}" \
          f"&page={str(page)}&language={CONFIG.TMDB_LANGUAGE}"
    response = requests.get(url)
    return response.json()


def get_movies_resource(movie_num, url='', page=1):
    response = get_resource(movie_num, url, page)
    if 'results' in response:
        response = response['results']
    return response


def get_one_movie_resource(movie_num):
    movie = get_resource(movie_num)
    return movie


def get_similar_resources(movie_id):
    return get_movies_resource(movie_id, '/similar')


def get_top_rated_resources(page=1):
    return get_movies_resource('', 'top_rated', page)


def get_popular_resources(page=1):
    return get_movies_resource('', 'popular', page)


def get_now_playing_resources(page=1):
    return get_movies_resource('', 'now_playing', page)


def get_upcoming_resources(page=1):
    return get_movies_resource('', 'upcoming', page)


def get_trailer_url(movie_id):
    url = f"{CONFIG.TMDB_URL}movie/{movie_id}/videos?api_key={CONFIG.TMDB_KEY}&language={CONFIG.TMDB_LANGUAGE}"
    response = requests.get(url)
    trailer_url = None
    if response.status_code == 200 and len(response.json()['results']) > 0:
        key = response.json()['results'][0].get('key')
        trailer_url = f"https://www.youtube.com/watch?v={key}"
    return trailer_url


def convert_movie_dates(movie):
    if len(movie['release_date']) > 4:
        date_time_obj = datetime.datetime.strptime(movie['release_date'], '%Y-%m-%d')
        movie['release_date'] = date_time_obj.strftime('%Y')
    return movie


def search(search_type, query, page=1):
    url = f"{CONFIG.TMDB_URL}search/{search_type}?api_key={CONFIG.TMDB_KEY}&page={str(page)}" \
          f"&language={CONFIG.TMDB_LANGUAGE}" \
          f"&query={query}"
    response = requests.get(url).json()['results']
    # TODO: Handle errors
    return response


def search_movie(query, page=1):
    return search('movie', query, page)


def search_keyword(query, page=1):
    return search('keyword', query, page)


def discover(genres, keywords, page=1):
    # genre and keyword IDs, comma separated
    url = f"{CONFIG.TMDB_URL}discover/movie?api_key={CONFIG.TMDB_KEY}&page={str(page)}" \
          f"&language={CONFIG.TMDB_LANGUAGE}&sort_by=popularity.desc" \
          f"&with_genres={genres}&with_keywords={keywords}"
    response = requests.get(url).json()['results']
    # TODO: Handle errors
    return response


def movie_card(movie):
    if movie:
        movie_data = get_movie_card_data(movie)
        movie_message = f"\U0001F3AC<b>{movie_data.get('title')} ({movie_data.get('release_date')})</b>" \
                        f"\n\n{movie_data.get('overview')} " \
                        f"<a href='{movie_data.get('detailsUrl')}'>...Mais detalhes</a>" \
                        f"\n\n<a href='{movie_data.get('posterUrl')}'>Acessar Poster</a>"
        if movie_data.get('trailerUrl'):
            movie_message += f"\n<a href='{movie_data.get('trailerUrl')}'>Acessar Trailer</a>"
        return movie_message
    else:
        return "Ops. Desculpe. Ocorreu um erro ao retorar o filme!"


def get_code(resp):
    return resp.split('_', 1)[1]