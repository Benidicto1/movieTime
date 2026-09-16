package com.movietime.app

import android.os.Bundle

import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent

import com.movietime.app.data.remote.RetrofitClient
import com.movietime.app.ui.MovieTimeNavigation

class MainActivity : ComponentActivity() {

    override fun onCreate(
        savedInstanceState: Bundle?
    ) {
        super.onCreate(
            savedInstanceState
        )

        RetrofitClient.initialize(
            applicationContext
        )

        setContent {

            MovieTimeNavigation()
        }
    }
}