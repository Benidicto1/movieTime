package com.movietime.app.ui.data

import com.movietime.app.data.model.Movie


val testMovies = listOf(

    Movie(
        id = 1,
        title = "Movie One",
        description = "An example MovieTime movie.",
        posterUrl = null,
        releaseDate = "2026-01-01",
        rating = 8.5
    ),

    Movie(
        id = 2,
        title = "Movie Two",
        description = "Another example MovieTime movie.",
        posterUrl = null,
        releaseDate = "2026-02-01",
        rating = 8.0
    ),

    Movie(
        id = 3,
        title = "Movie Three",
        description = "Another MovieTime title.",
        posterUrl = null,
        releaseDate = "2026-03-01",
        rating = 7.8
    )
)