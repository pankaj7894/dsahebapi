
from ninja import Router
from typing import Dict
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from .models import Listing, Education, Training, RegistrationList, Experience
from .serializers import ListingSerializer, ListingCreateSerializer, EducationSchema, TrainingSchema, RegistrationListSchema, ExperienceSchema,EducationSchema,TrainingSchema, RegistrationListSchema,ExperienceSchema
from django.utils import timezone
from ninja.security import HttpBearer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from config.utils.api_helpers import success_response, error_response, failure_response  # Assuming these are defined in utils.py
from django.http import JsonResponse
from typing import List


# # JWT authentication for endpoints
class JWTAuth(HttpBearer):
    def authenticate(self, request, token):
        from rest_framework_simplejwt.authentication import JWTAuthentication
        try:
            validated_token = JWTAuthentication().get_validated_token(token)
            user = JWTAuthentication().get_user(validated_token)
            return user
        except Exception:
            return None
    
    class Config:
        arbitrary_types_allowed = True

# Common headers for responses
COMMON_HEADERS = {
    "Content-Type": "application/json",
}

# Creating an instance of the JWTAuth class
auth = JWTAuth()
router = Router(auth=JWTAuth)



@router.post("/listings", response={200: ListingSerializer, 400: Dict})
def create_listing(request, data: ListingCreateSerializer):
    """
    Create a new listing for the authenticated doctor or hospital.
    """
    try:
        # Access the authenticated user
        user = request.auth  # This is automatically set by JWTAuth

        if not user:
            response = failure_response(message="Authentication failed")
            return JsonResponse(response, status=401, headers=COMMON_HEADERS)

        search_tags = ' '.join([data.title, data.services, data.specializations])

        listing = Listing.objects.create(
            title=data.title,
            description=data.description,
            services=data.services,
            specializations=data.specializations,
            search_tags=search_tags,
            state_id=data.state,
            city_id=data.city,
            location_id=data.location,
            is_active=True,
            created_at=timezone.now(),
            updated_at=timezone.now(),
            created_by=user.id  # Use the authenticated user's ID
        )

        response = success_response(
            message="Listing created successfully",
            data=ListingSerializer.from_attributes(listing).dict()
        )
        return JsonResponse(response, status=200, headers=COMMON_HEADERS)

    except Exception as e:
        response = error_response(message=f"An error occurred: {str(e)}")
        return JsonResponse(response, status=500, headers=COMMON_HEADERS)


@router.put("/listings/{listing_id}", response=ListingSerializer)
def update_listing(request, listing_id: int, data: ListingCreateSerializer):
    """
    Update an existing listing for the authenticated doctor or hospital.
    """
    user = request.auth  # This is automatically set by JWTAuth
    try:
        # Fetch the listing created by the authenticated user
        listing = get_object_or_404(Listing, pk=listing_id, created_by=user.id)
        
        # Update listing fields
        listing.title = data.title
        listing.description = data.description
        listing.services = data.services
        listing.specializations = data.specializations
        listing.search_tags = ' '.join([data.title, data.services, data.specializations])
        listing.state_id = data.state
        listing.city_id = data.city
        listing.location_id = data.location
        listing.updated_at = timezone.now()
        
        listing.save()

        return success_response(message="Listing updated successfully", data=listing)
    except Exception as e:
        return error_response(message=f"Error updating listing: {str(e)}")


@router.delete("/listings/{listing_id}")
def delete_listing(request, listing_id: int):
    """
    Soft delete a listing for the authenticated doctor or hospital (set is_active=False).
    """
    user = request.auth  # This is automatically set by JWTAuth
    try:
        # Fetch the listing created by the authenticated user
        listing = get_object_or_404(Listing, pk=listing_id, created_by=user.id)
        listing.status = False
        listing.save()

        return success_response(message="Listing marked as deleted.")
    except Exception as e:
        return error_response(message=f"Error deleting listing: {str(e)}")


@router.get("/listings/my-listings", response=ListingSerializer)
def list_my_listings(request):
    """
    List all active listings created by the authenticated doctor or hospital.
    """
    user = request.auth  # This is automatically set by JWTAuth
    try:
        listings = Listing.objects.filter(created_by=user.id, is_active=True)
        return success_response(message="Listings fetched successfully", data=listings)
    except Exception as e:
        return error_response(message=f"Error fetching listings: {str(e)}")


@router.get("/listings/search", response=ListingSerializer)
def search_my_listings(request, query: str):
    """
    Search active listings created by the authenticated doctor or hospital.
    """
    user = request.auth  # This is automatically set by JWTAuth
    try:
        listings = Listing.objects.filter(
            created_by=user.id,
            search_tags__icontains=query,
            is_active=True
        )
        return success_response(message="Listings fetched successfully", data=listings)
    except Exception as e:
        return error_response(message=f"Error searching listings: {str(e)}")
    


@router.post("/educations", response=EducationSchema)
def create_education(request, payload: EducationSchema):
    """
    Create a new education record for the authenticated user.
    """
    user = request.auth
    education = Education.objects.create(user=user, **payload.dict())
    return success_response(message="Education record created successfully", data=education)


@router.get("/educations", response=EducationSchema)
def list_educations(request):
    """
    Fetch all education records for the authenticated user.
    """
    user = request.auth
    educations = Education.objects.filter(user=user)
    return success_response(message="Education records fetched successfully", data=educations)


@router.get("/educations/{id}", response=EducationSchema)
def retrieve_education(request, id: int):
    """
    Fetch a specific education record for the authenticated user.
    """
    user = request.auth
    education = get_object_or_404(Education, pk=id, user=user)
    return success_response(message="Education record retrieved successfully", data=education)


@router.patch("/educations/{id}", response=EducationSchema)
def update_education(request, id: int, payload: EducationSchema):
    """
    Update an existing education record for the authenticated user.
    """
    user = request.auth
    education = get_object_or_404(Education, pk=id, user=user)
    for attr, value in payload.dict().items():
        setattr(education, attr, value)
    education.save()
    return success_response(message="Education record updated successfully", data=education)


@router.delete("/educations/{id}", response=dict)
def delete_education(request, id: int):
    """
    Delete an education record for the authenticated user.
    """
    user = request.auth
    education = get_object_or_404(Education, pk=id, user=user)
    education.delete()
    return success_response(message="Education record deleted successfully", data=None)


# Training Endpoints
@router.post("/trainings", response=TrainingSchema)
def create_training(request, payload: TrainingSchema):
    """
    Create a new training record for the authenticated user.
    """
    user = request.auth
    training = Training.objects.create(user=user, **payload.dict())
    return success_response(message="Training record created successfully", data=training)


@router.get("/trainings", response=TrainingSchema)
def list_trainings(request):
    """
    Fetch all training records for the authenticated user.
    """
    user = request.auth
    trainings = Training.objects.filter(user=user)
    return success_response(message="Training records fetched successfully", data=trainings)


@router.get("/trainings/{id}", response=TrainingSchema)
def retrieve_training(request, id: int):
    """
    Fetch a specific training record for the authenticated user.
    """
    user = request.auth
    training = get_object_or_404(Training, pk=id, user=user)
    return success_response(message="Training record retrieved successfully", data=training)


@router.patch("/trainings/{id}", response=TrainingSchema)
def update_training(request, id: int, payload: TrainingSchema):
    """
    Update an existing training record for the authenticated user.
    """
    user = request.auth
    training = get_object_or_404(Training, pk=id, user=user)
    for attr, value in payload.dict().items():
        setattr(training, attr, value)
    training.save()
    return success_response(message="Training record updated successfully", data=training)


@router.delete("/trainings/{id}", response=dict)
def delete_training(request, id: int):
    """
    Delete a training record for the authenticated user.
    """
    user = request.auth
    training = get_object_or_404(Training, pk=id, user=user)
    training.delete()
    return success_response(message="Training record deleted successfully", data=None)


# RegistrationList Endpoints
@router.post("/registrations", response=RegistrationListSchema)
def create_registration(request, payload: RegistrationListSchema):
    """
    Create a new registration record for the authenticated user.
    """
    user = request.auth
    registration = RegistrationList.objects.create(user=user, **payload.dict())
    return success_response(message="Registration record created successfully", data=registration)


@router.get("/registrations", response=RegistrationListSchema)
def list_registrations(request):
    """
    Fetch all registration records for the authenticated user.
    """
    user = request.auth
    registrations = RegistrationList.objects.filter(user=user)
    return success_response(message="Registration records fetched successfully", data=registrations)


@router.get("/registrations/{id}", response=RegistrationListSchema)
def retrieve_registration(request, id: int):
    """
    Fetch a specific registration record for the authenticated user.
    """
    user = request.auth
    registration = get_object_or_404(RegistrationList, pk=id, user=user)
    return success_response(message="Registration record retrieved successfully", data=registration)


@router.patch("/registrations/{id}", response=RegistrationListSchema)
def update_registration(request, id: int, payload: RegistrationListSchema):
    """
    Update an existing registration record for the authenticated user.
    """
    user = request.auth
    registration = get_object_or_404(RegistrationList, pk=id, user=user)
    for attr, value in payload.dict().items():
        setattr(registration, attr, value)
    registration.save()
    return success_response(message="Registration record updated successfully", data=registration)


@router.delete("/registrations/{id}", response=dict)
def delete_registration(request, id: int):
    """
    Delete a registration record for the authenticated user.
    """
    user = request.auth
    registration = get_object_or_404(RegistrationList, pk=id, user=user)
    registration.delete()
    return success_response(message="Registration record deleted successfully", data=None)


# Experience Endpoints
@router.post("/experiences", response=ExperienceSchema)
def create_experience(request, payload: ExperienceSchema):
    """
    Create a new experience record for the authenticated user.
    """
    user = request.auth
    experience = Experience.objects.create(user=user, **payload.dict())
    return success_response(message="Experience record created successfully", data=experience)


@router.get("/experiences", response=ExperienceSchema)
def list_experiences(request):
    """
    Fetch all experience records for the authenticated user.
    """
    user = request.auth
    experiences = Experience.objects.filter(user=user)
    return success_response(message="Experience records fetched successfully", data=experiences)


@router.get("/experiences/{id}", response=ExperienceSchema)
def retrieve_experience(request, id: int):
    """
    Fetch a specific experience record for the authenticated user.
    """
    user = request.auth
    experience = get_object_or_404(Experience, pk=id, user=user)
    return success_response(message="Experience record retrieved successfully", data=experience)


@router.patch("/experiences/{id}", response=ExperienceSchema)
def update_experience(request, id: int, payload: ExperienceSchema):
    """
    Update an existing experience record for the authenticated user.
    """
    user = request.auth
    experience = get_object_or_404(Experience, pk=id, user=user)
    for attr, value in payload.dict().items():
        setattr(experience, attr, value)
    experience.save()
    return success_response(message="Experience record updated successfully", data=experience)


@router.delete("/experiences/{id}", response=dict)
def delete_experience(request, id: int):
    """
    Delete an experience record for the authenticated user.
    """
    user = request.auth
    experience = get_object_or_404(Experience, pk=id, user=user)
    experience.delete()
    return success_response(message="Experience record deleted successfully", data=None)
