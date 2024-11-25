from pydantic import BaseModel
from ninja import Schema
from typing import Optional
from datetime import date
from uuid import UUID

class OTP_Request(BaseModel):
    phone_number: str

class OTP_Verify(BaseModel):
    phone_number: str
    otp: str


class User_Create(BaseModel):
    mobile: str
    usertype: str

    class Config:
        from_attributes = True

class User_Profile(BaseModel):
    name: str
    mobile: str
    usertype: str
    is_verified: bool

    class Config:
        from_attributes = True


class PatientProfileSchema(Schema):
    id: Optional[UUID]  # Updated to use UUID
    mobile: str
    email: Optional[str]
    dob: Optional[date]
    sex: Optional[str]
    address_line1: Optional[str]
    landmark: Optional[str]
    city: Optional[str]
    pin: Optional[str]

class PatientProfileResponseSchema(PatientProfileSchema):
    created_at: date
    updated_at: date


class StateSerializer(Schema):
    id: int
    name: str
    

class CitySerializer(Schema):
    id: int
    name: str
    state: StateSerializer

class LocationSerializer(Schema):
    id: int
    name: str
    cities: CitySerializer

class ServicesSerializer(Schema):
    id: int
    name: str
    description: str

class SpecializationSerializer(Schema):
    id: int
    name: str

class UniversitySerializer(Schema):
    id: int
    name: str
    state: StateSerializer
    city: CitySerializer
    pincode: str

class CollegeSerializer(Schema):
    id: int
    name: str
    state: StateSerializer
    city: CitySerializer
    pincode: str
    affiliation_type: str
    affliated_to: UniversitySerializer

class DegreeSerializer(Schema):
    id: int
    name: str

class MembershipsSerializer(Schema):
    id: int
    name: str

class RegistrationSerializer(Schema):
    id: int
    name: str