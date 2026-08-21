from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class MTNPaymentWebhookAPIView(APIView):

    authentication_classes = []
    permission_classes = []

    def post(self, request):

        payload = request.data

        # Provider-specific verification
        # will be implemented here.

        return Response(
            {
                "status": "received"
            },
            status=status.HTTP_200_OK,
        )


class AirtelPaymentWebhookAPIView(APIView):

    authentication_classes = []
    permission_classes = []

    def post(self, request):

        payload = request.data

        # Provider-specific verification
        # will be implemented here.

        return Response(
            {
                "status": "received"
            },
            status=status.HTTP_200_OK,
        )