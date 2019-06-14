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


def recommend_style(arr):
    '''Accepts an array of 0-3 strings describing the clothing. Matches it up with a possible style based on our hard-coded dictionary and appends it to the array. Returns appended array.'''
    style = {'plain, shirt': 'the_office',
            'plain, blouse': 'the_office',
             'plain, sweater':'the_office',
             'plain, dress': 'the_office',
             'plain, blazer': 'the_office',
             'plain, skirt': 'the_office',
            'cotton, dot, dress': 'nautical',
           'cotton, dot, cardigan': 'nautical',
           'cotton, dot, blouse': 'nautical',
           'cotton, stripe, dress': 'nautical',
           'cotton, stripe, cardigan': 'nautical',
           'cotton, stripe, blouse': 'nautical',
           'linen, dot, dress': 'nautical',
           'linen, dot, cardigan': 'nautical',
           'linen, dot, blouse': 'nautical',
           'linen, stripe, dress': 'nautical',
           'linen, stripe, cardigan': 'nautical',
           'linen, stripe, blouse': 'nautical',
           'lace, dot, dress': 'nautical',
           'lace, dot, cardigan': 'nautical',
           'lace, dot, blouse': 'nautical',
           'lace, stripe, dress': 'nautical',
           'lace, stripe, cardigan': 'nautical',
           'lace, stripe, blouse': 'nautical',
            'palm, shorts': 'by_the_beach',
            'palm, tank': 'by_the_beach',
            'palm, tee' :'by_the_beach',
            'palm, romper': 'by_the_beach',
            'floral, shorts': 'by_the_beach',
            'floral, tank': 'by_the_beach',
            'floral, tee' :'by_the_beach', 
            'floral, romper': 'by_the_beach',
             'cotton, colorblock, tank': 'street_style',
            'denim, graphic, tee': 'street_style',
                'denim, graphic, jeans': 'street_style',
                'denim, graphic, jacket': 'street_style',
                'denim, graphic, hoodie': 'street_style',
                'leather, graphic, tee': 'street_style',
                'leather, graphic, jeans': 'street_style',
                'leather, graphic, jacket': 'street_style',
                'leather, graphic, hoodie': 'street_style',
                'spandex, colorblock, legging': 'athlesiure',
             'spandex, colorblock, exercise_shorts': 'athelesiure',
             'spandex, colorblock, tee': 'athelesiure',
             'spandex, colorblock, sweatpants' : 'athelesiure',
             'spandex, colorblock, hoodie': 'athelesiure',
            'lace, stripe, shirt': 'night_out',
             'lace, stripe, skirt': 'night_out',
             'lace, stripe, jeans': 'night_out',
              'lace, plain, dress': 'night_out',
            'chiffon, paisley, dress': 'festival',
           'chiffon, zig_zag, dress': 'festival',
           'chiffon, distressed, dress': 'festival',
             'cotton, plain, shorts': 'festival'
    }

    attr_cloth = []
    attr_cloth.append(arr[0].lower())
    attr_cloth.append(arr[1].lower())
    attr_cloth.append(arr[2].lower())
    attr_cloth = tuple(attr_cloth)
    attr_cloth = ', '.join(attr_cloth)

    return arr.append(style.get(attr_cloth, None))


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

    #### QUESTION - we need to add 0 or None if model gives us no prediction. Does it do that already?

    fabric_predictions = [class_fabric.get(prediction[0]) for prediction in fabric_predictions]
    pattern_predictions = [class_pattern.get(prediction[0]) for prediction in pattern_predictions]
    type_predictions = [class_type.get(prediction[0]) for prediction in type_predictions]

    # getting our final dictionary of image_paths as keys and 3 predictions as a list as values
    path_pred = {img_path : [fabric_prediction, pattern_prediction, type_prediction] for img_path, fabric_prediction, pattern_prediction, type_prediction in zip(img_paths, fabric_predictions, pattern_predictions, type_predictions)}

    # appending a recommendation to our prediction using helper function
    for arr in path_pred.values():
        arr = recommend_style(arr)

    # clearing backend keras session after prediction was complete:
    K.clear_session()

    return path_pred
    


# testing function:
# -----------

from pathlib import Path
p = Path("static") / 'uploads'
filepaths = [x for x in p.iterdir() if x.is_file()]

print(predict_images(filepaths))