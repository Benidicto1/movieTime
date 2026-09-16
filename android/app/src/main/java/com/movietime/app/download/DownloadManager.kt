package com.movietime.app.download

class MovieDownloadManager {

    private val downloads =
        mutableMapOf<Int, DownloadItem>()

    fun getDownload(movieId: Int): DownloadItem? {

        return downloads[movieId]
    }

    fun startDownload(
        movieId: Int,
        movieTitle: String,
        movieSlug: String
    ) {

        downloads[movieId] = DownloadItem(

            movieId = movieId,

            movieTitle = movieTitle,

            movieSlug = movieSlug,

            progress = 0,

            status = DownloadStatus.PENDING,

            isPermanent = false
        )
    }

    fun updateProgress(
        movieId: Int,
        progress: Int
    ) {

        val current =
            downloads[movieId]
                ?: return

        downloads[movieId] =
            current.copy(
                progress = progress,
                status =
                    DownloadStatus.DOWNLOADING
            )
    }

    fun completeDownload(
        movieId: Int,
        filePath: String
    ) {

        val current =
            downloads[movieId]
                ?: return

        downloads[movieId] =
            current.copy(

                filePath = filePath,

                progress = 100,

                status =
                    DownloadStatus.COMPLETED,

                isPermanent = true
            )
    }

    fun failDownload(
        movieId: Int
    ) {

        val current =
            downloads[movieId]
                ?: return

        downloads[movieId] =
            current.copy(
                status = DownloadStatus.FAILED
            )
    }
}