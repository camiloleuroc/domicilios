from django.urls import path
from .views import RegisterUser, Login

urlpatterns = [
    path('register/', RegisterUser.as_view(), name='register'),
    path('login/', Login.as_view(), name='login'),
]