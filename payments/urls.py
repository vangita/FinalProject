from django.urls import path
from .views import PaymentViewSet

urlpatterns = [
    path('payment/', PaymentViewSet.as_view(), name='create-payment'),
]
