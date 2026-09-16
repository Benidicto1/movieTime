package com.movietime.app.data.auth

import android.content.Context

class TokenManager(
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
        preferences.edit()
            .putString(
                KEY_ACCESS_TOKEN,
                accessToken
            )
            .putString(
                KEY_REFRESH_TOKEN,
                refreshToken
            )
            .apply()
    }

    fun getAccessToken(): String? {
        return preferences.getString(
            KEY_ACCESS_TOKEN,
            null
        )
    }

    fun getRefreshToken(): String? {
        return preferences.getString(
            KEY_REFRESH_TOKEN,
            null
        )
    }

    fun clearTokens() {
        preferences.edit()
            .remove(KEY_ACCESS_TOKEN)
            .remove(KEY_REFRESH_TOKEN)
            .apply()
    }

    fun isLoggedIn(): Boolean {
        return getAccessToken() != null
    }

    companion object {

        private const val KEY_ACCESS_TOKEN =
            "access_token"

        private const val KEY_REFRESH_TOKEN =
            "refresh_token"
    }
}