package com.movietime.app.ui.screens

import androidx.compose.material3.Button
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import com.movietime.app.download.DownloadStatus

@Composable
fun DownloadButton(
    status: DownloadStatus,
    progress: Int,
    onClick: () -> Unit
) {

    when (status) {

        DownloadStatus.PENDING -> {

            Button(
                onClick = onClick
            ) {

                Text(
                    text = "Download"
                )
            }
        }

        DownloadStatus.DOWNLOADING -> {

            Button(
                onClick = {},
                enabled = false
            ) {

                Text(
                    text = "Downloading $progress%"
                )
            }
        }

        DownloadStatus.COMPLETED -> {

            Button(
                onClick = {},
                enabled = false
            ) {

                Text(
                    text = "Downloaded"
                )
            }
        }

        DownloadStatus.FAILED -> {

            Button(
                onClick = onClick
            ) {

                Text(
                    text = "Retry Download"
                )
            }
        }
    }
}