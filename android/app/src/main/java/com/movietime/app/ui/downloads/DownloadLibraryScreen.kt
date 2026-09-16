package com.movietime.app.ui.downloads

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.Card
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

import com.movietime.app.data.model.DownloadedMovie


@Composable
fun DownloadLibraryScreen(
    movies: List<DownloadedMovie>,
    onMovieClick: (DownloadedMovie) -> Unit,
    onBackClick: () -> Unit
) {

    Scaffold(

        topBar = {

            TopAppBar(

                title = {
                    Text(
                        text = "Download Library"
                    )
                },

                navigationIcon = {

                    IconButton(
                        onClick = onBackClick
                    ) {

                        Icon(
                            imageVector =
                                Icons.Default.ArrowBack,

                            contentDescription =
                                "Back"
                        )
                    }
                }
            )
        }

    ) { paddingValues ->

        if (movies.isEmpty()) {

            EmptyDownloadLibrary(
                paddingValues = paddingValues
            )

        } else {

            LazyColumn(

                modifier = Modifier
                    .fillMaxSize()
                    .padding(paddingValues),

                contentPadding =
                    PaddingValues(16.dp),

                verticalArrangement =
                    Arrangement.spacedBy(12.dp)

            ) {

                items(
                    items = movies,

                    key = {
                        it.movieId
                    }

                ) { movie ->

                    DownloadedMovieItem(
                        movie = movie,

                        onClick = {
                            onMovieClick(movie)
                        }
                    )
                }
            }
        }
    }
}


@Composable
private fun DownloadedMovieItem(
    movie: DownloadedMovie,
    onClick: () -> Unit
) {

    Card(

        modifier = Modifier
            .fillMaxWidth()
            .clickable(
                onClick = onClick
            )
    ) {

        Column(

            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)

        ) {

            Text(
                text = movie.title,

                style =
                    MaterialTheme
                        .typography
                        .titleMedium
            )

            Text(
                text = movie.description,

                style =
                    MaterialTheme
                        .typography
                        .bodyMedium,

                modifier =
                    Modifier.padding(
                        top = 6.dp
                    )
            )

            Text(
                text = "Downloaded",

                style =
                    MaterialTheme
                        .typography
                        .labelMedium,

                modifier =
                    Modifier.padding(
                        top = 8.dp
                    )
            )
        }
    }
}


@Composable
private fun EmptyDownloadLibrary(
    paddingValues: PaddingValues
) {

    Column(

        modifier = Modifier
            .fillMaxSize()
            .padding(paddingValues)
            .padding(24.dp)

    ) {

        Text(
            text = "No downloaded movies",

            style =
                MaterialTheme
                    .typography
                    .headlineSmall
        )

        Text(
            text =
                "Movies you permanently download " +
                        "will appear here.",

            style =
                MaterialTheme
                    .typography
                    .bodyLarge,

            modifier =
                Modifier.padding(
                    top = 8.dp
                )
        )
    }
}
