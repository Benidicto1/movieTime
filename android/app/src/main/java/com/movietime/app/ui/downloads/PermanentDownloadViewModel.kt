package com.movietime.app.ui.downloads

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.movietime.app.data.download.DownloadRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch


sealed class DownloadUiState {

    data object Idle : DownloadUiState()

    data object Loading : DownloadUiState()

    data class Success(
        val downloadId: Long
    ) : DownloadUiState()

    data class Error(
        val message: String
    ) : DownloadUiState()
}


class PermanentDownloadViewModel(
    private val repository: DownloadRepository
) : ViewModel() {

    private val _uiState =
        MutableStateFlow<DownloadUiState>(
            DownloadUiState.Idle
        )

    val uiState: StateFlow<DownloadUiState> =
        _uiState.asStateFlow()


    fun downloadMovie(
        movieId: Int
    ) {

        viewModelScope.launch {

            _uiState.value =
                DownloadUiState.Loading

            try {

                val downloadId =
                    repository.downloadMovie(
                        movieId = movieId
                    )

                _uiState.value =
                    DownloadUiState.Success(
                        downloadId = downloadId
                    )

            } catch (exception: Exception) {

                _uiState.value =
                    DownloadUiState.Error(
                        message =
                            exception.message
                                ?: "Download failed."
                    )
            }
        }
    }


    fun resetState() {

        _uiState.value =
            DownloadUiState.Idle
    }
}