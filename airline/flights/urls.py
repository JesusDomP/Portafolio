from django.urls import path
from .views import FlightPassengersView

urlpatterns = [
    path("<int:flight_id>/passengers/", FlightPassengersView.as_view(), name="flight-passengers"),
]
