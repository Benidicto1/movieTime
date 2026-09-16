package com.movietime.app.data.model

/**
 * Represents the lifecycle state of a MovieTime payment.
 *
 * The Android application only observes these states.
 * It must never change a payment to SUCCESS by itself.
 */
enum class PaymentState {

    /**
     * Payment has been created but has not yet been submitted
     * or accepted by the payment provider.
     */
    PENDING,

    /**
     * Payment request has been submitted to MTN or Airtel
     * and is waiting for final provider confirmation.
     */
    PROCESSING,

    /**
     * Backend/provider verification confirms that payment
     * was successfully completed.
     */
    SUCCESS,

    /**
     * Payment provider or backend verification reports failure.
     */
    FAILED,

    /**
     * Payment was cancelled and will not be completed.
     */
    CANCELLED;

    companion object {

        /**
         * Safely converts the status returned by Django into
         * the corresponding PaymentState.
         *
         * Unknown values are treated as PROCESSING rather than
         * SUCCESS. This prevents an unexpected backend status
         * from accidentally unlocking paid content.
         */
        fun fromApiValue(value: String?): PaymentState {
            return when (value?.trim()?.uppercase()) {
                "PENDING" -> PENDING
                "PROCESSING" -> PROCESSING
                "SUCCESS" -> SUCCESS
                "FAILED" -> FAILED
                "CANCELLED" -> CANCELLED
                else -> PROCESSING
            }
        }
    }
}