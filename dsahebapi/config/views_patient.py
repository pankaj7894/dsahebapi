from django.contrib.auth import get_user_model
from config.models import PatientProfile
from config.schemas import PatientProfileSchema, PatientProfileResponseSchema
from config.utils.api_helpers import success_response, failure_response
from ninja import Router
from typing import List, Optional
from ninja.errors import HttpError
from config.utils.jwt_auth import JWTAuth

router = Router(auth=JWTAuth())

@router.get("/patient-profile", response=List[PatientProfileResponseSchema])
def list_patient_profiles(request):
    """
    Get all patient profiles for the logged-in user.
    """
    user = request.auth  # Authenticated user
    profiles = PatientProfile.objects.filter(user=user)
    return success_response(message="Profiles retrieved successfully", data=profiles)

@router.get("/patient-profile/{id}", response=PatientProfileResponseSchema)
def get_patient_profile(request, id: str):  # Accept UUID as string
    """
    Get a specific patient profile by ID.
    """
    user = request.auth
    try:
        profile = PatientProfile.objects.get(id=id, user=user)
    except PatientProfile.DoesNotExist:
        raise HttpError(404, "Profile not found")
    return success_response(message="Profile retrieved successfully", data=profile)

@router.post("/patient-profile", response=PatientProfileResponseSchema)
def create_patient_profile(request, payload: PatientProfileSchema):
    """
    Create a new patient profile.
    """
    user = request.auth
    profile = PatientProfile.objects.create(user=user, **payload.dict())
    return success_response(message="Profile created successfully", data=profile)

@router.patch("/patient-profile/{id}", response=PatientProfileResponseSchema)
def update_patient_profile(request, id: str, payload: PatientProfileSchema):
    """
    Update an existing patient profile.
    """
    user = request.auth
    try:
        profile = PatientProfile.objects.get(id=id, user=user)
    except PatientProfile.DoesNotExist:
        raise HttpError(404, "Profile not found")
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(profile, attr, value)
    profile.save()
    return success_response(message="Profile updated successfully", data=profile)
