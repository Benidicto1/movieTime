# backend/payments/admin.py

from django.contrib import admin

from payments.models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """
    Django Admin configuration for MovieTime payments.

    Sensitive information such as mobile-money phone numbers,
    API credentials, access tokens, and callback secrets must
    never be stored or displayed through the Payment admin.
    """

    list_display = (
        "external_reference",
        "user",
        "target",
        "provider",
        "amount",
        "currency",
        "status",
        "provider_reference",
        "created_at",
        "completed_at",
    )

    list_filter = (
        "provider",
        "status",
        "currency",
        "created_at",
        "completed_at",
    )

    search_fields = (
        "external_reference",
        "provider_reference",
        "user__username",
        "user__email",
    )

    readonly_fields = (
        "external_reference",
        "user",
        "order",
        "purchase",
        "provider",
        "amount",
        "currency",
        "status",
        "provider_reference",
        "failure_reason",
        "created_at",
        "updated_at",
        "completed_at",
    )

    ordering = (
        "-created_at",
    )

    list_per_page = 50

    date_hierarchy = "created_at"

    fieldsets = (
        (
            "Payment",
            {
                "fields": (
                    "external_reference",
                    "user",
                    "provider",
                    "amount",
                    "currency",
                    "status",
                ),
            },
        ),
        (
            "Payment Target",
            {
                "fields": (
                    "purchase",
                    "order",
                ),
            },
        ),
        (
            "Provider Information",
            {
                "fields": (
                    "provider_reference",
                    "failure_reason",
                ),
            },
        ),
        (
            "Timestamps",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                    "completed_at",
                ),
            },
        ),
    )

    def target(self, obj):
        """
        Display the payment target in the admin list.

        A payment should have exactly one target:
            - Purchase
            - SubscriptionOrder
        """

        if obj.purchase_id is not None:
            return f"Purchase #{obj.purchase_id}"

        if obj.order_id is not None:
            return f"Subscription Order #{obj.order_id}"

        return "No target"

    target.short_description = "Target"

    def has_add_permission(self, request):
        """
        Prevent administrators from manually creating payments.

        Payments should be created by the MovieTime payment service
        so that ownership, amount, currency, and payment state
        are controlled by the application.
        """

        return False

    def has_delete_permission(self, request, obj=None):
        """
        Prevent deletion of payment records.

        Payment records are financial/audit records and should
        normally be retained rather than deleted.
        """

        return False