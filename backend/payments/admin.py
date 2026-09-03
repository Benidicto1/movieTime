from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "order",
        "purchase",
        "provider",
        "amount",
        "currency",
        "status",
        "created_at",
        "completed_at",
    )

    list_filter = (
        "provider",
        "status",
        "currency",
    )

    search_fields = (
        "user__username",
        "user__email",
        "provider_reference",
        "external_reference",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "completed_at",
    )