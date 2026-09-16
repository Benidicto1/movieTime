package com.movietime.app.ui.payment

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
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel

@Composable
fun PaymentConfirmationScreen(
    paymentId: Int,
    onPaymentSuccessful: (Int) -> Unit,
    onBackClick: () -> Unit,
    viewModel: PaymentConfirmationViewModel = viewModel()
) {

    val payment by
    viewModel.payment.collectAsState()

    val isLoading by
    viewModel.isLoading.collectAsState()

    val errorMessage by
    viewModel.errorMessage.collectAsState()


    LaunchedEffect(paymentId) {

        viewModel.confirmPayment(
            paymentId
        )
    }


    LaunchedEffect(payment) {

        val confirmedPayment =
            payment

        if (
            confirmedPayment != null &&
            confirmedPayment.status == "SUCCESS"
        ) {

            onPaymentSuccessful(
                confirmedPayment.movieId
            )
        }
    }


    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp),

        horizontalAlignment =
            Alignment.CenterHorizontally,

        verticalArrangement =
            Arrangement.Center
    ) {

        Text(
            text = "Payment Confirmation",

            style =
                MaterialTheme
                    .typography
                    .headlineMedium
        )


        Spacer(
            modifier =
                Modifier.height(24.dp)
        )


        if (isLoading) {

            CircularProgressIndicator()

            Spacer(
                modifier =
                    Modifier.height(16.dp)
            )

            Text(
                text =
                    "Verifying your payment..."
            )
        }


        if (errorMessage != null) {

            Text(
                text =
                    errorMessage
                        ?: "Unable to verify payment.",

                color =
                    MaterialTheme
                        .colorScheme
                        .error,

                modifier =
                    Modifier
                        .fillMaxWidth()
                        .padding(
                            bottom = 16.dp
                        )
            )

            Button(
                onClick = {

                    viewModel.confirmPayment(
                        paymentId
                    )
                }
            ) {

                Text(
                    text = "TRY AGAIN"
                )
            }
        }


        payment?.let { result ->

            when (result.status) {

                "SUCCESS" -> {

                    Text(
                        text =
                            "Payment successful!",

                        style =
                            MaterialTheme
                                .typography
                                .titleLarge
                    )

                    Spacer(
                        modifier =
                            Modifier.height(8.dp)
                    )

                    Text(
                        text =
                            result.message
                    )
                }

                "PENDING" -> {

                    Text(
                        text =
                            "Payment is still being processed.",

                        style =
                            MaterialTheme
                                .typography
                                .titleMedium
                    )

                    Spacer(
                        modifier =
                            Modifier.height(8.dp)
                    )

                    Text(
                        text =
                            result.message
                    )

                    Spacer(
                        modifier =
                            Modifier.height(16.dp)
                    )

                    Button(
                        onClick = {

                            viewModel.confirmPayment(
                                paymentId
                            )
                        }
                    ) {

                        Text(
                            text = "CHECK AGAIN"
                        )
                    }
                }

                "FAILED" -> {

                    Text(
                        text =
                            "Payment failed.",

                        style =
                            MaterialTheme
                                .typography
                                .titleMedium
                    )

                    Spacer(
                        modifier =
                            Modifier.height(8.dp)
                    )

                    Text(
                        text =
                            result.message
                    )

                    Spacer(
                        modifier =
                            Modifier.height(16.dp)
                    )

                    Button(
                        onClick = {

                            viewModel.confirmPayment(
                                paymentId
                            )
                        }
                    ) {

                        Text(
                            text = "CHECK AGAIN"
                        )
                    }
                }

                "CANCELLED" -> {

                    Text(
                        text =
                            "Payment was cancelled.",

                        style =
                            MaterialTheme
                                .typography
                                .titleMedium
                    )

                    Spacer(
                        modifier =
                            Modifier.height(8.dp)
                    )

                    Text(
                        text =
                            result.message
                    )
                }
            }
        }


        Spacer(
            modifier =
                Modifier.height(24.dp)
        )


        Button(
            onClick = {
                onBackClick()
            }
        ) {

            Text(
                text = "BACK"
            )
        }
    }
}