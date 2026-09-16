package com.movietime.app.ui.details

import android.widget.Toast

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding

import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text

import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue

import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp

import androidx.lifecycle.viewmodel.compose.viewModel

import com.movietime.app.data.download.MovieDownloadManager


@Composable
fun MovieDetailsScreen(
    movieId: Int,
    onBackClick: () -> Unit,
    onWatchClick: (String) -> Unit,
    onDownloadClick: () -> Unit,

    streamViewModel: MovieStreamViewModel =
        viewModel(),

    downloadViewModel: MovieDownloadViewModel =
        viewModel(),

    ownershipViewModel: MovieOwnershipViewModel =
        viewModel()
) {


    // ==================================================
    // CONTEXT
    // ==================================================

    val context =
        LocalContext.current


    // ==================================================
    // STREAM STATE
    // ==================================================

    val streamUrl by
    streamViewModel
        .streamUrl
        .collectAsState()


    val isStreamLoading by
    streamViewModel
        .isLoading
        .collectAsState()


    val streamError by
    streamViewModel
        .errorMessage
        .collectAsState()


    // ==================================================
    // DOWNLOAD STATE
    // ==================================================

    val downloadUrl by
    downloadViewModel
        .downloadUrl
        .collectAsState()


    val isDownloadLoading by
    downloadViewModel
        .isLoading
        .collectAsState()


    val downloadError by
    downloadViewModel
        .errorMessage
        .collectAsState()


    // ==================================================
    // OWNERSHIP STATE
    // ==================================================

    val ownership by
    ownershipViewModel
        .ownership
        .collectAsState()


    val isOwnershipLoading by
    ownershipViewModel
        .isLoading
        .collectAsState()


    val ownershipError by
    ownershipViewModel
        .errorMessage
        .collectAsState()


    // ==================================================
    // LOAD OWNERSHIP
    // ==================================================

    LaunchedEffect(movieId) {

        ownershipViewModel
            .loadOwnership(
                movieId
            )
    }


    // ==================================================
    // OPEN VIDEO PLAYER
    // ==================================================

    LaunchedEffect(streamUrl) {

        if (streamUrl != null) {

            onWatchClick(
                streamUrl!!
            )

            streamViewModel
                .clearStream()
        }
    }


    // ==================================================
    // START DOWNLOAD
    // ==================================================

    LaunchedEffect(downloadUrl) {

        if (downloadUrl != null) {

            val downloadManager =
                MovieDownloadManager(
                    context
                )


            downloadManager.downloadMovie(
                downloadUrl = downloadUrl!!,
                movieTitle = "MovieTime Movie"
            )


            Toast.makeText(
                context,
                "Download started",
                Toast.LENGTH_SHORT
            ).show()


            downloadViewModel
                .clearDownloadUrl()
        }
    }


    // ==================================================
    // MAIN SCREEN
    // ==================================================

    Column(
        modifier =
            Modifier
                .fillMaxSize()
                .padding(16.dp),

        verticalArrangement =
            Arrangement.Top
    ) {


        // ==================================================
        // TITLE
        // ==================================================

        Text(
            text = "Movie Details",

            style =
                MaterialTheme
                    .typography
                    .headlineMedium
        )


        Spacer(
            modifier =
                Modifier.height(24.dp)
        )


        // ==================================================
        // OWNERSHIP CHECK
        // ==================================================

        if (isOwnershipLoading) {

            CircularProgressIndicator(
                modifier =
                    Modifier.height(
                        20.dp
                    ),

                strokeWidth = 2.dp
            )


            Spacer(
                modifier =
                    Modifier.height(8.dp)
            )


            Text(
                text =
                    "Checking ownership..."
            )
        }


        // ==================================================
        // OWNERSHIP RESULT
        // ==================================================

        ownership?.let { result ->

            if (result.owned) {

                Text(
                    text =
                        "OWNED",

                    style =
                        MaterialTheme
                            .typography
                            .titleMedium
                )


                Spacer(
                    modifier =
                        Modifier.height(4.dp)
                )


                Text(
                    text =
                        "You permanently own this movie."
                )

            } else {

                Text(
                    text =
                        "NOT OWNED",

                    style =
                        MaterialTheme
                            .typography
                            .titleMedium
                )


                Spacer(
                    modifier =
                        Modifier.height(4.dp)
                )


                Text(
                    text =
                        "Purchase this movie to receive permanent ownership."
                )
            }
        }


        // ==================================================
        // OWNERSHIP ERROR
        // ==================================================

        if (ownershipError != null) {

            Spacer(
                modifier =
                    Modifier.height(8.dp)
            )


            Text(
                text =
                    ownershipError
                        ?: "Unable to check ownership.",

                color =
                    MaterialTheme
                        .colorScheme
                        .error
            )
        }


        Spacer(
            modifier =
                Modifier.height(16.dp)
        )


        // ==================================================
        // STREAM ERROR
        // ==================================================

        if (streamError != null) {

            Text(
                text =
                    streamError
                        ?: "Unable to start streaming.",

                color =
                    MaterialTheme
                        .colorScheme
                        .error,

                modifier =
                    Modifier
                        .fillMaxWidth()
                        .padding(
                            bottom = 12.dp
                        )
            )
        }


        // ==================================================
        // DOWNLOAD ERROR
        // ==================================================

        if (downloadError != null) {

            Text(
                text =
                    downloadError
                        ?: "Unable to start download.",

                color =
                    MaterialTheme
                        .colorScheme
                        .error,

                modifier =
                    Modifier
                        .fillMaxWidth()
                        .padding(
                            bottom = 12.dp
                        )
            )
        }


        // ==================================================
        // WATCH BUTTON
        // ==================================================

        Button(
            onClick = {

                streamViewModel
                    .loadStream(
                        movieId
                    )
            },

            enabled =
                !isStreamLoading &&
                        !isDownloadLoading &&
                        !isOwnershipLoading,

            modifier =
                Modifier.fillMaxWidth()
        ) {

            if (isStreamLoading) {

                CircularProgressIndicator(
                    modifier =
                        Modifier.height(
                            20.dp
                        ),

                    strokeWidth = 2.dp
                )

            } else {

                Text(
                    text =
                        "WATCH NOW"
                )
            }
        }


        Spacer(
            modifier =
                Modifier.height(12.dp)
        )


        // ==================================================
        // DOWNLOAD BUTTON
        // ==================================================

        Button(
            onClick = {

                downloadViewModel
                    .requestDownload(
                        movieId
                    )
            },

            enabled =
                !isDownloadLoading &&
                        !isStreamLoading &&
                        !isOwnershipLoading,

            modifier =
                Modifier.fillMaxWidth()
        ) {

            if (isDownloadLoading) {

                CircularProgressIndicator(
                    modifier =
                        Modifier.height(
                            20.dp
                        ),

                    strokeWidth = 2.dp
                )

            } else {

                Text(
                    text =
                        "DOWNLOAD PERMANENTLY"
                )
            }
        }


        Spacer(
            modifier =
                Modifier.height(12.dp)
        )


        // ==================================================
        // BACK BUTTON
        // ==================================================

        Button(
            onClick = {

                onBackClick()
            },

            modifier =
                Modifier.fillMaxWidth()
        ) {

            Text(
                text =
                    "BACK"
            )
        }
    }
}