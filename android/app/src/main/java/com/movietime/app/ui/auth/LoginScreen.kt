package com.movietime.app.ui.auth

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding

import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text

import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue

import androidx.compose.ui.Modifier
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp


@Composable
fun LoginScreen(
    onLoginClick: (
        username: String,
        password: String
    ) -> Unit,

    onRegisterClick: () -> Unit
) {

    var username by remember {
        mutableStateOf("")
    }


    var password by remember {
        mutableStateOf("")
    }


    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp),

        verticalArrangement =
            Arrangement.Center
    ) {

        Text(
            text = "MovieTime",

            style =
                MaterialTheme
                    .typography
                    .headlineLarge
        )


        Spacer(
            modifier =
                Modifier.height(24.dp)
        )


        Text(
            text = "Login",

            style =
                MaterialTheme
                    .typography
                    .headlineMedium
        )


        Spacer(
            modifier =
                Modifier.height(16.dp)
        )


        OutlinedTextField(
            value = username,

            onValueChange = {
                username = it
            },

            label = {
                Text("Username")
            },

            modifier =
                Modifier.fillMaxWidth(),

            singleLine = true
        )


        Spacer(
            modifier =
                Modifier.height(12.dp)
        )


        OutlinedTextField(
            value = password,

            onValueChange = {
                password = it
            },

            label = {
                Text("Password")
            },

            visualTransformation =
                PasswordVisualTransformation(),

            modifier =
                Modifier.fillMaxWidth(),

            singleLine = true
        )


        Spacer(
            modifier =
                Modifier.height(20.dp)
        )


        Button(
            onClick = {

                onLoginClick(
                    username,
                    password
                )
            },

            modifier =
                Modifier.fillMaxWidth(),

            enabled =
                username.isNotBlank() &&
                        password.isNotBlank()
        ) {

            Text(
                text = "LOGIN"
            )
        }


        Spacer(
            modifier =
                Modifier.height(12.dp)
        )


        Button(
            onClick = {
                onRegisterClick()
            },

            modifier =
                Modifier.fillMaxWidth()
        ) {

            Text(
                text =
                    "CREATE ACCOUNT"
            )
        }
    }
}