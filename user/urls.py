from django.urls import path
from .views import SignUpAPIView, SignInAPIView, LogoutAPIView

urlpatterns = [
    path('signup/', SignUpAPIView.as_view(), name='signup'),
    path('signin/', SignInAPIView.as_view(), name='signin'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
]
