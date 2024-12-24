from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Payment
from .serializers import PaymentSerializer
import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['POST'])
    def process_payment(self, request, pk=None):
        payment = self.get_object()

        try:
            intent = stripe.PaymentIntent.create(
                amount=int(payment.amount * 100),
                currency='usd',
                payment_method_types=['card'],
                metadata={'payment_id': payment.id}
            )

            payment.stripe_payment_intent_id = intent.id
            payment.save()

            return Response({
                'client_secret': intent.client_secret
            })

        except stripe.error.StripeError as e:
            return Response({'error': str(e)}, status=400)
