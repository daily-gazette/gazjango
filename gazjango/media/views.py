from django.http      import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from media.models     import MediaFile
import settings

def bucket(request, bucket):
    return render_to_response(base.html, locals())

def file(request, bucket, slug):
    obj = get_object_or_404(MediaFile, bucket__slug=bucket, slug=slug)
    return HttpResponseRedirect('/static/%s' % obj.data)
