from ninja import Router
from config.utils.api_helpers import success_response, failure_response
from config.serializers import OTP_Request, OTP_Verify
from config.utils.otp_utils import send_otp, verify_otp, send_sms, generate_otp
from django.contrib.auth import get_user_model
import random
from django.contrib.auth.hashers import make_password
from config.serializers import User_Create, User_Profile, User_Profile
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from django.contrib.auth import authenticate
from ninja.errors import HttpError
from ninja.security import HttpBearer
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from django_ratelimit.decorators import ratelimit
from datetime import timedelta
from django.utils import timezone
from config.models import LoginAttempt

User = get_user_model()
router = Router()

@router.post("/request-otp")
@ratelimit(key='ip', rate='3/m', method='ALL', block=True) 
def request_otp(request, data: OTP_Request):
    if getattr(request, 'limited', False):  # Check if the rate limit is exceeded
        return failure_response(message="Too many requests. Please try again later.", status_code=429)

    success, message = send_otp(data.phone_number)
    response_data = None
    if success:
        response_data = success_response(message=message)
    else:
        response_data = failure_response(message=message)

    return response_data

@router.post("/verify-otp")
def verify_otp_view(request, data: OTP_Verify):

    """
    Endpoint to verify OTP for the given phone number.
    """
    # Use the utility function to verify OTP
    success, message = verify_otp(data.phone_number, data.otp)
    
    if success:
        # Optionally, update the user's `is_verified` field to True
        user = User.objects.filter(mobile=data.phone_number).first()  # Get user by phone number
        if user:
            user.is_verified = True
            user.save()
        response_data = success_response(message=message)
    else:
        response_data = failure_response(message=message)
    
    return response_data




# Generate a random 6-digit password
def generate_random_password():
    return str(random.randint(100000, 999999))

# User Registration API (with auto-generated password)
@router.post("/create-user")
def create_user(request, data: User_Create):
    try:
        # Generate a random 6-digit password
        generated_password = generate_random_password()

        # Hash the generated password
        hashed_password = make_password(generated_password)

        # Create the user
        user = get_user_model().objects.create(
            mobile=data.mobile,
            usertype=data.usertype,
            password=hashed_password,
            is_verified=False,  # The user is not verified initially
        )

        # Send the generated password to the user via SMS
        send_sms(data.mobile, f"Your password is {generated_password}. Please use it to log in.")

        # Optionally, generate JWT token for immediate use
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        # Return success response with JWT and info
        return success_response(message="User created successfully", data={
            "access_token": access_token,
            "refresh_token": str(refresh),
        })

    except Exception as e:
        return failure_response(message=str(e))
    
MAX_ATTEMPTS = 5
LOCKOUT_TIME = timedelta(minutes=30)
@router.post("/login-with-otp")
def login_with_otp(request, data: OTP_Verify):
    # Verify OTP for the provided mobile number
    is_verified, message = verify_otp(data.phone_number, data.otp)
    if is_verified:
        user = User.objects.filter(mobile=data.phone_number).first()
        if user:
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            return success_response(message="Login successful", data={
                "access_token": access_token,
                "refresh_token": str(refresh),
            })
    return failure_response(message=message)

@router.post("/login")
def login(request, mobile: str, password: str):
    if not mobile or not password:
        raise failure_response(message="Please enter your mobile and passoword.", status_code=401)
    
    user = get_user_model().objects.filter(mobile=mobile).first()
    if not user:
        return failure_response(message="User not found", status_code=404)
    
    # Track failed login attempts
    if LoginAttempt.objects.filter(user=user, successful=False, attempted_at__gt=timezone.now() - LOCKOUT_TIME).count() >= MAX_ATTEMPTS:
        return failure_response(message="Account locked due to too many failed login attempts. Please try again later.", status_code=403)
    
    user_authenticated = authenticate(request, mobile=mobile, password=password)
    if not user_authenticated:
        # Log failed login attempt
        LoginAttempt.objects.create(user=user, successful=False)
        return failure_response(message="Invalid credentials", status_code=401)
    
    # Reset failed login attempts on successful login
    LoginAttempt.objects.filter(user=user).update(successful=True)
    
    # Generate JWT tokens
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    
    return success_response(message="Login successful", data={
        "access_token": access_token,
        "refresh_token": str(refresh),
        "user_type": user.usertype,
    })

class JWTAuth(HttpBearer):
    def authenticate(self, request, token):
        from rest_framework_simplejwt.authentication import JWTAuthentication
        try:
            validated_token = JWTAuthentication().get_validated_token(token)
            user = JWTAuthentication().get_user(validated_token)
            return user
        except Exception:
            return None

auth = JWTAuth()

@router.get("/profile", auth=auth)
def get_profile(request):
    """
    Fetch details of the logged-in user.
    """
    user = request.auth
    user_data = {
        "id": user.id,
        "name": user.name,
        "mobile": user.mobile,
        "usertype": user.usertype,
        "is_verified": user.is_verified,
    }
    return success_response(message="Profile fetched successfully", data=user_data)

@router.put("/update-profile", auth=auth)
def update_profile(request, name: str = None, email: str = None):
    """
    Update profile information for logged-in user.
    """
    user = request.auth
    if name:
        user.name = name
    if email:
        user.email = email
    user.save()

    return success_response(message="Profile updated successfully")

@router.post("/logout", auth=auth)
def logout(request):
    """
    Logout user by blacklisting tokens.
    """
    user = request.auth
    
    # Blacklist all outstanding tokens for the user
    tokens = OutstandingToken.objects.filter(user=user)
    for token in tokens:
        BlacklistedToken.objects.get_or_create(token=token)
    
    return success_response(message="Logout successful")

@router.post("/request-password-reset")
def request_password_reset(request, mobile: str):
    """
    Request OTP for password reset.
    """
    user = get_user_model().objects.filter(mobile=mobile).first()
    if not user:
        return failure_response(message="User not found", status_code=404)
    
    # Generate and send OTP
    otp = generate_otp(mobile)
    send_sms(mobile, f"our login OTP for Trainmenu is : {otp} is valid for 30 minutes. Team Trainmenu")
    
    return success_response(message="OTP sent successfully")

@router.post("/reset-password")
def reset_password(request, mobile: str, otp: str, new_password: str):
    """
    Reset password after OTP verification.
    """
    is_verified, message = verify_otp(mobile, otp)
    if not is_verified:
        return failure_response(message=message, status_code=404)
    
    user = get_user_model().objects.filter(mobile=mobile).first()
    if not user:
        return failure_response(message="User not found", status_code=404)
    
    # Update the user's password
    user.set_password(new_password)
    user.save()
    
    return success_response(message="Password reset successfully")

