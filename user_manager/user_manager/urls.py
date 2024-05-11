from django.urls import path
from . import views

urlpatterns = [
    path('greet/<str:name>/', views.greet, name='greet'),
]
