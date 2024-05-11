from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

@require_http_methods(["GET"])
def greet(request, name):
    response_data = {
        'message': f'Hello, {name}!'
    }
    return JsonResponse(response_data)
