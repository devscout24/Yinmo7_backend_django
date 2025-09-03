from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import SignupSerializer
from django.contrib.auth import get_user_model
User = get_user_model()
from django.conf import settings
from django.core.mail import send_mail
import random
from uuid import uuid4
from apps.user.models import UserOtp
from .serializers import SigninSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from datetime import timedelta
import threading
import jwt
import requests
import json
from jwt.algorithms import RSAAlgorithm
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import update_session_auth_hash

from .firebase_config import initialize_firebase




def send_reset_otp_email(email, otp):
    def send():
        send_mail(
            subject="Your Password Reset OTP",
            message=f"Your OTP is {otp}. Use this to reset your password.",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
        )
    threading.Thread(target=send).start()


# Create your views here.
class SignupView(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            refresh = RefreshToken.for_user(serializer.instance)
            response = {
                "status": "success",
                "status_code": status.HTTP_201_CREATED,
                "message": "User created successfully",
                "data": serializer.data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
            return Response(response, status=status.HTTP_201_CREATED)
        error_response = {
            "status": "error",
            "status_code": status.HTTP_400_BAD_REQUEST,
            "message": "Invalid credentials",
            "errors": serializer.errors
        }
        return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
    
class SigninView(APIView):
    def post(self, request):
        serializer = SigninSerializer(data=request.data)
        if not serializer.is_valid():
            response = {
                "status": "error",
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "Invalid credentials",
                "errors": serializer.errors
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        response = {
            "status": "success",
            "status_code": status.HTTP_200_OK,
            "message": "User logged in successfully",
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "data":{
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "type": user.type
            }
        }
        return Response(response, status=status.HTTP_200_OK)

class RequestForgetPasswordView(APIView):
    def post(self, request):
        email = request.data.get("email")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            error_response = {
                "status": "error",
                "status_code": status.HTTP_404_NOT_FOUND,
                "message": "Email not found."
            }
            return Response(error_response, status=status.HTTP_404_NOT_FOUND)
        
        user_otp, created = UserOtp.objects.get_or_create(user=user)
        
        user_otp.otp = random.randint(10000, 99999)
        user_otp.token = uuid4()
        user_otp.save()


        # Send OTP email
        send_reset_otp_email(user.email, user_otp.otp)
        
        response = {
            "status": "success",
            "status_code": status.HTTP_200_OK,
            "message": "OTP sent to your email.",
            "token": str(user_otp.token)
        }
        return Response(response, status=status.HTTP_200_OK)

    
class VerifyOTPView(APIView):
    def post(self, request):
        otp = request.data.get("otp")
        token = request.data.get("token")
        if not all([otp, token]):
            errpr_response = {
                "status": "error",
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "OTP and token are required."
            }
            return Response(errpr_response, status=status.HTTP_400_BAD_REQUEST)

        match = get_object_or_404(UserOtp, token=token, otp=otp)
        if match:
            expiry_time = match.updated_at + timedelta(minutes=2)
            if timezone.now() > expiry_time:
                errpr_response = {
                    "status": "error",
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "OTP has expired."
                }
                return Response(errpr_response, status=status.HTTP_400_BAD_REQUEST)
            respomse = {
                "status": "success",
                "status_code": status.HTTP_200_OK,
                "message": "OTP verified successfully.",
                "token": match.token
            }
            
            return Response(respomse, status=status.HTTP_200_OK)
        else:
            errpr_response = {
                "status": "error",
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "Invalid OTP."
            }

            return Response(errpr_response, status=status.HTTP_400_BAD_REQUEST)

class ForgetPasswordView(APIView):
    def post(self, request):
        password = request.data.get("password")
        token = request.data.get("token")

        try:
            obj = UserOtp.objects.get(token=token)
        except UserOtp.DoesNotExist:
            errpr_response = {
                "status": "error",
                "status_code": status.HTTP_404_NOT_FOUND,
                "message": "Invalid or not given token."
            }
            return Response(errpr_response, status=status.HTTP_404_NOT_FOUND)
        if not password:
            
            return Response({"error": "Password is required."}, status=400)
        obj.user.set_password(password)
        obj.user.save()
        obj.delete()
        response = {
            "status": "success",
            "status_code": status.HTTP_200_OK,
            "message": "Password reset successfully."
        }
        return Response(response, status=status.HTTP_200_OK)




class AppleLoginView(APIView):
    def post(self, request):
        # Step 1: Get id_token from Flutter request body
        id_token = request.data.get('id_token')
        if not id_token:
            error_response = {
                "status": "error",
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "ID token is required."
            }
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Step 2: Verify the id_token with Apple's servers
            decoded = self.verify_apple_token(id_token)
            
            # Step 3: Get or create user in your database
            user, created = self.get_or_create_user(decoded)
            refresh = RefreshToken.for_user(user)
            # Step 4: Return your authentication response
            return Response({
                'status': 'success',
                "status_code": status.HTTP_200_OK,
                "message": "User logged in successfully",
                'is_new_user': created,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                
            })
            
        except jwt.ExpiredSignatureError:
            error_response = {
                "status": "error",
                "status_code": status.HTTP_401_UNAUTHORIZED,
                "message": "Apple token has expired."
            }
            return Response(error_response, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            error_response = {
                "status": "error",
                "status_code": status.HTTP_401_UNAUTHORIZED,
                "message": "Invalid Apple token."
            }
            return Response(error_response, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            error_response = {
                "status": "error",
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Authentication failed.",
                'detail': str(e)
            }
            return Response(error_response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def verify_apple_token(self, id_token):
        # Step 1: Get Apple's public keys
        header = jwt.get_unverified_header(id_token)
        apple_public_keys = requests.get('https://appleid.apple.com/auth/keys').json()
        
        # Step 2: Find the matching key
        public_key = None
        for key in apple_public_keys['keys']:
            if key['kid'] == header['kid']:
                public_key = RSAAlgorithm.from_jwk(json.dumps(key))
                break
        
        if not public_key:
            raise ValueError('Apple public key not found')
        
        # Step 3: Verify the token
        decoded = jwt.decode(
            id_token,
            public_key,
            audience=settings.APPLE_CLIENT_ID,
            algorithms=['RS256'],
            options={'verify_exp': True}
        )
        
        return decoded
    
    def get_or_create_user(self, decoded_data):
        apple_id = decoded_data['sub']
        email = decoded_data.get('email')
        
        
        # Try to find existing user
        user = User.objects.filter(apple_id=apple_id).first()
        if user:
            return user, False
        
        # Create new user if not exists
        pass

        user = User.objects.create_user(
            email=email,
            apple_id=apple_id,
            is_active=True
        )
        full_name= decoded_data.get('name') if decoded_data.get('name') else decoded_data.get('full_name')
        if full_name:
            user.full_name = full_name
            user.save()
        
        return user, True
    



class GoogleLoginView(APIView):
    def post(self, request):
        # Initialize Firebase
        initialize_firebase()
        
        # Get the access token from frontend
        access_token = request.data.get('id_token')
        if not access_token:
            error_response = {
                "status": "error",
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "Access token is required."
            }
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Verify the token with Google's API
            user_info = self.verify_google_token(access_token)
            
            # Get or create user
            user, created = self.get_or_create_user(user_info)
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'status': 'success',
                "status_code": status.HTTP_200_OK,
                "message": "User logged in successfully",
                'is_new_user': created,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            })
            
        except Exception as e:
            error_response = {
                "status": "error",
                "status_code": status.HTTP_401_UNAUTHORIZED,
                "message": "Authentication failed."
            }
            return Response(error_response, status=status.HTTP_401_UNAUTHORIZED)
    
    def verify_google_token(self, access_token):
        # Verify token using Google's API
        response = requests.get(
            'https://www.googleapis.com/oauth2/v3/userinfo',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        if response.status_code != 200:
            raise ValueError('Invalid access token')
        
        return response.json()
    
    def get_or_create_user(self, user_info):
        google_id = user_info['sub']
        email = user_info['email']
        name = user_info.get('name', '')
        
        # Try to find existing user
        user = User.objects.filter(google_id=google_id).first()
        if user:
            return user, False
        
        # Create new user
        
        user = User.objects.create_user(

            email=email,
            google_id=google_id,
            full_name=name,
            is_active=True
        )
        return user, True
    

class SocialLoginView(APIView):
    def post(self, request):
        provider = request.data.get('provider')
        id_token = request.data.get('id_token')
        
        if not provider:
            error_response = {
                "status": "error",
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "Provider is required."
            }
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
            
        if not id_token:
            error_response = {
                "status": "error",
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "ID token is required."
            }
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        

        if provider.lower() == 'apple':
            apple_view = AppleLoginView()
            return apple_view.post(request)
        elif provider.lower() == 'google':
            google_view = GoogleLoginView()
            return google_view.post(request)
        else:
            error_response = {
                "status": "error",
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "Invalid provider. Supported providers are 'apple' and 'google'."
            }
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)




class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            if not refresh_token:
                error_response = {
                    "status": "error",
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Refresh token is required."
                }
                return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
            token = RefreshToken(refresh_token)
            token.blacklist()
            response = {
                "status": "success",
                "status_code": status.HTTP_205_RESET_CONTENT,
                "message": "Token blacklisted successfully."
            }
            return Response(response, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            error_response = {
                "status": "error",
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "Invalid refresh token."
            }
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        
        if not old_password or not new_password:
            error_response = {
                "status": "error",
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "Both old_password and new_password are required."
            }
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        
        if not user.check_password(old_password):
            error_response = {
                "status": "error",
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "Invalid old password."
            }
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(new_password)
        user.save()
        
        update_session_auth_hash(request, user)
        
        response = {
            "status": "success",
            "status_code": status.HTTP_200_OK,
            "message": "Password changed successfully."
        }
        return Response(response, status=status.HTTP_200_OK)