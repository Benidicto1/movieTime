package com.movietime.app.ui.payment

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll

import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Check

import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.RadioButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar

import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue

import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp


data class PaymentPlan(
    val id: Int,
    val name: String,
    val price: Int
)


@Composable
fun PaymentScreen(
    onBackClick: () -> Unit,
    onContinueClick: (
        planId: Int,
        paymentMethod: String
    ) -> Unit
) {

    val plans = listOf(

        PaymentPlan(
            id = 1,
            name = "Day",
            price = 900
        ),

        PaymentPlan(
            id = 2,
            name = "Week",
            price = 2000
        ),

        PaymentPlan(
            id = 3,
            name = "Month",
            price = 4500
        )
    )


    var selectedPlan by remember {
        mutableStateOf(plans.first())
    }


    var selectedPaymentMethod by remember {
        mutableStateOf("MTN")
    }


    Scaffold(

        topBar = {

            TopAppBar(

                title = {
                    Text("Payment")
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

        Column(

            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .padding(16.dp)
                .verticalScroll(
                    rememberScrollState()
                ),

            verticalArrangement =
                Arrangement.spacedBy(12.dp)
        ) {

            Text(

                text =
                    "Choose Subscription",

                style =
                    MaterialTheme.typography.headlineSmall
            )


            plans.forEach { plan ->

                PaymentPlanCard(

                    plan = plan,

                    selected =
                        selectedPlan.id == plan.id,

                    onClick = {

                        selectedPlan = plan
                    }
                )
            }


            Spacer(
                modifier =
                    Modifier.height(12.dp)
            )


            Text(

                text =
                    "Payment Method",

                style =
                    MaterialTheme.typography.headlineSmall
            )


            PaymentMethodCard(

                title =
                    "MTN Mobile Money",

                selected =
                    selectedPaymentMethod == "MTN",

                onClick = {

                    selectedPaymentMethod = "MTN"
                }
            )


            PaymentMethodCard(

                title =
                    "Airtel Money",

                selected =
                    selectedPaymentMethod == "AIRTEL",

                onClick = {

                    selectedPaymentMethod = "AIRTEL"
                }
            )


            Spacer(
                modifier =
                    Modifier.height(12.dp)
            )


            Text(

                text =
                    "Total: UGX ${selectedPlan.price}",

                style =
                    MaterialTheme.typography.titleLarge
            )


            Button(

                onClick = {

                    onContinueClick(
                        selectedPlan.id,
                        selectedPaymentMethod
                    )
                },

                modifier =
                    Modifier.fillMaxWidth()
            ) {

                Text("Continue")
            }
        }
    }
}


@Composable
private fun PaymentPlanCard(
    plan: PaymentPlan,
    selected: Boolean,
    onClick: () -> Unit
) {

    Card(

        onClick = onClick,

        modifier =
            Modifier.fillMaxWidth()
    ) {

        Row(

            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),

            verticalAlignment =
                Alignment.CenterVertically
        ) {

            RadioButton(

                selected = selected,

                onClick = onClick
            )


            Spacer(
                modifier =
                    Modifier.width(12.dp)
            )


            Column {

                Text(

                    text =
                        plan.name,

                    style =
                        MaterialTheme.typography.titleMedium
                )


                Text(

                    text =
                        "UGX ${plan.price}",

                    style =
                        MaterialTheme.typography.bodyMedium
                )
            }


            if (selected) {

                Spacer(
                    modifier =
                        Modifier.weight(1f)
                )


                Icon(

                    imageVector =
                        Icons.Default.Check,

                    contentDescription =
                        "Selected"
                )
            }
        }
    }
}


@Composable
private fun PaymentMethodCard(
    title: String,
    selected: Boolean,
    onClick: () -> Unit
) {

    Card(

        onClick = onClick,

        modifier =
            Modifier.fillMaxWidth()
    ) {

        Row(

            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),

            verticalAlignment =
                Alignment.CenterVertically
        ) {

            RadioButton(

                selected = selected,

                onClick = onClick
            )


            Spacer(
                modifier =
                    Modifier.width(12.dp)
            )


            Text(

                text = title,

                style =
                    MaterialTheme.typography.titleMedium
            )
        }
    }
}