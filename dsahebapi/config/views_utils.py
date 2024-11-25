from ninja import Router
from .models import State, City, Location, Services, Specialization, University, College, Degree, Memberships, Registration
from .serializers import StateSerializer, CitySerializer, LocationSerializer, ServicesSerializer, SpecializationSerializer, UniversitySerializer, CollegeSerializer, DegreeSerializer, MembershipsSerializer, RegistrationSerializer

router = Router()

# Endpoints for State
@router.get("/states", response=list[StateSerializer])
def get_states(request):
    states = State.objects.all()
    return states

@router.post("/states", response=StateSerializer)
def create_state(request, data: StateSerializer):
    state = State.objects.create(**data.dict())
    return state

@router.get("/states/{state_id}", response=StateSerializer)
def get_state(request, state_id: int):
    state = State.objects.get(id=state_id)
    return state

@router.put("/states/{state_id}", response=StateSerializer)
def update_state(request, state_id: int, data: StateSerializer):
    state = State.objects.get(id=state_id)
    for attr, value in data.dict().items():
        setattr(state, attr, value)
    state.save()
    return state

# Repeat similar CRUD operations for other models (City, Location, Services, etc.)

# Example for City:
@router.get("/cities", response=list[CitySerializer])
def get_cities(request):
    cities = City.objects.all()
    return cities

@router.post("/cities", response=CitySerializer)
def create_city(request, data: CitySerializer):
    city = City.objects.create(**data.dict())
    return city

@router.get("/cities/{city_id}", response=CitySerializer)
def get_city(request, city_id: int):
    city = City.objects.get(id=city_id)
    return city


