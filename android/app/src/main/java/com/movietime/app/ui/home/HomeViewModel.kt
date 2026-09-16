package com.movietime.app.ui.home

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.movietime.app.core.error.MovieTimeExceptionHandler
import com.movietime.app.data.model.Movie
import com.movietime.app.data.remote.RetrofitClient
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch


class HomeViewModel : ViewModel() {

    private val repository =
        MovieRepository(
            RetrofitClient.movieApi
        )


    private val _movies =
        MutableStateFlow<List<Movie>>(
            emptyList()
        )

    val movies: StateFlow<List<Movie>> =
        _movies.asStateFlow()


    private val _isLoading =
        MutableStateFlow(false)

    val isLoading: StateFlow<Boolean> =
        _isLoading.asStateFlow()


    private val _errorMessage =
        MutableStateFlow<String?>(null)

    val errorMessage: StateFlow<String?> =
        _errorMessage.asStateFlow()


    fun loadMovies() {

        viewModelScope.launch {

            _isLoading.value = true

            _errorMessage.value = null

            try {

                val result =
                    repository.getMovies()

                _movies.value = result

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


    fun clearError() {

        _errorMessage.value = null
    }
}
