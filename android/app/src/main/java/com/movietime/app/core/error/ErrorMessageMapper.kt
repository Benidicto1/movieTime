package com.movietime.app.core.error


object ErrorMessageMapper {

    fun getMessage(
        error: MovieTimeError
    ): String {

        return when (error) {

            MovieTimeError.Network -> {
                "No internet connection. " +
                        "Please check your connection " +
                        "and try again."
            }

            MovieTimeError.Timeout -> {
                "The request timed out. " +
                        "Please try again."
            }

            MovieTimeError.Unauthorized -> {
                "Your session has expired. " +
                        "Please log in again."
            }

            MovieTimeError.Forbidden -> {
                "You do not have permission " +
                        "to perform this action."
            }

            MovieTimeError.NotFound -> {
                "The requested content could not " +
                        "be found."
            }

            MovieTimeError.Server -> {
                "MovieTime is temporarily " +
                        "unavailable. Please try again later."
            }

            MovieTimeError.Payment -> {
                "The payment could not be completed. " +
                        "Please try again."
            }

            MovieTimeError.Download -> {
                "The movie could not be downloaded. " +
                        "Please try again."
            }

            MovieTimeError.Unknown -> {
                "Something went wrong. " +
                        "Please try again."
            }
        }
    }
}
