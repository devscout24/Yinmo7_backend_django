from django.urls import path
from .views import SetNewPasswordView, SignupView,SigninView,VerifyOTPView,ForgetPasswordView, SocialLoginView, ChangePasswordView,LogoutAPIView

urlpatterns = [
    path('signup/',SignupView.as_view()),
    path('signin/',SigninView.as_view()),
    path('signout/',LogoutAPIView.as_view()), 

    path('request-forget-password/', ForgetPasswordView.as_view(), name='request-forget-password'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('forget-password/', ForgetPasswordView.as_view(), name='forget-password'),
    path('set-new-password/', SetNewPasswordView.as_view(), name='set-new-password'),
    path('social-login/', SocialLoginView.as_view(), name='social-login'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),

]