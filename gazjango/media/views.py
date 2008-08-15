from django import forms
from django.core.urlresolvers import reverse
from django.http              import HttpResponseRedirect, Http404
from django.template          import RequestContext
from django.shortcuts         import get_object_or_404, render_to_response
from media.models     import MediaFile, ImageFile, MediaBucket
from media.forms      import MediaForm, ImageForm, BucketForm
from misc.files import handle_file_upload
import settings

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
    obj = get_object_or_404(MediaFile, bucket__slug=bucket, slug=slug)
    return HttpResponseRedirect(obj.data.url)

def show_form(request, kind="image", slug=None, template="custom-admin/form.html"):
    kind = _get_or_post('kind', request, kind)
    d = { 'image': (ImageForm, "Image Upload", ImageFile),
          'bucket': (BucketForm, "Media Bucket", MediaBucket) }
    fallback = (MediaForm, "Media Upload", MediaFile)
    form_type, title, model = d.setdefault(kind, fallback)
    
    model_form = isinstance(form_type, forms.ModelForm)
    obj = get_object_or_404(model, slug=slug) if (model_form and slug) else None
    extra = { 'instance': obj } if obj else {}
    
    if request.method == 'POST':
        form = form_type(request.POST, request.FILES, **extra)
        if form.is_valid():
            if model_form:
                form.save()
            else:
                bucket = form.cleaned_data['bucket']
                path = handle_file_upload(request.FILES['data'], bucket.slug)
                
                args = {}
                for k in form.cleaned_data:
                    if k not in ('authors', 'data'):
                        args[k] = form.cleaned_data[k]
                args['data'] = path
                
                thing = model.objects.create(**args)
                thing.users.add(*form.cleaned_data['authors'])
                
            return HttpResponseRedirect(reverse('reporter-admin'))
    else:
        if issubclass(model, MediaFile):
            extra['initial'] = {'authors': request.user.username}
        form = form_type(**extra)
    
    popup = _get_or_post('popup', request, False)
    
    data = {
        'form': form,
        'title': title,
        'base': "custom-admin/" + ("popup_base.html" if popup else "base.html"),
    }
    rc = RequestContext(request)
    return render_to_response(template, data, context_instance=rc)
