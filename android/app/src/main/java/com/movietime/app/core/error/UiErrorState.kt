package com.movietime.app.core.error


data class UiErrorState(
    val hasError: Boolean = false,
    val message: String? = null
)