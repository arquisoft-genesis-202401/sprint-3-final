from django.urls import path
import views

urlpatterns = [
    path('greet/<str:name>/', views.greet, name='greet'),
]
