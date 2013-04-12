import fcdjangoutils.responseutils
import threading

class EarlyResponse(object):
    def process_exception(self, request, exception):
        if isinstance(exception, fcdjangoutils.responseutils.EarlyResponseException):
            return exception.get_response(request)

_requests = threading.local()

def get_request():
    return _requests.request

class GlobalRequestMiddleware(object):
    def process_request(self, request):
        _requests.request = request
