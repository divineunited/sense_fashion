### IMPORTS FOR CNN IMAGE PREPROCESSING
# from keras.models import load_model
# import tensorflow as tf
import numpy as np
from keras.preprocessing import image
from skimage import transform

from PIL import Image, ExifTags
import io


def fix_orientation(file_like_object):
    '''Accepts a file object, loads it as a PIL image, checks for ExifTags to reorient smart phone taken images if needed, and then passes back the image object'''
    
    img = Image.open(file_like_object)
    # print(img.size) # flag to see initial dimensions
    
    if hasattr(img, '_getexif'):
        exifdata = img._getexif()
        try:
            orientation = exifdata.get(274)
            # print('has orientation:')
            # print(orientation)
        except:
            # There was no EXIF Orientation Data
            orientation = 1
    else:
        orientation = 1
    
    # fixing orientation if needed:
    if orientation == 3:
        img=img.rotate(180, expand=True)
    elif orientation == 6:
        img=img.rotate(270, expand=True)
    elif orientation == 8:
        img=img.rotate(90, expand=True)
        
    # print(img.size) # flag to see updated dimensions

    return img




def image_preprocess(img_path):
    '''preprocessing for ML model'''
    # new shape of image according to what we trained our model on
    new_shape = (50, 50, 3)
    # Load the image from disk
    img = image.load_img(img_path)
    # Convert the image to a numpy array
    image_array = image.img_to_array(img)
    # resize the image (must be done after it has turned into a np array):
    image_array = transform.resize(image_array, new_shape, anti_aliasing=True)
    # scaling the image data to fall between 0-1 since images have 255 brightness values:
    image_array /= 255
    # The input shape we have defined is the shape of a single sample. The model itself expects some array of samples as input (even if its an array of length 1). Your output really should be 4-d, with the 1st dimension to enumerate the samples. i.e. for a single image you should return a shape of (1, 50, 50, 3).
    # add an extra dimension
    image_array = np.expand_dims(image_array, axis=0)
    return image_array