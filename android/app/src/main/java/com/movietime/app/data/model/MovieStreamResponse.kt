package com.movietime.app.data.model

data class MovieStreamResponse(
    val movieId: Int,
    val streamUrl: String,
    val expiresAt: String?
)