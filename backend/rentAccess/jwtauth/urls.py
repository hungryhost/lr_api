from .views import registration, login, logout, logout_all, email_verification
from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from rest_framework_simplejwt.views import TokenVerifyView
app_name = 'jwtauth'
urlpatterns = [
    path('register/', registration, name='register'),
    path('token/', login, name='token_obtain_pair'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('logout/', logout, name='logout'),
    path('logoutall/', logout_all, name='logout_all'),
    path('email_verification/', email_verification, name='email_verification'),
]
