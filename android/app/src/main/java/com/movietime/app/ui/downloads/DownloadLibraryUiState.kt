package com.movietime.app.ui.downloads

import com.movietime.app.data.model.DownloadedMovie

data class DownloadLibraryUiState(
    val movies: List<DownloadedMovie> = emptyList(),
    val isLoading: Boolean = false,
    val errorMessage: String? = null
)
