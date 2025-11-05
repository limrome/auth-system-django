from rest_framework.views import exception_handler
from rest_framework.exceptions import NotAuthenticated

def custom_exception_handler(exc, context):
    
    response = exception_handler(exc, context)
    
    if response is not None and response.status_code == 403:
        request = context['request']
        if not request.user or not request.user.is_authenticated:
            new_exc = NotAuthenticated("Учетные данные не были предоставлены.")
            response = exception_handler(new_exc, context)
    
    return response