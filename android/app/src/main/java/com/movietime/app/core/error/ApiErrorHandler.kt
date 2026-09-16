package com.movietime.app.core.error

import java.io.IOException
import java.net.SocketTimeoutException


object ApiErrorHandler {

    fun handle(
        throwable: Throwable
    ): MovieTimeError {

        return when (throwable) {

            is SocketTimeoutException -> {
                MovieTimeError.Timeout
            }

            is IOException -> {
                MovieTimeError.Network
            }

            else -> {
                MovieTimeError.Unknown
            }
        }
    }
}
