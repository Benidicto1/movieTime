package com.movietime.app.core.error


sealed class MovieTimeError {

    data object Network :
        MovieTimeError()

    data object Timeout :
        MovieTimeError()

    data object Unauthorized :
        MovieTimeError()

    data object Forbidden :
        MovieTimeError()

    data object NotFound :
        MovieTimeError()

    data object Server :
        MovieTimeError()

    data object Payment :
        MovieTimeError()

    data object Download :
        MovieTimeError()

    data object Unknown :
        MovieTimeError()
}
