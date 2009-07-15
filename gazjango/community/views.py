import datetime
import calendar
import re

from django.views.decorators.cache  import cache_page
from django.db.models import Q
from django.template  import RequestContext
from django.http      import Http404, HttpResponse, HttpResponseRedirect
from django.core.urlresolvers   import reverse
from django.core.exceptions     import ObjectDoesNotExist
from django.shortcuts           import render_to_response, get_object_or_404

from tumblelog.agro.models              import Entry,Category
from tumblelog.agro.sources.flickr      import *
from tumblelog.agro.sources.delicious   import *
from tumblelog.agro.sources.twitter     import *
from tumblelog.gmaps.models             import *

def homepage(request, template="index.html"):
    entries = Entry.published.get_entries()
    objList = []
    for entry in entries:
        if entry.source_type == "photo":
            additionalInformation = entry.object.image
        else:
            additionalInformation = ""
        objList = objList + [(entry,additionalInformation)]
        
    data = {
        'entries': objList,
    }
    rc = RequestContext(request)
    return render_to_response(template, data, context_instance=rc)
    
def photo(request, template="index.html"):
    entries = Entry.published.get_photos()
    objList = []
    for entry in entries:
        additionalInformation = entry.object.image
        objList = objList + [(entry,additionalInformation)]

    data = {
        'entries': objList,
    }
    rc = RequestContext(request)
    return render_to_response(template, data, context_instance=rc)