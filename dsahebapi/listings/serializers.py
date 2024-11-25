# serializers.py
from ninja import Schema
from pydantic import Field
from typing import Optional
from datetime import date

class ListingSerializer(Schema):
    id: int
    title: str
    description: str
    services: str
    specializations: str
    search_tags: str
    state: int  
    city: int   
    location: int
    is_active: bool
    created_at: str
    updated_at: str
    created_by: int

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True

class ListingCreateSerializer(Schema):
    title: str
    description: str
    services: str
    specializations: str
    state: int  
    city: int   
    location: int

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class EducationSchema(Schema):
    id: int
    user_id: int
    degree_id: Optional[int]
    college_id: Optional[int]
    year: int
    status: bool
    created_at: date
    updated_at: date


# Training Schema
class TrainingSchema(Schema):
    id: int
    user_id: int
    degree_id: Optional[int]
    college_id: Optional[int]
    year: int
    status: bool
    created_at: date
    updated_at: date


# Registration List Schema
class RegistrationListSchema(Schema):
    id: int
    user_id: int
    name_id: int
    year: int
    status: bool


# Experience Schema
class ExperienceSchema(Schema):
    id: int
    user_id: int
    title: str
    description: Optional[str]
    start_date: Optional[date]
    end_date: Optional[date]
    ongoing: bool
    status: bool
    created_at: date
    updated_at: date


# Review Schema
class ReviewSchema(Schema):
    id: int
    user_id: int
    listing_id: int
    rating: int
    comment: Optional[str]
    status: bool
    created_at: date
    updated_at: date