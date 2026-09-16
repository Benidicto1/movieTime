package com.movietime.app.data.model

data class DownloadedMovie(
    val movieId: Int,
    val title: String,
    val description: String,
    val posterUrl: String?,
    val localFilePath: String,
    val downloadedAt: Long
)