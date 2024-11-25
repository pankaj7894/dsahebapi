import random
from django.utils.timezone import now
from ..models import OTP
from datetime import timedelta
from django.conf import settings
import requests


def generate_otp(length=6):
    """
    Generate a random numeric OTP of the given length.
    Default is 6 digits.
    """
    return ''.join(random.choices('0123456789', k=length))

def create_otp(phone_number, user=None, expiry_minutes=5):
    """
    Create an OTP for the given phone number and user (if provided).
    """
    otp_code = generate_otp()
    expires_at = now() + timedelta(minutes=expiry_minutes)

    otp = OTP.objects.create(
        phone_number=phone_number,
        otp=otp_code,
        user=user,
        expires_at=expires_at,
    )
    return otp

def verify_otp(phone_number, otp_code):
    """
    Verify the OTP for a given phone number.
    """
    try:
        otp = OTP.objects.filter(phone_number=phone_number, is_verified=False).latest('created_at')
        if otp.is_expired():
            return False, "OTP expired"
        if otp.otp != otp_code:
            return False, "Invalid OTP"
        
        otp.is_verified = True
        otp.save()
        return True, "OTP verified"
    except OTP.DoesNotExist:
        return False, "No OTP found for this phone number"

def send_otp(phone_number, message_template="Your login OTP for Trainmenu is : {otp} is valid for 30 minutes. Team Trainmenu"):
    otp = create_otp(phone_number)
    message = message_template.format(otp=otp.otp)
    success = send_sms(phone_number, message)  # Replace with your SMS provider's function
    
    if success:
        otp.is_sent = True
        otp.save()
        return True, f"OTP sent to {phone_number}"
    return False, "Failed to send OTP"

def send_otp_for_signal(instance, message_template="Your login OTP for Trainmenu is : {otp} is valid for 30 minutes. Team Trainmenu"):
    otp = instance.otp
    phone_number = instance.phone_number
    message = message_template.format(otp=otp)
    success = send_sms(phone_number, message) 
    if success:
        otp.is_sent = True
        otp.save()
        return True, f"OTP sent to {phone_number}"
    return False, "Failed to send OTP"

def send_sms(phone_number, message):
    """
    Sends an SMS to the specified phone number using the custom SMS provider.
    """
    API_KEY = settings.SMS_API_KEY
    sms_format = '''http://sms.azmobia.com/http-tokenkeyapi.php?authentic-key={}&senderid=TRAINM&route=1&number={}&message={}&templateid=1207168149392467501
    '''.format(API_KEY, phone_number, message)

    # Send the request to the SMS provider's API
    try:
        response = requests.get(sms_format)
        if response.status_code == 200:
            return True  # SMS sent successfully
        else:
            print(f"Failed to send SMS: {response.status_code}, {response.text}")
            return False  # SMS sending failed
    except requests.exceptions.RequestException as e:
        print(f"Error sending SMS: {e}")
        return False  # Error during the request