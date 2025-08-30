from rest_framework.views import exception_handler
from rest_framework import status
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.core.exceptions import PermissionDenied

def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    # Handle specific exceptions
    if isinstance(exc, (InvalidToken, TokenError)):
        custom_response = {
            "status": "error",
            "status_code": status.HTTP_401_UNAUTHORIZED,
            "message": "Authentication failed",
            "data": None,
            "errors": {
                "token": "Invalid or expired token"
            }
        }
        response.data = custom_response
        response.status_code = status.HTTP_401_UNAUTHORIZED
    
    elif isinstance(exc, PermissionDenied):
        custom_response = {
            "status": "error",
            "status_code": status.HTTP_403_FORBIDDEN,
            "message": "Permission denied",
            "data": None,
            "errors": {
                "permission": str(exc)
            }
        }
        response.data = custom_response
        response.status_code = status.HTTP_403_FORBIDDEN
    
    # Add more custom exception handlers as needed
    
    return response