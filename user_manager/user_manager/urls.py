from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from .views import create_customer_application, create_update_application_basic_info, get_basic_information

urlpatterns = [
    path('create-application/', csrf_exempt(create_customer_application), name='create_application'),
    path('update-application/<int:application_id>/', csrf_exempt(create_update_application_basic_info), name='update_application'),
    path('get-basic-information/<int:application_id>/', csrf_exempt(get_basic_information), name='get_basic_information'),
]
