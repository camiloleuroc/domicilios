from django.urls import path
from .views import RegisterUser, Login, LocationAssign, ServiceRequestCreate, CloseServiceRequest, DriverList, UserDetail

urlpatterns = [
    path('register/', RegisterUser.as_view(), name='register'),
    path('login/', Login.as_view(), name='login'),
    path('locations/', LocationAssign.as_view(), name='locations'),
    path('locations/<int:pk>/', LocationAssign.as_view(), name='location_detail'),
    path('delivery/', ServiceRequestCreate.as_view(), name='delivery'),
    path('endservice/', CloseServiceRequest.as_view(), name='endservice'),
    path('users/me/', UserDetail.as_view(), name='userdetail'),
    path('drivers/', DriverList.as_view(), name='drivers'),
]