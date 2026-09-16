package com.movietime.app.download

data class DownloadItem(

    val movieId: Int,

    val movieTitle: String,

    val movieSlug: String,

    val filePath: String? = null,

    val progress: Int = 0,

    val status: DownloadStatus = DownloadStatus.PENDING,

    val isPermanent: Boolean = false
)