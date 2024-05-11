from django.http import HttpResponse

def greet(request, name):
    return HttpResponse(f"Hello, {name}!")