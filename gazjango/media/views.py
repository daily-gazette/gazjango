from media.models        import MediaFile
from django.shortcuts    import get_object_or_404, render_to_response
from settings            import _base
import django.views.static

def bucket(request, bucket):
    return render_to_response(base.html, locals())

def file(request, bucket, slug):
    obj = get_object_or_404(MediaFile, bucket__slug=bucket, slug=slug)
    return django.views.static.serve(request, obj.data, document_root=_base)
