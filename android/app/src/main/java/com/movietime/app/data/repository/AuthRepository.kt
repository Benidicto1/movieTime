package com.movietime.app.data.repository

import android.content.Context

import com.movietime.app.data.local.TokenStorage
import com.movietime.app.data.model.LoginRequest
import com.movietime.app.data.model.RegisterRequest
import com.movietime.app.data.network.RetrofitClient


class AuthRepository(
    context: Context
) {

    private val tokenStorage =
        TokenStorage(
            context.applicationContext
        )


    suspend fun login(
        username: String,
        password: String
    ): Result<Unit> {

        return try {

            val response =
                RetrofitClient.authApi.login(

                    LoginRequest(
                        username = username,
                        password = password
                    )
                )


            if (response.isSuccessful) {

                val body =
                    response.body()


                if (body == null) {

                    return Result.failure(
                        Exception(
                            "Empty login response."
                        )
                    )
                }


                tokenStorage.saveTokens(
                    accessToken = body.access,
                    refreshToken = body.refresh
                )


                Result.success(Unit)

            } else {

                Result.failure(
                    Exception(
                        "Login failed: HTTP ${response.code()}"
                    )
                )
            }

        } catch (exception: Exception) {

            Result.failure(
                exception
            )
        }
    }


    suspend fun register(
        username: String,
        email: String,
        password: String,
        passwordConfirmation: String
    ): Result<Unit> {

        return try {

            val response =
                RetrofitClient.authApi.register(

                    RegisterRequest(
                        username = username,
                        email = email,
                        password = password,
                        passwordConfirmation =
                            passwordConfirmation
                    )
                )


            if (response.isSuccessful) {

                Result.success(Unit)

            } else {

                Result.failure(
                    Exception(
                        "Registration failed: HTTP ${response.code()}"
                    )
                )
            }

        } catch (exception: Exception) {

            Result.failure(
                exception
            )
        }
    }


    fun getAccessToken(): String? {

        return tokenStorage
            .getAccessToken()
    }


    fun getRefreshToken(): String? {

        return tokenStorage
            .getRefreshToken()
    }


    fun logout() {

        tokenStorage.clearTokens()
    }


    fun isLoggedIn(): Boolean {

        return tokenStorage
            .isLoggedIn()
    }
}