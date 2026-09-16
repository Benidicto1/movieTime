package com.movietime.app.data.download

import android.app.DownloadManager
import android.content.Context
import android.database.Cursor
import android.net.Uri
import android.os.Environment


class MovieDownloadManager(
    private val context: Context
) {

    private val downloadManager =
        context.getSystemService(
            Context.DOWNLOAD_SERVICE
        ) as DownloadManager


    fun startDownload(
        movieId: Int,
        movieTitle: String,
        downloadUrl: String
    ): Long {

        val request =
            DownloadManager.Request(
                Uri.parse(downloadUrl)
            )


        request.setTitle(
            movieTitle
        )


        request.setDescription(
            "Downloading $movieTitle"
        )


        request.setNotificationVisibility(
            DownloadManager.Request
                .VISIBILITY_VISIBLE_NOTIFY_COMPLETED
        )


        request.setAllowedOverMetered(
            true
        )


        request.setAllowedOverRoaming(
            false
        )


        request.setDestinationInExternalPublicDir(
            Environment.DIRECTORY_MOVIES,
            "MovieTime/$movieId.mp4"
        )


        return downloadManager.enqueue(
            request
        )
    }


    fun getStatus(
        downloadId: Long
    ): DownloadStatus {

        val query =
            DownloadManager.Query()
                .setFilterById(downloadId)


        val cursor =
            downloadManager.query(query)


        cursor.use {

            if (!it.moveToFirst()) {

                return DownloadStatus.NOT_FOUND
            }


            val statusIndex =
                it.getColumnIndex(
                    DownloadManager.COLUMN_STATUS
                )


            if (statusIndex == -1) {

                return DownloadStatus.NOT_FOUND
            }


            return when (
                it.getInt(statusIndex)
            ) {

                DownloadManager.STATUS_PENDING ->
                    DownloadStatus.PENDING

                DownloadManager.STATUS_RUNNING ->
                    DownloadStatus.DOWNLOADING

                DownloadManager.STATUS_PAUSED ->
                    DownloadStatus.PAUSED

                DownloadManager.STATUS_SUCCESSFUL ->
                    DownloadStatus.COMPLETED

                DownloadManager.STATUS_FAILED ->
                    DownloadStatus.FAILED

                else ->
                    DownloadStatus.UNKNOWN
            }
        }
    }


    fun getProgress(
        downloadId: Long
    ): Int {

        val query =
            DownloadManager.Query()
                .setFilterById(downloadId)


        val cursor =
            downloadManager.query(query)


        cursor.use {

            if (!it.moveToFirst()) {

                return 0
            }


            val downloadedIndex =
                it.getColumnIndex(
                    DownloadManager.COLUMN_BYTES_DOWNLOADED_SO_FAR
                )


            val totalIndex =
                it.getColumnIndex(
                    DownloadManager.COLUMN_TOTAL_SIZE_BYTES
                )


            if (
                downloadedIndex == -1 ||
                totalIndex == -1
            ) {

                return 0
            }


            val downloaded =
                it.getLong(
                    downloadedIndex
                )


            val total =
                it.getLong(
                    totalIndex
                )


            if (total <= 0L) {

                return 0
            }


            return (
                    downloaded * 100L / total
                    ).toInt()
        }
    }


    fun cancelDownload(
        downloadId: Long
    ): Int {

        return downloadManager.remove(
            downloadId
        )
    }


    fun removeDownload(
        downloadId: Long
    ): Int {

        return downloadManager.remove(
            downloadId
        )
    }


    fun getLocalUri(
        downloadId: Long
    ): Uri? {

        val query =
            DownloadManager.Query()
                .setFilterById(downloadId)


        val cursor =
            downloadManager.query(query)


        cursor.use {

            if (!it.moveToFirst()) {

                return null
            }


            val statusIndex =
                it.getColumnIndex(
                    DownloadManager.COLUMN_STATUS
                )


            if (statusIndex == -1) {

                return null
            }


            val status =
                it.getInt(statusIndex)


            if (
                status !=
                DownloadManager.STATUS_SUCCESSFUL
            ) {

                return null
            }


            val uriIndex =
                it.getColumnIndex(
                    DownloadManager.COLUMN_LOCAL_URI
                )


            if (uriIndex == -1) {

                return null
            }


            val uri =
                it.getString(uriIndex)


            return if (
                uri.isNullOrBlank()
            ) {
                null
            } else {
                Uri.parse(uri)
            }
        }
    }
}


enum class DownloadStatus {

    PENDING,

    DOWNLOADING,

    PAUSED,

    COMPLETED,

    FAILED,

    NOT_FOUND,

    UNKNOWN
}