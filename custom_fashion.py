# IMPORTS FOR CNN IMAGE PREPROCESSING
import numpy as np
from keras.preprocessing import image

# IMPORTS for CNN ML Models:
from keras.models import load_model
from keras import backend as K

# common imports for dealing with model path:
import os
from pathlib import Path


def image_preprocess(img_path):
    '''helper function to preprocess for ML model'''

    # Load the image file, resizing it to 224x224 pixels (required by this model)
    img = image.load_img(img_path, target_size=(224, 224))

    # Convert the image to a numpy array
    image_array = image.img_to_array(img)

    # Normalize the input image's pixel values to the range used when training the neural network
    image_array /= 255.0

    # reshape the input to 4 dimensions required by the model -- it expects an array of images, and here we only have one image
    # https://stackoverflow.com/questions/41563720/error-when-checking-model-input-expected-convolution2d-input-1-to-have-4-dimens
    image_array = np.expand_dims(image_array, axis=0)
    
    return image_array


def predict_images(img_paths):
    '''identifying images using our CNN ML model. Accepts an array of paths to uploaded images. Returns a dictionary / hashmap of imgpaths as keys and an array of highest predicted and percent confidence as values'''

    # clearing backend keras session to solve tensorflow threading issue:
    K.clear_session()

    # preprocess our images using the helper function
    image_arrays = [image_preprocess(img_path) for img_path in img_paths]

    # load our customized fashion pre-trained models
    fabric = load_model(os.path.abspath(str(Path('models') / 'vgg_weights_fabric.hdf5')))
    pattern = load_model(os.path.abspath(str(Path('models') / 'vgg_weights_data_aug_frozen_pattern_EI')))
    type_clothing = load_model(os.path.abspath(str(Path('models') / 'Cloth_type.hdf5')))

    # Run the images through the CNN models to make predictions
    fabric_predictions = [fabric.predict_classes(image_array) for image_array in image_arrays]
    pattern_predictions = [pattern.predict_classes(image_array) for image_array in image_arrays]
    type_predictions = [type_clothing.predict_classes(image_array) for image_array in image_arrays]

    # Link up predictions to the names of the predicted classes based on definitions from our trained model:
    class_fabric = {
    0: 'Chiffon',
    1: 'Cotton',
    2: 'Denim',
    3: 'Lace',
    4: 'Leather',
    5: 'Linen',
    6: 'Ribbed',
    7: 'Spandez',
    }

    class_pattern = {
    0: 'Colorblock',
    1: 'Distressed',
    2: 'Dot',
    3: 'Floral',
    4: 'Graphic',
    5: 'Paisley',
    6: 'Plaid',
    7: 'Plain',
    8: 'Stripe',
    }

    class_type = {
    0: 'Blazer',
    1: 'Blouse',
    2: 'Cardigan',
    3: 'Dress',
    4: 'Exerciseshort',
    5: 'Hoodies',
    6: 'Jeans',
    7: 'Romper',
    8: 'Shorts',
    9: 'Skirt',
    10: 'Tank',
    11: 'Tee'
    }

    fabric_predictions = [class_fabric.get(prediction[0]) for prediction in fabric_predictions]
    pattern_predictions = [class_pattern.get(prediction[0]) for prediction in pattern_predictions]
    type_predictions = [class_type.get(prediction[0]) for prediction in type_predictions]

    print(fabric_predictions)
    print(pattern_predictions)
    print(type_predictions)

    # getting our final dictionary of image_paths as keys and highest predicted decoded string with percent confidence array as values. Here we are filtering predictions to be passed ONLY if confidence is at least 60 percent. Otherwise, we are passing 0 and will allow Jinja templating engine to check if prediction was passed.
    # path_pred = {img_path : ([decoded[1], str(round(decoded[2] * 100, 2)) + '%'] if decoded[2] >= 0.6 else [decoded[1], 0]) for img_path, decoded in zip(img_paths, decoded_array)}

    # clearing backend keras session after prediction was complete:
    K.clear_session()

    # return path_pred
    


# testing function:
# -----------

# from pathlib import Path
# p = Path("static") / 'uploads'
# filepaths = [x for x in p.iterdir() if x.is_file()]

# print(predict_images(filepaths))