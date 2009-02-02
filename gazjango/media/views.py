from django import forms
from django.core.urlresolvers import reverse
from django.http              import HttpResponseRedirect, Http404
from django.template          import RequestContext
from django.shortcuts         import get_object_or_404, render_to_response
from gazjango.media.models import MediaFile, ImageFile, MediaBucket
from gazjango.misc.files   import handle_file_upload
from django.conf import settings

def _get_or_post(key, request, default=None):
    if key in request.GET:
        return request.GET[key]
    elif key in request.POST:
        return request.POST[key]
    else:
        return default

def bucket(request, bucket):
    return render_to_response("base.html", locals())

def file(request, bucket, slug):
    try:
        obj = get_object_or_404(MediaFile, bucket__slug=bucket, slug=slug)
    except Http404:
        obj = get_object_or_404(ImageFile, bucket__slug=bucket, slug=slug)
    return HttpResponseRedirect(obj.data.url)
