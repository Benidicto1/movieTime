package com.movietime.app.data.local

import android.content.Context


class TokenStorage(
    context: Context
) {

    private val preferences =
        context.getSharedPreferences(
            "movietime_auth",
            Context.MODE_PRIVATE
        )


    fun saveTokens(
        accessToken: String,
        refreshToken: String
    ) {

        preferences
            .edit()
            .putString(
                "access_token",
                accessToken
            )
            .putString(
                "refresh_token",
                refreshToken
            )
            .apply()
    }


    fun getAccessToken(): String? {

        return preferences.getString(
            "access_token",
            null
        )
    }


    fun getRefreshToken(): String? {

        return preferences.getString(
            "refresh_token",
            null
        )
    }


    fun clearTokens() {

        preferences
            .edit()
            .clear()
            .apply()
    }


    fun isLoggedIn(): Boolean {

        return !getAccessToken()
            .isNullOrBlank()
    }
}