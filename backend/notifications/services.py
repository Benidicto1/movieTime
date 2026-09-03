from .models import Notification


class NotificationService:

    @staticmethod
    def create(
        *,
        user,
        notification_type,
        title,
        message,
    ):

        return Notification.objects.create(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message,
        )

    @staticmethod
    def mark_as_read(
        *,
        notification,
    ):

        from django.utils import timezone

        notification.is_read = True
        notification.read_at = timezone.now()

        notification.save(
            update_fields=[
                "is_read",
                "read_at",
            ]
        )

        return notification