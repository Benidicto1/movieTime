package com.movietime.app.ui.purchases

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.movietime.app.core.error.MovieTimeExceptionHandler
import com.movietime.app.data.model.PurchaseHistoryItem
import com.movietime.app.data.remote.RetrofitClient
import com.movietime.app.data.repository.MovieRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class PurchaseHistoryViewModel : ViewModel() {

    private val repository =
        MovieRepository(
            RetrofitClient.movieApi
        )

    private val _purchases =
        MutableStateFlow<List<PurchaseHistoryItem>>(
            emptyList()
        )

    val purchases:
            StateFlow<List<PurchaseHistoryItem>> =
        _purchases.asStateFlow()

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


    fun loadPurchaseHistory() {

        viewModelScope.launch {

            _isLoading.value = true
            _errorMessage.value = null

            try {

                val result =
                    repository.getPurchaseHistory()

                _purchases.value = result

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