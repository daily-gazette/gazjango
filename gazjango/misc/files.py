import os, os.path
from django.conf import settings

def handle_file_upload(f, folder_name, return_full_path=False):
    """Save an uploaded file into the appropriate location."""
    
    directory = os.path.join(settings.MEDIA_ROOT, folder_name)
    if not os.path.isdir(directory):
        os.makedirs(directory)
    
    name = f.name
    while os.path.isfile(os.path.join(directory, name)):
        name = '_' + name
    
    dest = open(os.path.join(directory, name), 'wb+')
    for chunk in f.chunks():
        dest.write(chunk)

    if return_full_path:
        return os.path.join(directory, name)
    else:
        return os.path.join(folder_name, name)
