# IMPORTS FOR CNN IMAGE PREPROCESSING
import numpy as np
from keras.preprocessing import image

# IMPORTS for CNN ML Models:
from keras.models import load_model
from keras import backend as K

# common imports for dealing with model path:
import os
from pathlib import Path
import random


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


def get_style(arr):
    '''This helper function accepts an array of 3 labels (fabric, pattern, clothing) and uses clothing and pattern to define a style of clothing which will then be used to generate random image recommendations from our static img styles folder.'''
    clothing = arr[2]
    pattern = arr[1]

    # smart / office Styles:
    if clothing in ['Blazer']:
        return arr.append('smart_blazer') # recommend things that go well with blazer
    elif clothing in ['Blouse', 'Cardigan']:
        return arr.append('smart_blouse_cardigan')
    elif clothing in ['Skirt'] and pattern in ['Plain']:
        return arr.append('smart_skirt')
    # nautical styles:
    elif clothing in ['Dress', 'Skirt'] and pattern in ['Dot', 'Stripe']:
        return arr.append('nautical_dress_skirt')
    elif clothing in ['Shorts'] and pattern in ['Dot', 'Plain', 'Stripe']:
        return arr.append('nautical_shorts_tee')
    elif clothing in ['Tee'] and pattern in ['Dot', 'Stripe']:
        return arr.append('nautical_shorts_tee')
    # beach styles:
    elif pattern in ['Floral']:
        return arr.append('beach_floral')
    elif clothing in ['Tank']:
        return arr.append('beach_tank_tee')
    elif clothing in ['Tee'] and pattern in ['Colorblock', 'Distressed', 'Paisley', 'Plaid']:
        return arr.append('beach_tank_tee')
    elif clothing in ['Romper'] and pattern in ['Dot', 'Stripe', 'Floral']:
        return arr.append('beach_romper')
    elif clothing in ['Shorts'] and pattern in ['Colorblock', 'Distressed', 'Paisley', 'Plaid']:
        return arr.append('beach_shorts')
    # athleasure styles:
    elif clothing in ['Exercise shorts']:
        return arr.append('athleasure')
    elif clothing in ['Hoodie']:
        return arr.append('athleasure')
    elif clothing in ['Tee'] and pattern in ['Plain']:
        return arr.append('athleasure')
    # night_out styles:
    elif clothing in ['Dress', 'Skirt'] and pattern in ['Colorblock', 'Distressed', 'Paisley', 'Plaid', 'Plain']:
        return arr.append('night_out_female')
    elif clothing in ['Romper'] and pattern in ['Colorblock', 'Distressed', 'Paisley', 'Plaid', 'Plain']:
        return arr.append('night_out_female')
    # street styles:
    elif clothing in ['Jeans']:
        return arr.append('street_jeans')
    elif pattern in ['Graphic']:
        return arr.append('street_graphic_pattern')
    # eclectic style (undefined)
    else:
        return arr.append('eclectic')

def get_recommendations(arr, n=4):
    '''This function accepts a prediction array with a style at position 3 that has a corresponding system folder and then chooses n number of random images from that folder and appends that list to the original array along with a list of corresponding filenames.'''

    style = arr[3]
    p = Path('static') / 'img' / 'styles' / style
    filepaths = [x for x in p.iterdir() if x.is_file()]
    filepaths = random.sample(filepaths, n) # create a list of n random image filepaths
    filenames = [filepath.stem for filepath in filepaths] # create another list of the corresponding filenames without extension

    # appending each list to the array (adding 2 items of n length)
    arr.append(filepaths)
    arr.append(filenames)

    return arr

def predict_images(img_paths):
    '''identifying images using our CNN ML model. Accepts an array of paths to uploaded images. Returns a dictionary / hashmap of imgpaths as keys and an array of highest predicted and percent confidence as values'''

    # clearing backend keras session to solve tensorflow threading issue:
    K.clear_session()

    # preprocess our images using the helper function
    image_arrays = [image_preprocess(img_path) for img_path in img_paths]

    # load our customized fashion pre-trained models
    # fabric = load_model(os.path.abspath(str(Path('models') / 'vgg_weights_fabric.hdf5'))) # not accurate enough
    pattern = load_model(os.path.abspath(str(Path('models') / 'vgg_weights_data_aug_frozen_pattern_EI')))
    type_clothing = load_model(os.path.abspath(str(Path('models') / 'Cloth_type.hdf5')))

    # Run the images through the CNN models to make predictions
    # fabric_predictions = [fabric.predict_classes(image_array) for image_array in image_arrays]
    pattern_predictions = [pattern.predict_classes(image_array) for image_array in image_arrays]
    type_predictions = [type_clothing.predict_classes(image_array) for image_array in image_arrays]

    # Link up predictions to the names of the predicted classes based on definitions from our trained model:
    # class_fabric = {
    # 0: 'Chiffon',
    # 1: 'Cotton',
    # 2: 'Denim',
    # 3: 'Lace',
    # 4: 'Leather',
    # 5: 'Linen',
    # 6: 'Ribbed',
    # 7: 'Spandex',
    # }

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
    4: 'Exercise shorts',
    5: 'Hoodie',
    6: 'Jeans',
    7: 'Romper',
    8: 'Shorts',
    9: 'Skirt',
    10: 'Tank',
    11: 'Tee'
    }

    # fabric_predictions = [class_fabric.get(prediction[0]) for prediction in fabric_predictions]
    fabric_predictions = [0 for prediction in pattern_predictions] # just fill it with empty 0s
    pattern_predictions = [class_pattern.get(prediction[0]) for prediction in pattern_predictions]
    type_predictions = [class_type.get(prediction[0]) for prediction in type_predictions]

    # getting our final dictionary of image_paths as keys and 3 predictions as a list as values
    path_pred = {img_path : [fabric_prediction, pattern_prediction, type_prediction] for img_path, fabric_prediction, pattern_prediction, type_prediction in zip(img_paths, fabric_predictions, pattern_predictions, type_predictions)}

    # appending a style to our prediction using helper function:
    for arr in path_pred.values():
        arr = get_style(arr)

    # appending n recommendations to our prediction using helper function
    for arr in path_pred.values():
        arr = get_recommendations(arr, 4)

    # clearing backend keras session after prediction was complete:
    K.clear_session()

    return path_pred


# testing function:
# -----------

# from pathlib import Path
# p = Path("static") / 'uploads'
# filepaths = [x for x in p.iterdir() if x.is_file()]

# print(predict_images(filepaths))
