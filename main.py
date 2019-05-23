from flask import Flask, render_template, request
from flask import redirect, url_for
from flask import flash # for upload flash messages 
from werkzeug.utils import secure_filename # for flask uploads

### COMMON IMPORTS:
import os
import json
import io

### IMPORTS FOR WORKING WITH IMAGES
from PIL import Image, ExifTags

### IMPORTS FOR CNN IMAGE PREPROCESSING
# from keras.models import load_model
# import tensorflow as tf
import numpy as np
from keras.preprocessing import image
from skimage import transform

### CUSTOM IMPORTS:


UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


app=Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    '''This function checks to make sure the uploaded image files have allowed filenames and extensions'''
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def fix_orientation(file_like_object):
    '''Accepts an image file object and checks for ExifTags to reorient smart phone taken images if needed'''
    
    # load image from disk temporarilly - will update to pass a File Object through this:
    img = Image.open(file_like_object)
    print(img.size) # flag to see initial dimensions
    
    if hasattr(img, '_getexif'):
        exifdata = img._getexif()
        try:
            orientation = exifdata.get(274)
            print('has orientation')
            print(orientation)
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
        
    print(img.size) # flag to see updated dimensions

    # sending the data file object back
    data = io.BytesIO() 
    # saving the image as a data stream to pass
    img.save(data) 
    return data




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




@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'pic' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        fi = request.files['pic'] # Alternate Syntax: # fi = request.files.get("file")
        
        # if user does not select file, browser also submits an empty part without filename
        if fi.filename == '':
            flash('No selected file')
            return redirect(request.url)

        # Checking to make sure it's an allowed filename
        if fi and allowed_file(fi.filename):
            # getting a secure filename before saving it on our server (using werzkeug.utils.secure_filename)
            filename = secure_filename(fi.filename)
            # reorienting file if needed, and changing it to a BytesIO data stream now.
            fi = fix_orientation(fi)
            # saving file onto server (or uploading to s3)
                # If it wasn't converted to BytesIO, can use this method --> # fi.save(os.path.join(app.config['UPLOAD_FOLDER'], filename)) 
            with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), "wb") as f:
                f.write(fi.getvalue())

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
    return render_template("result.html", image_path = "\\" + image_path)


if __name__ == "__main__":
    app.run(debug=True)