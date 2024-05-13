from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from .services.user_service import create_customer_application_service
from .services.user_service import create_update_application_basic_info_service
from .services.user_service import get_basic_information_by_application_service
import traceback
import sys
import json
from .modules.otp_module import OTPModule

@require_http_methods(['POST'])
def send_otp_to_phone(request):
    try:
        # Assuming JSON data is sent in the request; validate as needed
        data = json.loads(request.body.decode('utf-8'))
        
        # Payload Checks
        if len(data) != 1:
            return HttpResponseBadRequest("Invalid payload fields")
        if 'phone_number' not in data:
            return HttpResponseBadRequest("Missing required field: phone_number")
        
        # Extract phone number from request
        phone_number = data['phone_number']
        
        # Call the service function to send an OTP
        otp_module = OTPModule()
        success = otp_module.send_otp(phone_number)
        print(success)
        
        if success:
            return JsonResponse({'message': 'OTP sent successfully.', 'phone_number': phone_number})
        else:
            return HttpResponseBadRequest(f"Failed to send OTP")
    
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        return HttpResponseBadRequest(f"An error occurred: {str(e)}")
    
@require_http_methods(['POST'])
def create_customer_application(request):
    try:
        # Assuming JSON data is sent in request; validate as needed
        data = json.loads(request.body.decode('utf-8'))
        
        # Payload Checks
        required_keys = ["document_type", "document_number"]
        if len(data) != len(required_keys):
            return HttpResponseBadRequest("Invalid payload fields")
        if not all(key in data for key in required_keys):
            return HttpResponseBadRequest("Missing required fields")

        # Extract data from request
        document_type = data['document_type']
        document_number = data['document_number']           

        # Call the service function
        application_id = create_customer_application_service(
            document_type, document_number
        )

        # Return the application ID
        return JsonResponse({'application_id': application_id})

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        return HttpResponseBadRequest(f"An error occurred: {str(e)}")
    
@require_http_methods(['POST'])
def create_update_application_basic_info(request, application_id):
    try:
        # Assuming JSON data is sent in request; validate as needed
        data = json.loads(request.body.decode('utf-8'))
        
        # Payload Checks
        required_keys = ["first_name", "last_name", "country", "state", "city", "address", "mobile_number", "email"]
        if len(data) != len(required_keys):
            return HttpResponseBadRequest("Invalid payload fields")
        if not all(key in data for key in required_keys):
            return HttpResponseBadRequest("Missing required fields")

        # Extract data from request
        first_name = data['first_name']
        last_name = data['last_name']
        country = data['country']
        state = data['state']
        city = data['city']
        address = data['address']
        mobile_number = data['mobile_number']
        email = data['email']

        # Call the service function
        result = create_update_application_basic_info_service(
            application_id, first_name, last_name, country, state, city, address, mobile_number, email
        )

        # Handle service function responses
        if result == "Application not found.":
            return HttpResponseBadRequest(result)
        if result == "This is not the most recent application. Updates can only be made to the most recent application.":
            return HttpResponseBadRequest(result)

        # If all goes well, return the application ID
        return JsonResponse({'application_id': result})

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        return HttpResponseBadRequest(f"An error occurred: {str(e)}")

@require_http_methods(['GET'])
def get_basic_information(request, application_id):
    try:
        # Call the service function
        result = get_basic_information_by_application_service(application_id)

        # Handle possible errors
        if 'error' in result:
            return HttpResponseBadRequest(result['error'])

        # Return the decrypted information as JSON
        return JsonResponse(result)

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        return HttpResponseBadRequest(f"An error occurred: {str(e)}")