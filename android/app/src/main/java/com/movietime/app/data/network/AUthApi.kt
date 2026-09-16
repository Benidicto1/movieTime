package com.movietime.app.data.network

import com.movietime.app.data.model.LoginRequest
import com.movietime.app.data.model.RegisterRequest
import com.movietime.app.data.model.RegisterResponse
import com.movietime.app.data.model.TokenResponse

import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.POST


interface AuthApi {

    @POST("api/accounts/register/")
    suspend fun register(
        @Body request: RegisterRequest
    ): Response<RegisterResponse>


    @POST("api/accounts/token/")
    suspend fun login(
        @Body request: LoginRequest
    ): Response<TokenResponse>
}