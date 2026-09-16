package com.movietime.app.data.local

data class OfflineMovie(
    val id: Int,
    val title: String,
    val description: String,
    val posterPath: String?,
    val videoPath: String,
    val downloadedAt: Long
)