from helpers.genres import genres


class Features:

    def __init__(self, genre_id):
        feature_array = list()
        for genre in genres:
            has_genre = int(genre.get('id') == genre_id)
            feature_array.append(has_genre)
        self.features = feature_array

    def get(self):
        return self.features
