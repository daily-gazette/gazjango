from gazjango.stackedpages.views import page
from django.http import Http404
from django.conf import settings

class StackedPageFallbackMiddleware(object):
    def process_response(self, request, response):
        if response.status_code != 404:
            return response # nothing to do
        try:
            return page(request, request.path_info)
        except Http404:
            # there is no such page: 
            # return to your regularly scheduled 404 error
            return response
        except:
            if settings.DEBUG:
                raise
            return response
    
