package com.movietime.app.core.error


object MovieTimeExceptionHandler {

    fun getErrorMessage(
        throwable: Throwable
    ): String {

        val error =
            ApiErrorHandler.handle(
                throwable
            )

        return ErrorMessageMapper.getMessage(
            error
        )
    }
}