import os
import settings

def handle_file_upload(f, bucket_name):
    """Save an uploaded file into the appropriate location."""
    
    directory = os.path.join(settings.MEDIA_ROOT, bucket_name)
    if not os.path.isdir(directory):
        os.makedirs(directory)
    path = os.path.join(directory, f.name)
    
    dest = open(path, 'wb+')
    for chunk in f.chunks():
        dest.write(chunk)
    return path
