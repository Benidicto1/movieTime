package com.movietime.app.data.model

data class PaymentResponse(
    val orderId: Int,
    val paymentId: Int,
    val planId: Int,
    val amount: String,
    val currency: String,
    val paymentMethod: String,
    val paymentStatus: String,
    val externalReference: String,
    val phoneNumber: String,
    val message: String
)