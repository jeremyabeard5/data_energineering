from django.urls import path
from .views import tableau_url

urlpatterns = [
    path('tableau-url/', tableau_url, name='tableau-url'),
]
