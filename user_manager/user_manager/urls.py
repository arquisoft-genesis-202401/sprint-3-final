from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from .views import create_customer_application, update_customer_application, get_basic_information

urlpatterns = [
    path('create-application/', csrf_exempt(create_customer_application), name='create_application'),
    path('update-application/<int:application_id>/', csrf_exempt(update_customer_application), name='update_application'),
    path('get-basic-information/<int:application_id>/', csrf_exempt(get_basic_information), name='get_basic_information'),
]
