package com.movietime.app.data.repository

import com.movietime.app.data.model.Movie
import com.movietime.app.data.model.MovieStreamResponse
import com.movietime.app.data.remote.MovieApiService

class MovieRepository(
    private val movieApiService: MovieApiService
) {

    /**
     * Retrieves the movie catalog from the backend.
     *
     * The backend remains responsible for filtering,
     * searching and ordering the movie catalog.
     */
    suspend fun getMovies(
        search: String? = null,
        genre: String? = null,
        ordering: String? = null,
        page: Int? = null
    ): Result<List<Movie>> {
        return try {
            val movies = movieApiService.getMovies(
                search = search,
                genre = genre,
                ordering = ordering,
                page = page
            )

            Result.success(movies)
        } catch (exception: Exception) {
            Result.failure(exception)
        }
    }

    /**
     * Retrieves details for a single movie.
     */
    suspend fun getMovie(
        movieId: Int
    ): Result<Movie> {

        if (movieId <= 0) {
            return Result.failure(
                IllegalArgumentException("Movie ID must be greater than zero.")
            )
        }

        return try {
            val movie = movieApiService.getMovie(movieId)

            Result.success(movie)
        } catch (exception: Exception) {
            Result.failure(exception)
        }
    }

    /**
     * Requests a streaming URL from the backend.
     *
     * Chapter 73 security rule:
     *
     * Android does NOT determine whether the user owns
     * the movie or has an active subscription.
     *
     * Django performs the authorization check and only
     * returns a stream URL when access is permitted.
     */
    suspend fun getMovieStream(
        movieId: Int
    ): Result<MovieStreamResponse> {

        if (movieId <= 0) {
            return Result.failure(
                IllegalArgumentException("Movie ID must be greater than zero.")
            )
        }

        return try {
            val streamResponse =
                movieApiService.getMovieStream(movieId)

            Result.success(streamResponse)
        } catch (exception: Exception) {
            Result.failure(exception)
        }
    }

    /**
     * Searches the movie catalog.
     */
    suspend fun searchMovies(
        query: String,
        page: Int? = null
    ): Result<List<Movie>> {

        val normalizedQuery = query.trim()

        if (normalizedQuery.isEmpty()) {
            return getMovies(page = page)
        }

        return getMovies(
            search = normalizedQuery,
            page = page
        )
    }

    /**
     * Retrieves movies belonging to a genre.
     */
    suspend fun getMoviesByGenre(
        genre: String,
        page: Int? = null
    ): Result<List<Movie>> {

        val normalizedGenre = genre.trim()

        if (normalizedGenre.isEmpty()) {
            return Result.failure(
                IllegalArgumentException("Genre cannot be empty.")
            )
        }

        return getMovies(
            genre = normalizedGenre,
            page = page
        )
    }

    /**
     * Retrieves movies using a backend ordering value.
     *
     * Examples:
     *
     * "-created_at"
     * "title"
     * "-price"
     */
    suspend fun getMoviesOrdered(
        ordering: String,
        page: Int? = null
    ): Result<List<Movie>> {

        val normalizedOrdering = ordering.trim()

        if (normalizedOrdering.isEmpty()) {
            return Result.failure(
                IllegalArgumentException("Ordering cannot be empty.")
            )
        }

        return getMovies(
            ordering = normalizedOrdering,
            page = page
        )
    }
}