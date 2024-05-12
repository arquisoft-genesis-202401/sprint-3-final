from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from .services.user_service import create_customer_application_basic_info
from .services.user_service import update_customer_application_basic_info
from .services.user_service import get_basic_information_by_application_id

@require_http_methods(['POST'])
def create_customer_application(request):
    try:
        # Assuming JSON data is sent in request; validate as needed
        data = request.POST

        # Extract data from request
        document_type = data.get('document_type')
        document_number = data.get('document_number')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        country = data.get('country')
        state = data.get('state')
        city = data.get('city')
        address = data.get('address')
        mobile_number = data.get('mobile_number')
        email = data.get('email')

        # Check required fields
        if not all([document_type, document_number, first_name, last_name, country, state, city, address, mobile_number, email]):
            return HttpResponseBadRequest("Missing required fields")

        # Call the service function
        application_id = create_customer_application_basic_info(
            document_type, document_number, first_name, last_name, country, state, city, address, mobile_number, email
        )

        # Return the application ID
        return JsonResponse({'application_id': application_id})

    except Exception as e:
        return HttpResponseBadRequest(f"An error occurred: {str(e)}")
    
@require_http_methods(['POST'])
def update_customer_application(request, application_id):
    try:
        # Assuming JSON data is sent in request; validate as needed
        data = request.POST

        # Extract data from request
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        country = data.get('country')
        state = data.get('state')
        city = data.get('city')
        address = data.get('address')
        mobile_number = data.get('mobile_number')
        email = data.get('email')

        # Check required fields
        if not all([application_id, first_name, last_name, country, state, city, address, mobile_number, email]):
            return HttpResponseBadRequest("Missing required fields")

        # Call the service function
        result = update_customer_application_basic_info(
            application_id, first_name, last_name, country, state, city, address, mobile_number, email
        )

        # Handle service function responses
        if result == "Basic Information not found for this application.":
            return HttpResponseBadRequest(result)

        # If all goes well, return the application ID
        return JsonResponse({'application_id': result})

    except Exception as e:
        return HttpResponseBadRequest(f"An error occurred: {str(e)}")

@require_http_methods(['GET'])
def get_basic_information(request, application_id):
    try:
        # Call the service function
        result = get_basic_information_by_application_id(application_id)

        # Handle possible errors
        if 'error' in result:
            return HttpResponseBadRequest(result['error'])

        # Return the decrypted information as JSON
        return JsonResponse(result)

    except Exception as e:
        return HttpResponseBadRequest(f"An error occurred: {str(e)}")