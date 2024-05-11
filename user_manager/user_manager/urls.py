from django.urls import path
from views import greet

urlpatterns = [
    path('greet/<str:name>/', greet, name='greet'),
]
