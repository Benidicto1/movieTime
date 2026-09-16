package com.movietime.app.ui.details

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.movietime.app.core.error.MovieTimeExceptionHandler
import com.movietime.app.data.remote.RetrofitClient
import com.movietime.app.data.repository.MovieRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class MovieDownloadViewModel : ViewModel() {

    private val repository =
        MovieRepository(
            RetrofitClient.movieApi
        )

    private val _downloadUrl =
        MutableStateFlow<String?>(null)

    val downloadUrl: StateFlow<String?> =
        _downloadUrl.asStateFlow()

    private val _isLoading =
        MutableStateFlow(false)

    val isLoading: StateFlow<Boolean> =
        _isLoading.asStateFlow()

    private val _errorMessage =
        MutableStateFlow<String?>(null)

    val errorMessage: StateFlow<String?> =
        _errorMessage.asStateFlow()

    fun requestDownload(
        movieId: Int
    ) {

        viewModelScope.launch {

            _isLoading.value = true
            _errorMessage.value = null
            _downloadUrl.value = null

            try {

                val response =
                    repository.getMovieDownload(
                        movieId
                    )

                _downloadUrl.value =
                    response.downloadUrl

            } catch (exception: Exception) {

                _errorMessage.value =
                    MovieTimeExceptionHandler
                        .getErrorMessage(
                            exception
                        )
            }

            _isLoading.value = false
        }
    }

    fun clearDownloadUrl() {
        _downloadUrl.value = null
    }

    fun clearError() {
        _errorMessage.value = null
    }
}