package com.movietime.app.data.repository

import com.movietime.app.data.model.PaymentCreateResponse
import com.movietime.app.data.model.PaymentStatusResponse
import com.movietime.app.data.remote.PaymentApiService

/**
 * Repository responsible for MovieTime payment operations.
 *
 * Important security rule:
 * The Android application never confirms or completes a payment.
 *
 * Android only:
 * 1. Requests payment creation.
 * 2. Receives the payment ID.
 * 3. Checks the payment status.
 *
 * The Django backend is responsible for communicating with MTN/Airtel
 * and determining whether the payment is actually successful.
 */
class PaymentRepository(
    private val paymentApiService: PaymentApiService
) {

    /**
     * Create a payment for a permanent movie purchase.
     *
     * The purchase ID identifies an existing backend purchase.
     * The backend determines the authoritative amount and currency.
     *
     * @param purchaseId Backend purchase ID.
     * @param paymentMethod MTN or AIRTEL.
     * @param phoneNumber Uganda mobile-money number.
     *
     * @return PaymentCreateResponse from Django.
     */
    suspend fun createPurchasePayment(
        purchaseId: Int,
        paymentMethod: String,
        phoneNumber: String
    ): PaymentCreateResponse {
        return paymentApiService.createPurchasePayment(
            purchaseId = purchaseId,
            paymentMethod = paymentMethod,
            phoneNumber = phoneNumber
        )
    }

    /**
     * Create a payment for a subscription.
     *
     * The backend determines the subscription price from the
     * selected SubscriptionPlan.
     *
     * @param planId Backend subscription plan ID.
     * @param paymentMethod MTN or AIRTEL.
     * @param phoneNumber Uganda mobile-money number.
     *
     * @return PaymentCreateResponse from Django.
     */
    suspend fun createSubscriptionPayment(
        planId: Int,
        paymentMethod: String,
        phoneNumber: String
    ): PaymentCreateResponse {
        return paymentApiService.createSubscriptionPayment(
            planId = planId,
            paymentMethod = paymentMethod,
            phoneNumber = phoneNumber
        )
    }

    /**
     * Retrieve the current status of a payment.
     *
     * This is intentionally a GET/read operation.
     *
     * Android does NOT send a SUCCESS status to the backend.
     * Django determines the status using trusted payment-provider
     * verification/callback processing.
     *
     * @param paymentId Backend payment ID.
     *
     * @return PaymentStatusResponse from Django.
     */
    suspend fun getPaymentStatus(
        paymentId: Int
    ): PaymentStatusResponse {
        return paymentApiService.getPaymentStatus(
            paymentId = paymentId
        )
    }
}