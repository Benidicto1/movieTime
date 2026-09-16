package com.movietime.app.data.download

import android.content.Context


class DownloadRepository(
    context: Context
) {

    private val downloadManager =
        MovieDownloadManager(
            context.applicationContext
        )


    fun downloadMovie(
        movieId: Int,
        movieTitle: String,
        downloadUrl: String
    ): Long {

        return downloadManager.startDownload(
            movieId = movieId,
            movieTitle = movieTitle,
            downloadUrl = downloadUrl
        )
    }


    fun getDownloadStatus(
        downloadId: Long
    ): DownloadStatus {

        return downloadManager.getStatus(
            downloadId
        )
    }


    fun getDownloadProgress(
        downloadId: Long
    ): Int {

        return downloadManager.getProgress(
            downloadId
        )
    }


    fun cancelDownload(
        downloadId: Long
    ): Int {

        return downloadManager.cancelDownload(
            downloadId
        )
    }


    fun removeDownload(
        downloadId: Long
    ): Int {

        return downloadManager.removeDownload(
            downloadId
        )
    }


    fun getLocalUri(
        downloadId: Long
    ) = downloadManager.getLocalUri(
        downloadId
    )
}