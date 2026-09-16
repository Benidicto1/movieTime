package com.movietime.app.data.download

import android.app.DownloadManager
import android.content.Context
import android.net.Uri
import android.os.Environment

class MovieDownloadManager(
    context: Context
) {

    private val downloadManager =
        context.getSystemService(
            Context.DOWNLOAD_SERVICE
        ) as DownloadManager

    fun downloadMovie(
        downloadUrl: String,
        movieTitle: String
    ): Long {

        val fileName =
            createFileName(movieTitle)

        val request =
            DownloadManager.Request(
                Uri.parse(downloadUrl)
            )

        request.setTitle(
            movieTitle
        )

        request.setDescription(
            "Downloading MovieTime movie"
        )

        request.setNotificationVisibility(
            DownloadManager
                .Request
                .VISIBILITY_VISIBLE_NOTIFY_COMPLETED
        )

        request.setDestinationInExternalFilesDir(
            null,
            Environment.DIRECTORY_MOVIES,
            fileName
        )

        return downloadManager.enqueue(
            request
        )
    }

    private fun createFileName(
        movieTitle: String
    ): String {

        val safeTitle =
            movieTitle
                .replace(
                    Regex("[^a-zA-Z0-9._-]"),
                    "_"
                )

        return "$safeTitle.mp4"
    }
}