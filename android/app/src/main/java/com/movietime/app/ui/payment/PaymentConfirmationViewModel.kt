package com.movietime.app.ui.payment

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.movietime.app.data.model.PaymentStatusResponse
import com.movietime.app.data.repository.PaymentRepository
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class PaymentConfirmationViewModel(
    private val paymentRepository: PaymentRepository
) : ViewModel() {

    companion object {
        private const val POLLING_INTERVAL_MS = 3_000L
        private const val MAX_POLLING_ATTEMPTS = 30
    }

    private val _paymentState =
        MutableStateFlow<PaymentConfirmationState>(
            PaymentConfirmationState.Idle
        )

    val paymentState: StateFlow<PaymentConfirmationState> =
        _paymentState.asStateFlow()

    private var pollingJob: Job? = null

    /**
     * Starts checking the payment status.
     *
     * The Android application does NOT mark the payment as successful.
     * Django determines the authoritative payment state.
     */
    fun startPaymentStatusPolling(
        paymentId: Int
    ) {

        if (paymentId <= 0) {
            _paymentState.value =
                PaymentConfirmationState.Error(
                    "Invalid payment ID."
                )
            return
        }

        pollingJob?.cancel()

        pollingJob = viewModelScope.launch {

            _paymentState.value =
                PaymentConfirmationState.Checking

            repeat(MAX_POLLING_ATTEMPTS) { attempt ->

                val result =
                    paymentRepository.getPaymentStatus(
                        paymentId
                    )

                result
                    .onSuccess { response ->

                        val state =
                            PaymentState.fromApiValue(
                                response.status
                            )

                        when (state) {

                            PaymentState.SUCCESS -> {

                                _paymentState.value =
                                    PaymentConfirmationState.Success(
                                        response
                                    )

                                cancelPolling()
                            }

                            PaymentState.FAILED -> {

                                _paymentState.value =
                                    PaymentConfirmationState.Failed(
                                        response
                                    )

                                cancelPolling()
                            }

                            PaymentState.CANCELLED -> {

                                _paymentState.value =
                                    PaymentConfirmationState.Cancelled(
                                        response
                                    )

                                cancelPolling()
                            }

                            PaymentState.PROCESSING,
                            PaymentState.PENDING -> {

                                _paymentState.value =
                                    PaymentConfirmationState.Processing(
                                        response
                                    )
                            }
                        }
                    }
                    .onFailure { exception ->

                        /*
                         * Do not immediately declare the payment
                         * failed because of a temporary network error.
                         *
                         * The next polling attempt can recover.
                         */
                        if (attempt == MAX_POLLING_ATTEMPTS - 1) {

                            _paymentState.value =
                                PaymentConfirmationState.Error(
                                    exception.message
                                        ?: "Unable to check payment status."
                                )
                        }
                    }

                if (pollingJob?.isActive != true) {
                    return@launch
                }

                if (attempt < MAX_POLLING_ATTEMPTS - 1) {
                    delay(POLLING_INTERVAL_MS)
                }
            }

            if (pollingJob?.isActive == true) {

                _paymentState.value =
                    PaymentConfirmationState.Timeout

                pollingJob = null
            }
        }
    }

    /**
     * Manually checks the payment once.
     */
    fun checkPaymentStatus(
        paymentId: Int
    ) {

        if (paymentId <= 0) {
            _paymentState.value =
                PaymentConfirmationState.Error(
                    "Invalid payment ID."
                )
            return
        }

        viewModelScope.launch {

            _paymentState.value =
                PaymentConfirmationState.Checking

            paymentRepository
                .getPaymentStatus(paymentId)
                .onSuccess { response ->

                    updateStateFromResponse(response)
                }
                .onFailure { exception ->

                    _paymentState.value =
                        PaymentConfirmationState.Error(
                            exception.message
                                ?: "Unable to check payment status."
                        )
                }
        }
    }

    /**
     * Stops payment polling.
     */
    fun cancelPolling() {

        pollingJob?.cancel()
        pollingJob = null
    }

    /**
     * Clears the current payment state.
     */
    fun resetState() {

        cancelPolling()

        _paymentState.value =
            PaymentConfirmationState.Idle
    }

    private fun updateStateFromResponse(
        response: PaymentStatusResponse
    ) {

        when (
            PaymentState.fromApiValue(response.status)
        ) {

            PaymentState.SUCCESS -> {
                _paymentState.value =
                    PaymentConfirmationState.Success(
                        response
                    )
            }

            PaymentState.FAILED -> {
                _paymentState.value =
                    PaymentConfirmationState.Failed(
                        response
                    )
            }

            PaymentState.CANCELLED -> {
                _paymentState.value =
                    PaymentConfirmationState.Cancelled(
                        response
                    )
            }

            PaymentState.PROCESSING,
            PaymentState.PENDING -> {
                _paymentState.value =
                    PaymentConfirmationState.Processing(
                        response
                    )
            }
        }
    }

    override fun onCleared() {

        cancelPolling()

        super.onCleared()
    }
}


/**
 * UI state for the payment confirmation screen.
 */
sealed interface PaymentConfirmationState {

    data object Idle : PaymentConfirmationState

    data object Checking : PaymentConfirmationState

    data class Processing(
        val payment: PaymentStatusResponse
    ) : PaymentConfirmationState

    data class Success(
        val payment: PaymentStatusResponse
    ) : PaymentConfirmationState

    data class Failed(
        val payment: PaymentStatusResponse
    ) : PaymentConfirmationState

    data class Cancelled(
        val payment: PaymentStatusResponse
    ) : PaymentConfirmationState

    data object Timeout : PaymentConfirmationState

    data class Error(
        val message: String
    ) : PaymentConfirmationState
}


/**
 * Backend payment states understood by the Android application.
 */
enum class PaymentState {

    PENDING,
    PROCESSING,
    SUCCESS,
    FAILED,
    CANCELLED;

    companion object {

        fun fromApiValue(
            value: String?
        ): PaymentState {

            return when (
                value
                    ?.trim()
                    ?.uppercase()
            ) {

                "PENDING" ->
                    PENDING

                "PROCESSING" ->
                    PROCESSING

                "SUCCESS",
                "SUCCESSFUL",
                "COMPLETED",
                "PAID" ->
                    SUCCESS

                "FAILED",
                "FAILURE" ->
                    FAILED

                "CANCELLED",
                "CANCELED" ->
                    CANCELLED

                else ->
                    PROCESSING
            }
        }
    }
}