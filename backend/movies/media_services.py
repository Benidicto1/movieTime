from .storage_services import (
    MovieStorageService,
)

class MediaDeliveryService:

    @staticmethod
    def get_stream_url(
        *,
        movie,
        user,
    ):
        storage_key = (
            MovieStorageService.validate_movie_key(
                movie
            )
        )

        return MovieStorageService.generate_signed_url(
            file_key=storage_key,
        )