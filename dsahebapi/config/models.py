from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
import uuid
from datetime import timedelta
from django.utils.timezone import now
from django.conf import settings

class CustomUserManager(BaseUserManager):
    def create_user(self, mobile, name, usertype, password=None, **extra_fields):
        """
        Create and return a user with an email and password.
        """
        if not mobile:
            raise ValueError('The mobile field must be set')
        user = self.model(mobile=mobile, name=name, usertype=usertype, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, mobile, name, usertype, password=None, **extra_fields):
        """
        Create and return a superuser with an email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        return self.create_user(mobile, name, usertype, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    USER_TYPE_CHOICES = [
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
        ('hospital', 'Hospital'),
        ('clinic', 'Clinic'),
        ('front_desk', 'Front Desk'),
        ('back_desk', 'Back Desk'),
        ('admin', 'Admin'),
        ('superadmin', 'Super Admin'),
    ]

    name = models.CharField(max_length=255)
    mobile = models.CharField(max_length=15, unique=True)
    usertype = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    slug = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)  # UUID slug field
    is_verified = models.BooleanField(default=False)  # Verification status
    objects = CustomUserManager()

    USERNAME_FIELD = 'mobile'
    REQUIRED_FIELDS = ['name', 'usertype']

    def __str__(self):
        return self.name




class OTP(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="otps", null=True, blank=True) 
    phone_number = models.CharField(max_length=15)  # Phone number for OTP
    otp = models.CharField(max_length=6)  # The OTP code
    created_at = models.DateTimeField(auto_now_add=True)  # When the OTP was created
    expires_at = models.DateTimeField()  # When the OTP will expire
    is_sent = models.BooleanField(default=False)  # OTP
    is_verified = models.BooleanField(default=False)  # OTP verification status
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)  # Unique identifier for tracking OTPs

    def save(self, *args, **kwargs):
        # Set expiration to 5 minutes from creation if not explicitly set
        if not self.expires_at:
            self.expires_at = now() + timedelta(minutes=5)
        super().save(*args, **kwargs)

    def is_expired(self):
        """Check if the OTP is expired."""
        return now() > self.expires_at

    def __str__(self):
        return f"OTP for {self.phone_number} (Verified: {self.is_verified})"


class LoginAttempt(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    attempted_at = models.DateTimeField(default=now)
    successful = models.BooleanField(default=False)

# Max attempts allowed before lockout
MAX_ATTEMPTS = 5
LOCKOUT_TIME = timedelta(minutes=30)


class PatientProfile(models.Model):
    SEX_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # UUID as primary key
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="patient_profiles"
    )
    mobile = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    sex = models.CharField(max_length=10, choices=SEX_CHOICES, blank=True, null=True)
    address_line1 = models.TextField(blank=True, null=True)
    landmark = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    pin = models.CharField(max_length=10, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile of {self.user.name} ({self.mobile})"

class State(models.Model):
    name = models.CharField(max_length=255,db_index=True,unique=True)
    status = models.CharField(max_length=5)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']  # Order by the 'name' field or any other relevant field
    

class City(models.Model):
    name = models.CharField(max_length=255,db_index=True)
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='cities')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']  # Order by the 'name' field or any other relevant field
    

class Location(models.Model):
    name = models.CharField(max_length=255)
    cities = models.ForeignKey(City, related_name='locations', on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']  # Order by the 'name' field or any other relevant field
    

class Services(models.Model):
    name = models.CharField(max_length=255,db_index=True,unique=True)
    description = models.TextField(blank=True, null=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    class Meta:
        ordering = ['name']  # Order by the 'name' field or any other relevant field
    
class Specialization(models.Model):
    name = models.CharField(max_length=255,db_index=True,unique=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    class Meta:
        ordering = ['name']  # Order by the 'name' field or any other relevant field
    
class University(models.Model):
    name = models.CharField(max_length=255,db_index=True)
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='universities')
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='universities')
    pincode = models.CharField(max_length=6)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']  # Order by the 'name' field or any other relevant field

class College(models.Model):
    name = models.CharField(max_length=255,db_index=True)
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='colleges')
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='colleges')
    pincode = models.CharField(max_length=6)
    affiliation_type = models.CharField(max_length=255, choices=[('govt', 'Government'), ('private', 'Private'),('deemed', 'Deemed')])
    affliated_to = models.ForeignKey(University, on_delete=models.CASCADE, related_name='colleges')
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']  # Order by the 'name' field or any other relevant field

class Degree(models.Model):
    name = models.CharField(max_length=255,db_index=True,unique=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']  # Order by the 'name' field or any other relevant field

class Memberships(models.Model):
    name = models.CharField(max_length=255,db_index=True,unique=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']  # Order by the 'name' field or any other relevant field

class Registration(models.Model):
    name = models.CharField(max_length=255,db_index=True,unique=True)
    status = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']  # Order by the 'name' field or any other relevant field