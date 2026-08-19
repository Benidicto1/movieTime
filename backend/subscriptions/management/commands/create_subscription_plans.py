from django.core.management.base import BaseCommand

from subscriptions.models import SubscriptionPlan


class Command(BaseCommand):

    help = "Create or update MovieTime subscription plans"

    def handle(self, *args, **options):

        plans = [
            {
                "name": "Day",
                "plan_type": SubscriptionPlan.PlanType.DAY,
                "price": 900,
                "duration_days": 1,
            },
            {
                "name": "Week",
                "plan_type": SubscriptionPlan.PlanType.WEEK,
                "price": 2000,
                "duration_days": 7,
            },
            {
                "name": "Month",
                "plan_type": SubscriptionPlan.PlanType.MONTH,
                "price": 4500,
                "duration_days": 30,
            },
        ]

        for plan_data in plans:

            plan, created = (
                SubscriptionPlan.objects.update_or_create(
                    plan_type=plan_data["plan_type"],
                    defaults={
                        "name": plan_data["name"],
                        "price": plan_data["price"],
                        "duration_days": plan_data[
                            "duration_days"
                        ],
                        "is_active": True,
                    },
                )
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created {plan.name} plan."
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Updated {plan.name} plan."
                    )
                )