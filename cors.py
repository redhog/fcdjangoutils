import django.http

def cors(fn = None, origins = '*', methods = ['POST', 'GET', 'OPTIONS'], headers = ['Origin', 'X-Requested-With', 'Content-Type', 'Accept'], credentials = False):
    """Decorator to set Cross Origin Resource Sharing headers and allow a specific view to be used across sites. Very usefull together with json_view.""" 
    def cors(fn):
        def cors(request, *arg, **kw):
            if 'HTTP_ACCESS_CONTROL_REQUEST_METHOD' in request.META:
                response = django.http.HttpResponse()
            else:
                response = fn(request, *arg, **kw)
            response['Access-Control-Allow-Origin'] = origins
            if credentials: response['Access-Control-Allow-Credentials'] = 'true'
            response['Access-Control-Allow-Methods'] = ', '.join(methods)
            response['Access-Control-Allow-Headers'] = ', '.join(headers)
            return response
        return cors
    if fn is None:
        return cors
    return cors(fn)
