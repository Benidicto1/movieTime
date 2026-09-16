package com.movietime.app.ui

import android.net.Uri

import androidx.compose.runtime.Composable
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument

import com.movietime.app.ui.categories.CategoriesScreen
import com.movietime.app.ui.details.MovieDetailsScreen
import com.movietime.app.ui.home.HomeScreen
import com.movietime.app.ui.offline.OfflineMovieLibraryScreen
import com.movietime.app.ui.payment.PaymentConfirmationScreen
import com.movietime.app.ui.player.VideoPlayerScreen
import com.movietime.app.ui.purchases.PurchaseHistoryScreen
import com.movietime.app.ui.search.SearchScreen


@Composable
fun MovieTimeNavigation() {

    val navController =
        rememberNavController()

    NavHost(
        navController = navController,
        startDestination = "home"
    ) {

        // --------------------------------------------------
        // HOME
        // --------------------------------------------------

        composable(
            route = "home"
        ) {

            HomeScreen(

                onMovieClick = { movieId ->

                    navController.navigate(
                        "movie_details/$movieId"
                    )
                },

                onSearchClick = {

                    navController.navigate(
                        "search"
                    )
                },

                onCategoriesClick = {

                    navController.navigate(
                        "categories"
                    )
                },

                onOfflineLibraryClick = {

                    navController.navigate(
                        "offline_library"
                    )
                }
            )
        }


        // --------------------------------------------------
        // MOVIE DETAILS
        // --------------------------------------------------

        composable(
            route = "movie_details/{movieId}",

            arguments = listOf(

                navArgument("movieId") {

                    type =
                        NavType.IntType
                }
            )
        ) { backStackEntry ->

            val movieId =
                backStackEntry
                    .arguments
                    ?.getInt("movieId")

            if (movieId != null) {

                MovieDetailsScreen(

                    movieId = movieId,

                    onBackClick = {

                        navController
                            .popBackStack()
                    },

                    onWatchClick = { streamUrl ->

                        val encodedUrl =
                            Uri.encode(
                                streamUrl
                            )

                        navController.navigate(
                            "video_player/$encodedUrl"
                        )
                    },

                    onDownloadClick = {

                        /*
                         * Download authorization is
                         * handled inside
                         * MovieDetailsScreen.
                         */
                    }
                )
            }
        }


        // --------------------------------------------------
        // SEARCH
        // --------------------------------------------------

        composable(
            route = "search"
        ) {

            SearchScreen(

                onMovieClick = { movieId ->

                    navController.navigate(
                        "movie_details/$movieId"
                    )
                },

                onBackClick = {

                    navController
                        .popBackStack()
                }
            )
        }


        // --------------------------------------------------
        // CATEGORIES
        // --------------------------------------------------

        composable(
            route = "categories"
        ) {

            CategoriesScreen(

                onMovieClick = { movieId ->

                    navController.navigate(
                        "movie_details/$movieId"
                    )
                },

                onBackClick = {

                    navController
                        .popBackStack()
                }
            )
        }


        // --------------------------------------------------
        // VIDEO PLAYER
        // --------------------------------------------------

        composable(
            route = "video_player/{streamUrl}",

            arguments = listOf(

                navArgument("streamUrl") {

                    type =
                        NavType.StringType
                }
            )
        ) { backStackEntry ->

            val encodedUrl =
                backStackEntry
                    .arguments
                    ?.getString("streamUrl")

            if (encodedUrl != null) {

                val streamUrl =
                    Uri.decode(
                        encodedUrl
                    )

                VideoPlayerScreen(
                    streamUrl = streamUrl
                )
            }
        }


        // --------------------------------------------------
        // OFFLINE MOVIE LIBRARY
        // --------------------------------------------------

        composable(
            route = "offline_library"
        ) {

            OfflineMovieLibraryScreen(

                onMovieClick = { movie ->

                    /*
                     * Local video playback will be
                     * connected to the downloaded movie
                     * in the offline playback implementation.
                     */
                },

                onBackClick = {

                    navController
                        .popBackStack()
                }
            )
        }


        // --------------------------------------------------
        // PAYMENT CONFIRMATION
        // --------------------------------------------------

        composable(
            route =
                "payment_confirmation/{paymentId}",

            arguments = listOf(

                navArgument("paymentId") {

                    type =
                        NavType.IntType
                }
            )
        ) { backStackEntry ->

            val paymentId =
                backStackEntry
                    .arguments
                    ?.getInt("paymentId")

            if (paymentId != null) {

                PaymentConfirmationScreen(

                    paymentId =
                        paymentId,

                    onPaymentSuccessful = {
                            movieId ->

                        navController.navigate(
                            "movie_details/$movieId"
                        ) {

                            popUpTo(
                                "payment_confirmation/$paymentId"
                            ) {

                                inclusive =
                                    true
                            }
                        }
                    },

                    onBackClick = {

                        navController
                            .popBackStack()
                    }
                )
            }
        }


        // --------------------------------------------------
        // PURCHASE HISTORY
        // --------------------------------------------------

        composable(
            route = "purchase_history"
        ) {

            PurchaseHistoryScreen(

                onMovieClick = { movieId ->

                    navController.navigate(
                        "movie_details/$movieId"
                    )
                },

                onBackClick = {

                    navController
                        .popBackStack()
                }
            )
        }
    }
}