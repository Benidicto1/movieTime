package com.movietime.app.ui.screens

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Card
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.navigation.NavHostController
import com.movietime.app.data.model.Movie
import com.movietime.app.ui.data.testMovies


@Composable
fun SearchScreen(
    navController: NavHostController
) {

    /*
     * ---------------------------------------------------------
     * SEARCH STATE
     * ---------------------------------------------------------
     */

    var searchQuery by remember {
        mutableStateOf("")
    }


    /*
     * ---------------------------------------------------------
     * FILTER MOVIES
     * ---------------------------------------------------------
     */

    val filteredMovies = testMovies.filter { movie ->

        movie.title.contains(
            searchQuery,
            ignoreCase = true
        )
    }


    /*
     * ---------------------------------------------------------
     * SCREEN
     * ---------------------------------------------------------
     */

    Scaffold { innerPadding ->

        Column(

            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .padding(16.dp),

            verticalArrangement = Arrangement.spacedBy(12.dp)

        ) {

            /*
             * -------------------------------------------------
             * SEARCH FIELD
             * -------------------------------------------------
             */

            OutlinedTextField(

                value = searchQuery,

                onValueChange = {
                    searchQuery = it
                },

                modifier = Modifier
                    .fillMaxWidth(),

                label = {
                    Text(
                        text = "Search movies"
                    )
                },

                placeholder = {
                    Text(
                        text = "Enter movie title"
                    )
                },

                singleLine = true
            )


            /*
             * -------------------------------------------------
             * SEARCH RESULTS
             * -------------------------------------------------
             */

            if (
                searchQuery.isNotBlank() &&
                filteredMovies.isEmpty()
            ) {

                Text(
                    text = "No movies found."
                )

            } else {

                LazyColumn(

                    modifier = Modifier.fillMaxSize(),

                    verticalArrangement = Arrangement.spacedBy(12.dp)

                ) {

                    items(filteredMovies) { movie ->

                        SearchMovieItem(

                            movie = movie,

                            onClick = {

                                navController.navigate(
                                    "movie_details/${movie.id}"
                                )
                            }
                        )
                    }
                }
            }
        }
    }
}


/*
 * ============================================================
 * SEARCH MOVIE ITEM
 * ============================================================
 */

@Composable
fun SearchMovieItem(
    movie: Movie,
    onClick: () -> Unit
) {

    Card(

        modifier = Modifier
            .fillMaxWidth()
            .clickable {
                onClick()
            }

    ) {

        Column(

            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),

            verticalArrangement = Arrangement.spacedBy(6.dp)

        ) {

            /*
             * Movie title
             */

            Text(
                text = movie.title
            )


            /*
             * Movie rating
             */

            Text(
                text = "⭐ ${movie.rating}"
            )


            /*
             * Movie description
             */

            Text(
                text = movie.description
            )
        }
    }
}