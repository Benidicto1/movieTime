class MovieStorageService:

    @staticmethod
    def get_movie_key(movie):
        return movie.media.movie_storage_key

    @staticmethod
    def validate_movie_key(movie):
        key = MovieStorageService.get_movie_key(movie)

        if not key:
            raise ValueError(
                "Movie does not have a storage key."
            )

        return key

    @staticmethod
    def generate_signed_url(
        *,
        file_key,
        expires_in=600,
    ):
        raise NotImplementedError(
            "Storage provider implementation "
            "has not been configured."
        )