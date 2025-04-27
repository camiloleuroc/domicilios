from django.urls import path
from .views import RegisterUser, Login, LocationAssign

urlpatterns = [
    path('register/', RegisterUser.as_view(), name='register'),
    path('login/', Login.as_view(), name='login'),
    path('locations/', LocationAssign.as_view(), name='locations'),
]