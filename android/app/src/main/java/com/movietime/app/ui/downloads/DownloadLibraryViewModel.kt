package com.movietime.app.ui.downloads

import androidx.lifecycle.ViewModel

import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow


class DownloadLibraryViewModel : ViewModel() {

    private val _uiState =
        MutableStateFlow(
            DownloadLibraryUiState()
        )

    val uiState: StateFlow<DownloadLibraryUiState> =
        _uiState.asStateFlow()


    fun loadDownloads() {

        /*
         * The local download database will be
         * connected in a later chapter.
         *
         * For now, the library starts empty.
         */

        _uiState.value =
            DownloadLibraryUiState(
                movies = emptyList(),
                isLoading = false
            )
    }


    fun clearError() {

        _uiState.value =
            _uiState.value.copy(
                errorMessage = null
            )
    }
}
