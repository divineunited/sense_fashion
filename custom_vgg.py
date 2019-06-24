# IMPORTS FOR CNN IMAGE PREPROCESSING
import numpy as np
from keras.preprocessing import image
from skimage import transform

# IMPORTS for CNN ML Models:
from keras.applications import vgg16
import tensorflow as tf

# Pillow image for orientation fixing:
from PIL import Image, ExifTags


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

    # this returns the PIL image object
    return img




def image_preprocess(img_path):
    '''helper function to preprocess for ML model'''

    # Load the image file, resizing it to 224x224 pixels (required by this model)
    img = image.load_img(img_path, target_size=(224, 224))

    # Convert the image to a numpy array
    image_array = image.img_to_array(img)

    # reshape the input to 4 dimensions required by the model -- it expects an array of images, and here we only have one image
    # https://stackoverflow.com/questions/41563720/error-when-checking-model-input-expected-convolution2d-input-1-to-have-4-dimens
    image_array = np.expand_dims(image_array, axis=0)

    # Normalize the input image's pixel values to the range used when training the neural network
    image_array = vgg16.preprocess_input(image_array)
    
    return image_array


def predict_images(img_paths, model, graph):
    '''identifying images using our CNN ML model. Accepts an array of paths to uploaded images and our vgg model and a TF Graph for thread issues. Returns a dictionary / hashmap of imgpaths as keys and an array of highest predicted and percent confidence as values'''

    # preprocess our images using the helper function
    image_arrays = [image_preprocess(img_path) for img_path in img_paths]

    # Run the images through the CNN model to make predictions
    predictions = []
    for image_array in image_arrays:
        # need a tensorflow session for each image
        sess = tf.Session()
        init = tf.global_variables_initializer() # https://stackoverflow.com/questions/36007883/tensorflow-attempting-to-use-uninitialized-value-in-variable-initialization
        sess.run(init)
        with graph.as_default(): # must use the tf graph to manage thread resources
            predictions.append(model.predict(image_array))
        # closing our TF session
        sess.close
        tf.reset_default_graph() # Clears the default graph stack and resets the global default graph.

    # Look up the names of the predicted classes. This is a function to decode the predictions based on VGG16 imagenet trained classes. It gives us 5 predictions with probabilities in order. We just want the top prediction.
    decoded_array = [vgg16.decode_predictions(prediction)[0][0] for prediction in predictions]

    # getting our final dictionary of image_paths as keys and highest predicted decoded string with percent confidence array as values. 
    path_pred = {img_path : ([decoded[1], str(round(decoded[2] * 100, 2)) + '%']) for img_path, decoded in zip(img_paths, decoded_array)}
    # Here we are filtering predictions to be passed ONLY if confidence is at least 60 percent. Otherwise, we are passing 0 and will allow Jinja templating engine to check if prediction was passed.
    # path_pred = {img_path : ([decoded[1], str(round(decoded[2] * 100, 2)) + '%'] if decoded[2] >= 0.6 else [decoded[1], 0]) for img_path, decoded in zip(img_paths, decoded_array)}


    return path_pred
    


# testing function:
# -----------

# from pathlib import Path
# p = Path("static") / 'uploads'
# filepaths = [x for x in p.iterdir() if x.is_file()]

# print(predict_images(filepaths))