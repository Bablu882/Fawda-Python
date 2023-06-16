from django.http import HttpResponseNotFound
from rest_framework.response import Response

class CustomNotFoundMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # If the response has status code 404 (Page Not Found)
        if response.status_code == 404:
            return HttpResponseNotFound("This is an incorrect URL.")
        
        return response
