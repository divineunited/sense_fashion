from flask import Flask, render_template, request
from flask import redirect, url_for
from flask import flash # for upload flash messages 
import os
import json
from werkzeug.utils import secure_filename

# from keras.models import load_model
# import tensorflow as tf
import numpy as np
from keras.preprocessing import image
from skimage import transform

# custom imports:


UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


app=Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    '''This function checks to make sure the uploaded image files have allowed filenames and extensions'''
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def image_orient(img_path):
    # Load the image from disk
    img = image.load_img(img_path)

    # Convert the image to a numpy array
    img = image.img_to_array(img)

    height = img.shape[0]
    width = img.shape[1]

    if height > width:
        # rotate it if it's a vertical image
        image_style = 'transform:rotate(90deg); width:325px;'
    else:
        # otherwise the image is landscape
        image_style = 'transform:rotate(0deg); width:525px;'

    return image_style

def image_preprocess(img_path):
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


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'pic' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['pic']
        # if user does not select file, browser also submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename) # always use that function to secure a filename before storing it directly on the filesystem.
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename)) # saving that file onto our server
            return redirect(url_for('result', filename=filename, _anchor='sense'))
    else:
        return render_template("index.html")


# if our index is a POST request, it will save the image, and then redirect to this page and serve up the image.
@app.route('/result/<filename>')
def result(filename):
    # send it as a proper JSON dumps string for the redirect routing so that it can be unpacked using a JSON loads:
    # predictions = json.dumps(predictions)
    # taking our passed json dump and loading it back out as a list to pass to our results template
    # predictions = json.loads(predictions)
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    # shape = image_orient(image_path)
    # print(shape)
    image_style = 'transform:rotate(90deg); width:325px;'
    image_style = 'transform:rotate(0deg); width:525px;'
    return render_template("result.html", image_path = "\\" + image_path, image_style = image_style)


if __name__ == "__main__":
    app.run(debug=True)