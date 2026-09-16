package com.movietime.app.data.model

import com.google.gson.annotations.SerializedName


data class LoginRequest(
    val username: String,
    val password: String
)


data class RegisterRequest(
    val username: String,
    val email: String,
    val password: String,

    @SerializedName("password2")
    val passwordConfirmation: String
)


data class TokenResponse(
    val access: String,
    val refresh: String
)


data class RegisterResponse(
    val detail: String? = null,
    val message: String? = null
)