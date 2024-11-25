from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI
from config.views import router as config_router
from config.views_utils import router as utils_router
from listings.views import router as listings_router
from listings.views_doctor import router as listings_router_doctor

urlpatterns = [
    path('admin/', admin.site.urls),
]

api = NinjaAPI(    
    title="DsahebAPI",  # Replace this with your desired app name
    version="1.0.0",  # Optional: API version
    description="API Doctor Saheb"  # Optional: Add a description for better context
    )

# Add the 'config' app's router to the '/api/users/' URL path
api.add_router("/users/", config_router, tags=["Users"])
api.add_router("/utils/", utils_router, tags=["Utils"])
api.add_router("/listing/", listings_router, tags=["Listings"])
api.add_router("/listing/doctor/", listings_router_doctor, tags=["Doctor Listings"])

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/", api.urls),  # This sets up the '/api/' URL prefix for all API routes
]