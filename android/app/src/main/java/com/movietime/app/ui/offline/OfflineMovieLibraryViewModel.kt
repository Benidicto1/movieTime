package com.movietime.app.ui.offline

import androidx.lifecycle.ViewModel
import com.movietime.app.data.local.OfflineMovie
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow


class OfflineMovieLibraryViewModel : ViewModel() {

    private val _movies =
        MutableStateFlow<List<OfflineMovie>>(
            emptyList()
        )

    val movies: StateFlow<List<OfflineMovie>> =
        _movies.asStateFlow()

    private val _isLoading =
        MutableStateFlow(false)

    val isLoading: StateFlow<Boolean> =
        _isLoading.asStateFlow()

    fun loadOfflineMovies() {

        _isLoading.value = true

        /*
         * The actual downloaded-file database
         * will be connected here.
         *
         * Chapter 62 establishes the offline
         * library UI/state structure.
         */

        _movies.value = emptyList()

        _isLoading.value = false
    }
}