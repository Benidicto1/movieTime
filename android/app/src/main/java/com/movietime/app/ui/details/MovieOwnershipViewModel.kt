package com.movietime.app.ui.details

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.movietime.app.core.error.MovieTimeExceptionHandler
import com.movietime.app.data.model.MovieOwnershipResponse
import com.movietime.app.data.remote.RetrofitClient
import com.movietime.app.data.repository.MovieRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class MovieOwnershipViewModel : ViewModel() {

    private val repository =
        MovieRepository(
            RetrofitClient.movieApi
        )


    private val _ownership =
        MutableStateFlow<MovieOwnershipResponse?>(null)

    val ownership:
            StateFlow<MovieOwnershipResponse?> =
        _ownership.asStateFlow()


    private val _isLoading =
        MutableStateFlow(false)

    val isLoading:
            StateFlow<Boolean> =
        _isLoading.asStateFlow()


    private val _errorMessage =
        MutableStateFlow<String?>(null)

    val errorMessage:
            StateFlow<String?> =
        _errorMessage.asStateFlow()


    fun loadOwnership(
        movieId: Int
    ) {

        viewModelScope.launch {

            _isLoading.value = true

            _errorMessage.value = null

            _ownership.value = null


            try {

                val result =
                    repository.getMovieOwnership(
                        movieId
                    )

                _ownership.value =
                    result

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


    fun clearOwnership() {

        _ownership.value = null
    }


    fun clearError() {

        _errorMessage.value = null
    }
}