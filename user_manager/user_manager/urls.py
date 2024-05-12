from django.urls import path
from .views import create_customer_application
from .views import update_customer_application
from .views import get_basic_information

urlpatterns = [
    path('create-application/', create_customer_application, name='create_application'),
    path('update-application/<int:application_id>/', update_customer_application, name='update_application'),
     path('get-basic-information/<int:application_id>/', get_basic_information, name='get_basic_information'),
]
