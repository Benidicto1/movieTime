package com.movietime.app.ui.offline

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.movietime.app.data.local.OfflineMovie


@Composable
fun OfflineMovieLibraryScreen(
    onMovieClick: (OfflineMovie) -> Unit,
    onBackClick: () -> Unit,
    viewModel: OfflineMovieLibraryViewModel =
        viewModel()
) {

    val movies by viewModel.movies.collectAsState()

    val isLoading by
    viewModel.isLoading.collectAsState()

    LaunchedEffect(Unit) {

        viewModel.loadOfflineMovies()
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {

        Text(
            text = "Offline Movie Library",
            style = MaterialTheme.typography.headlineSmall,
            modifier = Modifier.padding(
                bottom = 16.dp
            )
        )

        when {

            isLoading -> {

                Column(
                    modifier = Modifier.fillMaxSize(),
                    horizontalAlignment =
                        Alignment.CenterHorizontally,
                    verticalArrangement =
                        Arrangement.Center
                ) {

                    CircularProgressIndicator()
                }
            }

            movies.isEmpty() -> {

                Column(
                    modifier = Modifier.fillMaxSize(),
                    horizontalAlignment =
                        Alignment.CenterHorizontally,
                    verticalArrangement =
                        Arrangement.Center
                ) {

                    Text(
                        text =
                            "No downloaded movies yet.",
                        style =
                            MaterialTheme
                                .typography
                                .bodyLarge
                    )
                }
            }

            else -> {

                LazyColumn(
                    modifier = Modifier.fillMaxSize(),
                    contentPadding =
                        PaddingValues(
                            bottom = 16.dp
                        ),
                    verticalArrangement =
                        Arrangement.spacedBy(12.dp)
                ) {

                    items(
                        items = movies,
                        key = {
                            it.id
                        }
                    ) { movie ->

                        OfflineMovieItem(
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
}


@Composable
private fun OfflineMovieItem(
    movie: OfflineMovie,
    onClick: () -> Unit
) {

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(
                onClick = onClick
            )
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
            maxLines = 2,
            modifier = Modifier.padding(
                top = 4.dp
            )
        )

        Text(
            text = "Downloaded movie",
            style =
                MaterialTheme
                    .typography
                    .labelMedium,
            modifier = Modifier.padding(
                top = 8.dp
            )
        )
    }
}