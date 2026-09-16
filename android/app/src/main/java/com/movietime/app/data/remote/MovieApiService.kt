package com.movietime.app.data.remote

import com.movietime.app.data.model.Movie
import com.movietime.app.data.model.MovieStreamResponse
import retrofit2.http.GET
import retrofit2.http.Path
import retrofit2.http.Query

interface MovieApiService {

    /**
     * Get the movie catalog.
     *
     * GET /api/v1/movies/
     *
     * Example:
     * /api/v1/movies/
     * /api/v1/movies/?search=avatar
     * /api/v1/movies/?genre=action
     */
    @GET("api/v1/movies/")
    suspend fun getMovies(
        @Query("search") search: String? = null,
        @Query("genre") genre: String? = null,
        @Query("ordering") ordering: String? = null,
        @Query("page") page: Int? = null
    ): List<Movie>

    /**
     * Get details for a single movie.
     *
     * GET /api/v1/movies/{movieId}/
     */
    @GET("api/v1/movies/{movieId}/")
    suspend fun getMovie(
        @Path("movieId") movieId: Int
    ): Movie

    /**
     * Request authorization to stream a movie.
     *
     * GET /api/v1/movies/{movieId}/stream/
     *
     * The backend determines whether the authenticated
     * user is allowed to stream the movie.
     */
    @GET("api/v1/movies/{movieId}/stream/")
    suspend fun getMovieStream(
        @Path("movieId") movieId: Int
    ): MovieStreamResponse
}