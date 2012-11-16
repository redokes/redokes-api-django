import json
#import jsonpickle
import logging
import urllib2
import time
import hashlib
import os
import tempfile
#from PIL import Image as PILImage
from django.conf import settings

"""""""""""""""""""""""""""""""""""""""
 Image manipulation class
"""""""""""""""""""""""""""""""""""""""  
class Image():
    image = None
    tmp_file = None
    
    def __init__(self):
        pass
    
    def load_path(self, path):
        """
        Load an image from a path
        """
        
        self.path = path
        self.image = PILImage.open(path)
        
    def load_url(self, url):
        """
        Create a temporary file from a url. This file will be
        used as the image.
        """
        #Attempt to open the url
        try:
            url_handler = urllib2.urlopen(url, None, 0.2)
        except:
            raise
        
        #Create the temp file
        file_name, file_extension = os.path.splitext(url)
        file_hash = hashlib.md5(str(time.time())).hexdigest()
        file_path = '/tmp/{0}{1}'.format(file_hash, file_extension)
        f = tempfile.NamedTemporaryFile()
        f.write(url_handler.read())
        #f.close()
        self.load_path(f.name)
        
    def thumbnail_crop(self, size=100):
        """
        Crop a thumbnail to a square
        """
        
        #Compute the crop dimensions
        width, height = self.image.size
        if width > height:
            delta = width - height
            left = int(delta/2)
            upper = 0
            right = height + left
            lower = height
        else:
            delta = height - width
            left = 0
            upper = int(delta/2)
            right = width
            lower = width + upper
        
        #Crop and thumbnail the image
        self.image = self.image.crop((left, upper, right, lower))
        self.image.thumbnail((size,size), PILImage.ANTIALIAS)
        
    def crop(self, x, y, width, height):
        self.image = self.image.crop((x, y, width + x, height + y))
        
    def resize_ratio(self, width, ratio=1):
        image_width, image_height = self.image.size
        width_percent = (width/float(image_width))
        height = int((float(image_height) * float(width_percent)))
        self.image = self.image.resize((width,height), PILImage.ANTIALIAS)
        
    def save(self, path):
        """
        Save the image to a path
        """
        
        self.image.save(path)
    
    
"""""""""""""""""""""""""""""""""""""""
 Utility methods
"""""""""""""""""""""""""""""""""""""""
def apply_config(instance, kwargs):
    for key, value in kwargs.iteritems():
        setattr(instance, key, value)
        
def config(apply_config={}, **kwargs):
    config = dict(**kwargs)
    config.update(apply_config or {})
    return config
        
def is_production():
    environment = ''
    try:
        environment = settings.ENVIRONMENT
    except: 
        environment = "development"
    if environment == "production":
        return True
    return False

def is_development():
    environment = ''
    try:
        environment = settings.ENVIRONMENT
    except: 
        environment = "development"
    if environment == "development":
        return True
    return False

def image_test():
    img = Image();
    img.load_url("http://nooga.retickr.com/assets/d3ebf96d0a6e270af13414f361764cda26471.jpg")
    img.thumbnail_crop(100)
    img.save(settings.ROOT_PATH + "tmp/testing.jpg")

def dump(o):
    logging.debug(encode(o))
    
def encode(o):
    return json.dumps(json.loads(jsonpickle.encode(o)), indent=4, sort_keys=True)
    
def dump_encode(o):
    try:
        output = o.__dict__
    except:
        o.__dict__ = {"test": "test"}
    return o.__dict__
def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]
    
def update_get_params(request, params):
    get_params = request.GET.copy()
    get_params.update(params)
    request.GET = get_params

def update_post_params(request, params):
    post_params = request.POST.copy()
    post_params.update(params)
    request.POST = post_params
