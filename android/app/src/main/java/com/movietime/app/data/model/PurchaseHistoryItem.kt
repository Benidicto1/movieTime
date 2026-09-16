package com.movietime.app.data.model

data class PurchaseHistoryItem(
    val id: Int,
    val movieId: Int,
    val movieTitle: String,
    val amount: String,
    val purchaseDate: String,
    val paymentStatus: String,
    val ownershipStatus: String
)