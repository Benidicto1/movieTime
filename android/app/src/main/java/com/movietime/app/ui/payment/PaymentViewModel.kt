package com.movietime.app.ui.payment

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import com.movietime.app.data.model.PaymentCreateResponse
import com.movietime.app.data.model.PaymentState
import com.movietime.app.data.model.PaymentStatusResponse
import com.movietime.app.data.repository.PaymentRepository
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

/**
 * ViewModel for MovieTime payment operations.
 *
 * Security model:
 *
 * Android can:
 * - request creation of a payment
 * - observe payment status
 * - display payment results
 *
 * Android cannot:
 * - mark a payment as SUCCESS
 * - confirm a payment manually
 * - change the payment amount
 * - change the payment ownership
 *
 * The Django backend is the authority for payment completion.
 */
class PaymentViewModel(
    private val repository: PaymentRepository
) : ViewModel() {

    private val _paymentState =
        MutableStateFlow<PaymentState>(PaymentState.PENDING)

    val paymentState: StateFlow<PaymentState> =
        _paymentState.asStateFlow()

    private val _payment =
        MutableStateFlow<PaymentCreateResponse?>(null)

    val payment: StateFlow<PaymentCreateResponse?> =
        _payment.asStateFlow()

    private val _paymentStatus =
        MutableStateFlow<PaymentStatusResponse?>(null)

    val paymentStatus: StateFlow<PaymentStatusResponse?> =
        _paymentStatus.asStateFlow()

    private val _isLoading =
        MutableStateFlow(false)

    val isLoading: StateFlow<Boolean> =
        _isLoading.asStateFlow()

    private val _errorMessage =
        MutableStateFlow<String?>(null)

    val errorMessage: StateFlow<String?> =
        _errorMessage.asStateFlow()

    private var pollingJob: Job? = null

    /**
     * Create a payment for a permanent movie purchase.
     *
     * The backend determines the actual purchase amount.
     */
    fun createPurchasePayment(
        purchaseId: Int,
        paymentMethod: String,
        phoneNumber: String
    ) {
        if (purchaseId <= 0) {
            _errorMessage.value = "Invalid purchase."
            return
        }

        if (phoneNumber.isBlank()) {
            _errorMessage.value = "Enter your mobile-money number."
            return
        }

        if (!isSupportedPaymentMethod(paymentMethod)) {
            _errorMessage.value = "Unsupported payment method."
            return
        }

        cancelPolling()

        viewModelScope.launch {
            _isLoading.value = true
            _errorMessage.value = null
            _paymentState.value = PaymentState.PENDING

            try {
                val response = repository.createPurchasePayment(
                    purchaseId = purchaseId,
                    paymentMethod = paymentMethod,
                    phoneNumber = phoneNumber
                )

                _payment.value = response

                val state = PaymentState.fromApiValue(
                    response.payment_status
                )

                _paymentState.value = state

                if (
                    state == PaymentState.PENDING ||
                    state == PaymentState.PROCESSING
                ) {
                    startPolling(response.payment_id)
                }
            } catch (exception: Exception) {
                _paymentState.value = PaymentState.FAILED
                _errorMessage.value =
                    exception.message ?: "Unable to create payment."
            } finally {
                _isLoading.value = false
            }
        }
    }

    /**
     * Create a payment for a subscription.
     *
     * The backend determines the actual subscription price.
     */
    fun createSubscriptionPayment(
        planId: Int,
        paymentMethod: String,
        phoneNumber: String
    ) {
        if (planId <= 0) {
            _errorMessage.value = "Invalid subscription plan."
            return
        }

        if (phoneNumber.isBlank()) {
            _errorMessage.value = "Enter your mobile-money number."
            return
        }

        if (!isSupportedPaymentMethod(paymentMethod)) {
            _errorMessage.value = "Unsupported payment method."
            return
        }

        cancelPolling()

        viewModelScope.launch {
            _isLoading.value = true
            _errorMessage.value = null
            _paymentState.value = PaymentState.PENDING

            try {
                val response = repository.createSubscriptionPayment(
                    planId = planId,
                    paymentMethod = paymentMethod,
                    phoneNumber = phoneNumber
                )

                _payment.value = response

                val state = PaymentState.fromApiValue(
                    response.payment_status
                )

                _paymentState.value = state

                if (
                    state == PaymentState.PENDING ||
                    state == PaymentState.PROCESSING
                ) {
                    startPolling(response.payment_id)
                }
            } catch (exception: Exception) {
                _paymentState.value = PaymentState.FAILED
                _errorMessage.value =
                    exception.message ?: "Unable to create payment."
            } finally {
                _isLoading.value = false
            }
        }
    }

    /**
     * Retrieve the current payment status once.
     *
     * This is a read-only operation.
     */
    fun refreshPaymentStatus(paymentId: Int) {
        if (paymentId <= 0) {
            _errorMessage.value = "Invalid payment."
            return
        }

        viewModelScope.launch {
            try {
                val response =
                    repository.getPaymentStatus(paymentId)

                _paymentStatus.value = response

                val state = PaymentState.fromApiValue(
                    response.status
                )

                _paymentState.value = state

                if (isTerminalState(state)) {
                    cancelPolling()
                }
            } catch (exception: Exception) {
                _errorMessage.value =
                    exception.message ?: "Unable to check payment status."
            }
        }
    }

    /**
     * Start polling the backend for payment status.
     *
     * Polling is deliberately limited so that the application does
     * not continuously contact the backend.
     */
    private fun startPolling(
        paymentId: Int,
        intervalMillis: Long = 3_000L,
        maximumAttempts: Int = 30
    ) {
        cancelPolling()

        pollingJob = viewModelScope.launch {

            repeat(maximumAttempts) {

                try {
                    val response =
                        repository.getPaymentStatus(paymentId)

                    _paymentStatus.value = response

                    val state = PaymentState.fromApiValue(
                        response.status
                    )

                    _paymentState.value = state

                    if (isTerminalState(state)) {
                        return@launch
                    }

                    delay(intervalMillis)

                } catch (exception: Exception) {
                    _errorMessage.value =
                        exception.message
                            ?: "Unable to check payment status."

                    return@launch
                }
            }

            /*
             * The payment may still be processing on the provider.
             *
             * We intentionally do NOT mark it as FAILED just because
             * our polling window ended.
             */
            if (_paymentState.value == PaymentState.PENDING ||
                _paymentState.value == PaymentState.PROCESSING
            ) {
                _errorMessage.value =
                    "Payment is still being processed. Check again later."
            }
        }
    }

    /**
     * Stop payment-status polling.
     */
    fun cancelPolling() {
        pollingJob?.cancel()
        pollingJob = null
    }

    /**
     * Clear the current error message.
     */
    fun clearError() {
        _errorMessage.value = null
    }

    /**
     * Reset the current payment UI state.
     *
     * This does NOT change anything on the backend.
     */
    fun resetPaymentState() {
        cancelPolling()

        _payment.value = null
        _paymentStatus.value = null
        _errorMessage.value = null
        _isLoading.value = false
        _paymentState.value = PaymentState.PENDING
    }

    /**
     * Check whether a payment state is terminal.
     */
    private fun isTerminalState(
        state: PaymentState
    ): Boolean {
        return when (state) {
            PaymentState.SUCCESS,
            PaymentState.FAILED,
            PaymentState.CANCELLED -> true

            PaymentState.PENDING,
            PaymentState.PROCESSING -> false
        }
    }

    /**
     * Only supported MovieTime mobile-money providers.
     */
    private fun isSupportedPaymentMethod(
        paymentMethod: String
    ): Boolean {
        return when (paymentMethod.trim().uppercase()) {
            "MTN",
            "AIRTEL" -> true

            else -> false
        }
    }

    override fun onCleared() {
        cancelPolling()
        super.onCleared()
    }

    companion object {

        /**
         * Factory used when creating PaymentViewModel from Compose
         * or an Activity/Fragment.
         */
        fun factory(
            repository: PaymentRepository
        ): ViewModelProvider.Factory {

            return object : ViewModelProvider.Factory {

                @Suppress("UNCHECKED_CAST")
                override fun <T : ViewModel> create(
                    modelClass: Class<T>
                ): T {

                    if (
                        modelClass.isAssignableFrom(
                            PaymentViewModel::class.java
                        )
                    ) {
                        return PaymentViewModel(
                            repository
                        ) as T
                    }

                    throw IllegalArgumentException(
                        "Unknown ViewModel class: ${modelClass.name}"
                    )
                }
            }
        }
    }
}