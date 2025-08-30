from django.urls import path
from .views import SignupView,SigninView,RequestForgetPasswordView,VerifyOTPView,ForgetPasswordView, SocialLoginView

urlpatterns = [
    path('signup/',SignupView.as_view()),
    path('signin/',SigninView.as_view()),

    # forget password 
    path('request-forget-password/', RequestForgetPasswordView.as_view(), name='request-forget-password'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('forget-password/', ForgetPasswordView.as_view(), name='forget-password'),
    path('social-login/', SocialLoginView.as_view(), name='social-login'),
]