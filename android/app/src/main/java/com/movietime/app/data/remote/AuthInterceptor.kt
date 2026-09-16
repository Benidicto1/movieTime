package com.movietime.app.data.remote

import com.movietime.app.data.auth.SecureTokenManager
import okhttp3.Interceptor
import okhttp3.Response

class AuthInterceptor(
    private val tokenManager: SecureTokenManager
) : Interceptor {

    override fun intercept(
        chain: Interceptor.Chain
    ): Response {

        val originalRequest =
            chain.request()

        val accessToken =
            tokenManager.getAccessToken()

        if (accessToken.isNullOrBlank()) {

            return chain.proceed(
                originalRequest
            )
        }

        val authenticatedRequest =
            originalRequest
                .newBuilder()
                .addHeader(
                    "Authorization",
                    "Bearer $accessToken"
                )
                .build()

        return chain.proceed(
            authenticatedRequest
        )
    }
}