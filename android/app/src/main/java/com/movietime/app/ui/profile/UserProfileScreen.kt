package com.movietime.app.ui.profile

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
import androidx.compose.material.icons.filled.AccountCircle
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Download
import androidx.compose.material.icons.filled.History
import androidx.compose.material.icons.filled.Logout
import androidx.compose.material.icons.filled.Subscriptions

import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar

import androidx.compose.runtime.Composable

import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp


@Composable
fun UserProfileScreen(
    onBackClick: () -> Unit,
    onDownloadsClick: () -> Unit,
    onPurchaseHistoryClick: () -> Unit,
    onSubscriptionClick: () -> Unit,
    onLogoutClick: () -> Unit
) {

    Scaffold(

        topBar = {

            TopAppBar(

                title = {
                    Text(
                        text = "Profile"
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

        Column(

            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .padding(16.dp)
                .verticalScroll(
                    rememberScrollState()
                ),

            horizontalAlignment =
                Alignment.CenterHorizontally
        ) {

            // --------------------------------------------------
            // PROFILE ICON
            // --------------------------------------------------

            Icon(

                imageVector =
                    Icons.Default.AccountCircle,

                contentDescription =
                    "Profile",

                modifier = Modifier
                    .height(100.dp)
                    .width(100.dp)
            )


            Spacer(
                modifier =
                    Modifier.height(16.dp)
            )


            // --------------------------------------------------
            // USER NAME
            // --------------------------------------------------

            Text(

                text =
                    "MovieTime User",

                style =
                    MaterialTheme.typography.headlineSmall
            )


            Spacer(
                modifier =
                    Modifier.height(4.dp)
            )


            // --------------------------------------------------
            // USER EMAIL
            // --------------------------------------------------

            Text(

                text =
                    "user@example.com",

                style =
                    MaterialTheme.typography.bodyMedium
            )


            Spacer(
                modifier =
                    Modifier.height(24.dp)
            )


            // --------------------------------------------------
            // ACCOUNT SECTION
            // --------------------------------------------------

            Text(

                text =
                    "Account",

                style =
                    MaterialTheme.typography.titleLarge,

                modifier =
                    Modifier.fillMaxWidth()
            )


            Spacer(
                modifier =
                    Modifier.height(8.dp)
            )


            // --------------------------------------------------
            // SUBSCRIPTION
            // --------------------------------------------------

            ProfileMenuCard(

                icon =
                    Icons.Default.Subscriptions,

                title =
                    "Subscription",

                description =
                    "View subscription plans and payments",

                onClick =
                    onSubscriptionClick
            )


            // --------------------------------------------------
            // PURCHASE HISTORY
            // --------------------------------------------------

            ProfileMenuCard(

                icon =
                    Icons.Default.History,

                title =
                    "Purchase History",

                description =
                    "View your movie purchases",

                onClick =
                    onPurchaseHistoryClick
            )


            // --------------------------------------------------
            // DOWNLOAD LIBRARY
            // --------------------------------------------------

            ProfileMenuCard(

                icon =
                    Icons.Default.Download,

                title =
                    "Download Library",

                description =
                    "View your downloaded movies",

                onClick =
                    onDownloadsClick
            )


            Spacer(
                modifier =
                    Modifier.height(24.dp)
            )


            // --------------------------------------------------
            // LOGOUT
            // --------------------------------------------------

            Button(

                onClick =
                    onLogoutClick,

                modifier =
                    Modifier.fillMaxWidth()
            ) {

                Icon(

                    imageVector =
                        Icons.Default.Logout,

                    contentDescription =
                        "Logout"
                )


                Spacer(
                    modifier =
                        Modifier.width(8.dp)
                )


                Text(
                    text =
                        "Logout"
                )
            }
        }
    }
}


@Composable
private fun ProfileMenuCard(

    icon:
    androidx.compose.ui.graphics.vector.ImageVector,

    title: String,

    description: String,

    onClick: () -> Unit
) {

    Card(

        onClick =
            onClick,

        modifier =
            Modifier
                .fillMaxWidth()
                .padding(
                    vertical = 6.dp
                )
    ) {

        Row(

            modifier =
                Modifier
                    .fillMaxWidth()
                    .padding(16.dp),

            verticalAlignment =
                Alignment.CenterVertically
        ) {

            Icon(

                imageVector =
                    icon,

                contentDescription =
                    title
            )


            Spacer(
                modifier =
                    Modifier.width(16.dp)
            )


            Column(

                modifier =
                    Modifier.weight(1f)
            ) {

                Text(

                    text =
                        title,

                    style =
                        MaterialTheme.typography.titleMedium
                )


                Spacer(
                    modifier =
                        Modifier.height(2.dp)
                )


                Text(

                    text =
                        description,

                    style =
                        MaterialTheme.typography.bodyMedium
                )
            }
        }
    }
}