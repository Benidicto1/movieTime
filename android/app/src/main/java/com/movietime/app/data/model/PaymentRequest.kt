package com.movietime.app.data.model

data class PaymentRequest(
    val planId: Int,
    val paymentMethod: String,
    val phoneNumber: String
)

