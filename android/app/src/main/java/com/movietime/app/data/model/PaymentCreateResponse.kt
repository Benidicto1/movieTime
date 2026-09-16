package com.movietime.app.data.model

data class PaymentCreateResponse(
    val payment_id: Int,
    val amount: String,
    val currency: String,
    val payment_method: String,
    val payment_status: String,
    val external_reference: String,
    val provider_reference: String?,
    val message: String,
    val purchase_id: Int?,
    val order_id: Int?
)