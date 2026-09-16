package com.movietime.app.data.model

data class MovieOwnershipResponse(
    val movieId: Int,
    val owned: Boolean,
    val purchaseId: Int?,
    val paymentStatus: String?,
    val ownershipStatus: String
)