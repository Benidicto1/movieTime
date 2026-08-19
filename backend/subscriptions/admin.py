from django.contrib import admin
from django.contrib import admin

from .models import (
    Subscription,
    SubscriptionOrder,
    SubscriptionPlan,
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


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "plan",
        "status",
        "started_at",
        "expires_at",
    )

    list_filter = (
        "status",
        "plan",
    )

    search_fields = (
        "user__username",
        "user__email",
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
        "user__email",
    )