# views.py
from ninja import Router
from django.shortcuts import get_object_or_404
from .models import Listing
from .serializers import ListingSerializer
from django.db.models import Q

router = Router()

@router.get("/listings", response=ListingSerializer)
def list_listings(request):
    """
    List all active listings publicly.
    Can be filtered by location, specialization, service, etc.
    """
    query = request.GET.get('query', '')
    listings = Listing.objects.filter(
        Q(title__icontains=query) |
        Q(services__icontains=query) |
        Q(specializations__icontains=query) |
        Q(state__name__icontains=query) |
        Q(city__name__icontains=query) |
        Q(location__name__icontains=query)
    ).filter(is_active=True)  # Ensure only active listings are shown

    return listings

@router.get("/listings/{listing_id}", response=ListingSerializer)
def get_listing(request, listing_id: int):
    """
    Retrieve a listing by its ID (public view).
    """
    listing = get_object_or_404(Listing, pk=listing_id, is_active=True)
    return listing
