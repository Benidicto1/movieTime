from django.utils import timezone

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Notification
from .serializers import NotificationSerializer


class NotificationListAPIView(
    generics.ListAPIView
):

    serializer_class = NotificationSerializer

    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):

        return Notification.objects.filter(
            user=self.request.user,
        ).order_by(
            "-created_at"
        )


class NotificationReadAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    def post(
        self,
        request,
        notification_id,
    ):

        notification = (
            Notification.objects
            .filter(
                id=notification_id,
                user=request.user,
            )
            .first()
        )

        if notification is None:

            return Response(
                {
                    "detail": (
                        "Notification not found."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        notification.is_read = True
        notification.read_at = timezone.now()

        notification.save(
            update_fields=[
                "is_read",
                "read_at",
            ]
        )

        return Response(
            {
                "detail": (
                    "Notification marked as read."
                )
            }
        )



class NotificationUnreadCountAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request):

        unread_count = Notification.objects.filter(
            user=request.user,
            is_read=False,
        ).count()

        return Response(
            {
                "unread_count": unread_count,
            }
        )