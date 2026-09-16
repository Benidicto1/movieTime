package com.movietime.app.ui.purchases

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
import androidx.compose.material3.Button
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
import com.movietime.app.data.model.PurchaseHistoryItem

@Composable
fun PurchaseHistoryScreen(
    onMovieClick: (Int) -> Unit,
    onBackClick: () -> Unit,
    viewModel: PurchaseHistoryViewModel =
        viewModel()
) {

    val purchases by
    viewModel
        .purchases
        .collectAsState()

    val isLoading by
    viewModel
        .isLoading
        .collectAsState()

    val errorMessage by
    viewModel
        .errorMessage
        .collectAsState()


    LaunchedEffect(Unit) {

        viewModel.loadPurchaseHistory()
    }


    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {

        Text(
            text = "Purchase History",

            style =
                MaterialTheme
                    .typography
                    .headlineMedium
        )


        if (isLoading) {

            Box(
                modifier =
                    Modifier
                        .fillMaxWidth()
                        .padding(
                            32.dp
                        ),

                contentAlignment =
                    Alignment.Center
            ) {

                CircularProgressIndicator()
            }
        }


        if (errorMessage != null) {

            Column(
                modifier =
                    Modifier
                        .fillMaxWidth()
                        .padding(
                            16.dp
                        ),

                horizontalAlignment =
                    Alignment.CenterHorizontally
            ) {

                Text(
                    text =
                        errorMessage
                            ?: "Unable to load purchase history.",

                    color =
                        MaterialTheme
                            .colorScheme
                            .error
                )


                Button(
                    onClick = {

                        viewModel
                            .loadPurchaseHistory()
                    }
                ) {

                    Text(
                        text = "RETRY"
                    )
                }
            }
        }


        if (
            !isLoading &&
            errorMessage == null
        ) {

            if (purchases.isEmpty()) {

                Box(
                    modifier =
                        Modifier
                            .fillMaxSize(),

                    contentAlignment =
                        Alignment.Center
                ) {

                    Text(
                        text =
                            "You have no purchases yet."
                    )
                }

            } else {

                PurchaseList(
                    purchases = purchases,
                    onMovieClick = onMovieClick
                )
            }
        }


        Button(
            onClick = {

                onBackClick()
            },

            modifier =
                Modifier.fillMaxWidth()
        ) {

            Text(
                text = "BACK"
            )
        }
    }
}


@Composable
private fun PurchaseList(
    purchases: List<PurchaseHistoryItem>,
    onMovieClick: (Int) -> Unit
) {

    LazyColumn(
        modifier =
            Modifier.fillMaxSize(),

        contentPadding =
            PaddingValues(
                top = 16.dp,
                bottom = 80.dp
            ),

        verticalArrangement =
            Arrangement.spacedBy(
                8.dp
            )
    ) {

        items(
            items = purchases,

            key = {
                    purchase ->
                purchase.id
            }
        ) { purchase ->

            PurchaseItem(
                purchase = purchase,

                onClick = {

                    onMovieClick(
                        purchase.movieId
                    )
                }
            )
        }
    }
}


@Composable
private fun PurchaseItem(
    purchase: PurchaseHistoryItem,
    onClick: () -> Unit
) {

    Column(
        modifier =
            Modifier
                .fillMaxWidth()
                .clickable(
                    onClick = onClick
                )
                .padding(16.dp)
    ) {

        Text(
            text =
                purchase.movieTitle,

            style =
                MaterialTheme
                    .typography
                    .titleLarge
        )


        Text(
            text =
                "Amount: UGX ${purchase.amount}",

            style =
                MaterialTheme
                    .typography
                    .bodyMedium,

            modifier =
                Modifier.padding(
                    top = 4.dp
                )
        )


        Text(
            text =
                "Purchased: ${purchase.purchaseDate}",

            style =
                MaterialTheme
                    .typography
                    .bodySmall,

            modifier =
                Modifier.padding(
                    top = 4.dp
                )
        )


        Text(
            text =
                "Payment: ${purchase.paymentStatus}",

            style =
                MaterialTheme
                    .typography
                    .bodySmall,

            modifier =
                Modifier.padding(
                    top = 4.dp
                )
        )


        Text(
            text =
                "Ownership: ${purchase.ownershipStatus}",

            style =
                MaterialTheme
                    .typography
                    .bodySmall,

            modifier =
                Modifier.padding(
                    top = 4.dp
                )
        )
    }
}