package com.movietime.app.data.remote

import com.movietime.app.data.model.LoginRequest
import com.movietime.app.data.model.TokenResponse
import retrofit2.http.Body
import retrofit2.http.POST

interface AuthApiService {

    /**
     * Obtain JWT access and refresh tokens.
     *
     * POST /api/v1/auth/token/
     */
    @POST("api/v1/auth/token/")
    suspend fun login(
        @Body request: LoginRequest
    ): TokenResponse

    /**
     * Obtain a new access token using the refresh token.
     *
     * POST /api/v1/auth/token/refresh/
     */
    @POST("api/v1/auth/token/refresh/")
    suspend fun refreshToken(
        @Body request: Map<String, String>
    ): TokenResponse
}