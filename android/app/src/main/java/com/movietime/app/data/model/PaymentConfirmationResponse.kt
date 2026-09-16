package com.movietime.app.data.model

/**
 * Represents the result of a payment status check.
 *
 * Chapter 73:
 * Payment confirmation is performed by the backend/provider.
 * The Android application must never declare a payment successful
 * by itself.
 */
data class PaymentConfirmationResponse(
    val payment_id: Int,
    val status: String,
    val amount: String,
    val currency: String,
    val payment_method: String,
    val external_reference: String,
    val provider_reference: String?,
    val completed_at: String?,
    val purchase_id: Int?,
    val order_id: Int?
)