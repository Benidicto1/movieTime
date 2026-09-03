from django.contrib import admin

from .models import (
    SubscriptionPlan,
    Subscription,
    SubscriptionOrder,
)


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "plan_type",
        "price",
        "duration_days",
        "is_active",
    )

    list_filter = (
        "plan_type",
        "is_active",
    )

    search_fields = (
        "name",
    )

    ordering = (
        "price",
    )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "plan",
        "status",
        "started_at",
        "expires_at",
        "created_at",
    )

    list_filter = (
        "status",
        "plan",
    )

    search_fields = (
        "user__username",
    )

    ordering = (
        "-created_at",
    )


@admin.register(SubscriptionOrder)
class SubscriptionOrderAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "plan",
        "amount",
        "currency",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "plan",
        "currency",
    )

    search_fields = (
        "user__username",
    )

    ordering = (
        "-created_at",
    )