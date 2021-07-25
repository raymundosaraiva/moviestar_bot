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
    DB_HOST = os.environ.get("DB_HOST", "http://localhost:8000")
    DB_SAVE = os.environ.get("DB_SAVE", False)



