package com.movietime.app.ui.navigation

import androidx.compose.runtime.Composable
import androidx.navigation.NavHostController
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.navArgument
import com.movietime.app.ui.screens.HomeScreen
import com.movietime.app.ui.screens.MovieDetailsScreen
import com.movietime.app.ui.screens.SearchScreen


@Composable
fun MovieTimeNavGraph(
    navController: NavHostController
) {

    NavHost(

        navController = navController,

        startDestination = MovieTimeRoutes.HOME

    ) {


        /*
         * ====================================================
         * HOME
         * ====================================================
         */

        composable(
            route = MovieTimeRoutes.HOME
        ) {

            HomeScreen(
                navController = navController
            )
        }


        /*
         * ====================================================
         * SEARCH
         * ====================================================
         */

        composable(
            route = MovieTimeRoutes.SEARCH
        ) {

            SearchScreen(
                navController = navController
            )
        }


        /*
         * ====================================================
         * MOVIE DETAILS
         * ====================================================
         */

        composable(

            route = MovieTimeRoutes.MOVIE_DETAILS,

            arguments = listOf(

                navArgument("movieId") {

                    type = NavType.IntType
                }
            )

        ) { backStackEntry ->

            val movieId = backStackEntry
                .arguments
                ?.getInt("movieId")
                ?: return@composable


            MovieDetailsScreen(

                navController = navController,

                movieId = movieId
            )
        }
    }
}