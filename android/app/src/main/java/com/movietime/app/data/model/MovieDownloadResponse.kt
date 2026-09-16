package com.movietime.app.data.model

data class MovieDownloadResponse(
    val movieId: Int,
    val downloadUrl: String,
    val expiresAt: String?
)