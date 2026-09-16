package com.movietime.app.ui.home

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
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
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.movietime.app.data.model.Movie

@Composable
fun HomeScreen(
    onMovieClick: (Int) -> Unit,
    onSearchClick: () -> Unit,
    onCategoriesClick: () -> Unit,
    onOfflineLibraryClick: () -> Unit,
    viewModel: HomeViewModel = viewModel()
) {
    val movies by viewModel.movies.collectAsState()
    val isLoading by viewModel.isLoading.collectAsState()
    val errorMessage by viewModel.errorMessage.collectAsState()

    LaunchedEffect(Unit) {
        viewModel.loadMovies()
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {

        Text(
            text = "MovieTime",
            style = MaterialTheme.typography.headlineMedium
        )

        TextButton(
            onClick = onSearchClick
        ) {
            Text(
                text = "Search"
            )
        }

        TextButton(
            onClick = onCategoriesClick
        ) {
            Text(
                text = "Categories"
            )
        }

        TextButton(
            onClick = onOfflineLibraryClick
        ) {
            Text(
                text = "Offline Library"
            )
        }

        if (isLoading) {

            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(32.dp),
                contentAlignment = Alignment.Center
            ) {

                CircularProgressIndicator()
            }
        }

        if (errorMessage != null) {

            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                horizontalAlignment =
                    Alignment.CenterHorizontally
            ) {

                Text(
                    text =
                        errorMessage
                            ?: "Unable to load movies.",
                    color =
                        MaterialTheme
                            .colorScheme
                            .error
                )

                TextButton(
                    onClick = {
                        viewModel.loadMovies()
                    }
                ) {

                    Text(
                        text = "Retry"
                    )
                }
            }
        }

        if (!isLoading && errorMessage == null) {

            if (movies.isEmpty()) {

                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment =
                        Alignment.Center
                ) {

                    Text(
                        text = "No movies available."
                    )
                }

            } else {

                MovieList(
                    movies = movies,
                    onMovieClick = onMovieClick
                )
            }
        }
    }
}

@Composable
private fun MovieList(
    movies: List<Movie>,
    onMovieClick: (Int) -> Unit
) {

    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(
            top = 16.dp,
            bottom = 32.dp
        ),
        verticalArrangement =
            Arrangement.spacedBy(8.dp)
    ) {

        items(
            items = movies,
            key = { movie ->
                movie.id
            }
        ) { movie ->

            MovieItem(
                movie = movie,
                onClick = {
                    onMovieClick(movie.id)
                }
            )
        }
    }
}

@Composable
private fun MovieItem(
    movie: Movie,
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
                    .titleLarge
        )

        if (movie.description.isNotBlank()) {

            Text(
                text = movie.description,
                style =
                    MaterialTheme
                        .typography
                        .bodyMedium,
                modifier = Modifier.padding(
                    top = 4.dp
                )
            )
        }

        movie.releaseDate?.let { releaseDate ->

            Text(
                text = "Release date: $releaseDate",
                style =
                    MaterialTheme
                        .typography
                        .bodySmall,
                modifier = Modifier.padding(
                    top = 4.dp
                )
            )
        }

        movie.rating?.let { rating ->

            Text(
                text = "Rating: $rating",
                style =
                    MaterialTheme
                        .typography
                        .bodySmall,
                modifier = Modifier.padding(
                    top = 4.dp
                )
            )
        }
    }
}