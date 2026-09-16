package com.movietime.app.data.model

data class PaymentStatusResponse(
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