package com.movietime.app.data.remote

import com.movietime.app.data.local.TokenManager
import okhttp3.Interceptor
import okhttp3.OkHttpClient
import okhttp3.Response
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit


object RetrofitClient {

    /*
     * Production API.
     *
     * IMPORTANT:
     * Replace this with the real MovieTime HTTPS API domain.
     */
    private const val BASE_URL =
        "https://api.example.com/"


    private const val CONNECT_TIMEOUT_SECONDS = 30L

    private const val READ_TIMEOUT_SECONDS = 30L

    private const val WRITE_TIMEOUT_SECONDS = 30L


    private val tokenManager: TokenManager by lazy {
        TokenManager()
    }


    private class AuthInterceptor : Interceptor {

        override fun intercept(
            chain: Interceptor.Chain
        ): Response {

            val originalRequest =
                chain.request()

            val path =
                originalRequest.url.encodedPath


            val isAuthenticationRequest =
                path == "/api/v1/auth/token/" ||
                        path == "/api/v1/auth/token/refresh/"


            if (isAuthenticationRequest) {
                return chain.proceed(
                    originalRequest
                )
            }


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
                    .header(
                        "Authorization",
                        "Bearer $accessToken"
                    )
                    .build()


            return chain.proceed(
                authenticatedRequest
            )
        }
    }


    private val loggingInterceptor:
            HttpLoggingInterceptor by lazy {

        HttpLoggingInterceptor().apply {

            /*
             * Do not use BODY logging in production.
             *
             * Authorization tokens, payment information and
             * signed media URLs must never appear in logs.
             */
            level =
                HttpLoggingInterceptor.Level.BASIC
        }
    }


    private val okHttpClient:
            OkHttpClient by lazy {

        OkHttpClient.Builder()

            .addInterceptor(
                AuthInterceptor()
            )

            .addInterceptor(
                loggingInterceptor
            )

            .connectTimeout(
                CONNECT_TIMEOUT_SECONDS,
                TimeUnit.SECONDS
            )

            .readTimeout(
                READ_TIMEOUT_SECONDS,
                TimeUnit.SECONDS
            )

            .writeTimeout(
                WRITE_TIMEOUT_SECONDS,
                TimeUnit.SECONDS
            )

            .build()
    }


    private val retrofit:
            Retrofit by lazy {

        Retrofit.Builder()

            .baseUrl(
                BASE_URL
            )

            .client(
                okHttpClient
            )

            .addConverterFactory(
                GsonConverterFactory.create()
            )

            .build()
    }


    val authApi:
            AuthApiService by lazy {

        retrofit.create(
            AuthApiService::class.java
        )
    }


    val movieApi:
            MovieApiService by lazy {

        retrofit.create(
            MovieApiService::class.java
        )
    }


    val paymentApi:
            PaymentApiService by lazy {

        retrofit.create(
            PaymentApiService::class.java
        )
    }
}