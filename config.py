#  MIT License (MIT) (c) 2021
#  This software was created by ICMC Recommendation Group
#  Supervisor: Raymundo Saraiva
#

import os


class DefaultConfig:
    """ Bot Configuration """

    # TELEGRAM API
    TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
    WEBHOOK_PORT = os.environ.get("WEBHOOK_PORT", 8443)
    APP_NAME = os.environ.get("APP_NAME", "")

    # TMDB API
    TMDB_KEY = os.environ.get("TMDB_KEY", "")
    TMDB_URL = os.environ.get("TMDB_URL", "https://api.themoviedb.org/3/")
    TMDB_LANGUAGE = os.environ.get("TMDB_LANGUAGE", "pt-BR")

    # DB API
    DB_HOST = os.environ.get("MONGODB_URI", "localhost:27017")
    DB_SAVE = os.environ.get("DB_SAVE", True)

    # BANDIT CONFIGS
    # N x 20 movies in the list
    BANDIT_NEGATIVE_FEEDBACK = os.environ.get("BANDIT_N_LIST", 3)
    BANDIT_OPTION = os.environ.get("BANDIT_OPTION", 3)



