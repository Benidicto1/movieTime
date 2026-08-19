# purchases/views.py

from django.shortcuts import get_object_or_404

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from movies.models import Movie

from .models import Purchase
from .serializers import PurchaseSerializer
from .services import PurchaseService


class PurchaseListAPIView(generics.ListAPIView):
    serializer_class = PurchaseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Purchase.objects.filter(
            user=self.request.user
        ).select_related("movie")


class PurchaseCreateAPIView(generics.CreateAPIView):
    serializer_class = PurchaseSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        movie_id = request.data.get("movie")

        movie = get_object_or_404(
            Movie,
            id=movie_id,
        )

        try:
            purchase = PurchaseService.create_pending_purchase(
                user=request.user,
                movie=movie,
            )

        except ValueError as exc:
            return Response(
                {
                    "detail": str(exc),
                },
                status=400,
            )

        serializer = self.get_serializer(purchase)

        return Response(
            serializer.data,
            status=201,
        )