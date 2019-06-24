# -----------------------------
# *Tips on Running the App from your Local Server:*
# -----------------------------

# If you see this error with the AWS S3 - TypeError: expected string or bytes-like object - that means that you are not getting the Bucket and authentication passed to the upload function. So, you need to get the environment variables to be passed to it because our authentication and Bucket is located in our .env files. Make sure you have python-dotenv installed in your environment requirements. To get this uploading to AWS S3, you need to get the Bucket Variables from the .env file. In order to get those authentication variables, you'll need to have a virtual environment called venv set up and installed all the requirements.txt into that virtual environment. Then, you allow the bash to source that venv by typing this in the bash: *source venv/Scripts/activate*
# Afterwards, the .env is setup, and you can type "flask run" to start the server with the proper environment variables passed.

# -----------------------------
# *DOCKER DEPLOYMENT NOTE:*
# -----------------------------

# When creating the Docker Image for deployment, a new copy of this was built up from scratch with adjustments made on main.py


from flask import Flask, render_template, request
from flask import redirect, url_for, session
from flask_dropzone import Dropzone

### ML Model Loading
from keras.applications import vgg16
from keras.models import load_model
import tensorflow as tf

### COMMON IMPORTS:
import json
import os
from pathlib import Path
import datetime

### CUSTOM IMPORTS:
import custom_fashion
import custom_vgg
import custom_s3

### AWS:
from config import S3_BUCKET, S3_KEY, S3_SECRET
import boto3

# Instantiating the Flask App and setting a random key for the session module to function
app=Flask(__name__)
app.secret_key = "super secret key"
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['UPLOAD_FOLDER'] = Path('static') / 'uploads'

# Flask-Dropzone config:
app.config.update(
    DROPZONE_ALLOWED_FILE_TYPE='image',
    DROPZONE_MAX_FILE_SIZE=10,
    DROPZONE_MAX_FILES=300,
    # DROPZONE_UPLOAD_ON_CLICK=True,
    # DROPZONE_REDIRECT_VIEW = 'result',
)
# instantiating the dropzone backend 
dropzone = Dropzone(app)


###### Loading our Models:

#### Trying to load the VGG model beforehand works well in testing, but NOT deployed in production. After a couple days, running the VGG model gives us this error: tensorflow.python.framework.errors_impl.FailedPreconditionError: Attempting to use uninitialized value block1_conv1/kernel         [[{{node block1_conv1/kernel/read}}]]
    # It works well in testing though... Uncomment the code, send the model and graph through to the function to get it back online
# Load Keras' VGG16 model that was pre-trained against the ImageNet database
# model_vgg = vgg16.VGG16()
# creating a TF default graph that helps with threading issues: https://github.com/tensorflow/tensorflow/issues/14356#issuecomment-389606499
# graph = tf.get_default_graph()



# load our customized fashion pre-trained models -- preloading and sending 3 different models does not work in prototype
# fabric = load_model(os.path.abspath(str(Path('models') / 'vgg_weights_fabric.hdf5')))
# fabric._make_predict_function()
# graph_fab = tf.get_default_graph()

# pattern = load_model(os.path.abspath(str(Path('models') / 'vgg_weights_data_aug_frozen_pattern_EI')))
# pattern._make_predict_function()
# graph_pat = tf.get_default_graph()

# type_clothing = load_model(os.path.abspath(str(Path('models') / 'Cloth_type.hdf5')))
# type_clothing._make_predict_function()
# graph_typ = tf.get_default_graph()



@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        # clearing out local files from previous session
        custom_s3.wipe_folder(app.config['UPLOAD_FOLDER'])

        # create s3 upload directory based on datetime of pageload and passing it between flask pages via session module
        sdirectory = 'session_'
        sdirectory += datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S")
        session['sdirectory'] = sdirectory

        return render_template("index.html")



# api endpoint for uploading pictures
@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        
        # getting uploaded file and filename
        f = request.files.get('file')
        filename = f.filename

        # getting session directory:
        if 'sdirectory' in session: # getting s3 folder name
            sdirectory = session.get('sdirectory', None)
        else:
            sdirectory = '__undefined'
        
        # reorienting file if needed, and changing it to a PIL Image object
        f = custom_vgg.fix_orientation(f)
        
        # saving to local upload folder temporarilly:
        p = Path('static') / 'uploads' / sdirectory
        if p.is_dir() == False:
            p.mkdir(parents=True, exist_ok=True)
        filep = p / filename
        f.save(filep)
        
        # then uploading onto server using aws s3
        custom_s3.upload_file(os.path.abspath(str(filep)), S3_BUCKET, sdirectory + '/' + filename)
        
        return 'OK' # flask needs a return statement to be happy.



# api endpoint to see all files uploaded on s3
@app.route('/files')
def files():
    s3_resource = boto3.resource('s3')
    my_bucket = s3_resource.Bucket(S3_BUCKET)
    summaries = my_bucket.objects.all()

    return render_template('files.html', my_bucket=my_bucket, files=summaries)



# api endpoint to see results of GENERIC image recognition
@app.route('/result')
def result():
    
    # getting session directory:
    if 'sdirectory' in session: # getting s3 folder name
        sdirectory = session.get('sdirectory', None)
    else:
        sdirectory = '__undefined'
    
    # getting filepaths of our s3 bucket
    # s3 = boto3.resource('s3')
    # my_bucket = s3.Bucket(S3_BUCKET)
    # When a list of objects is retrieved from Amazon S3, they Key of the object is always its full path:
    # https://stackoverflow.com/questions/27292145/python-boto-list-contents-of-specific-dir-in-bucket
    # https://stackoverflow.com/questions/36205481/read-file-content-from-s3-bucket-with-boto3
    # s3filepaths = [obj.key for obj in my_bucket.objects.filter(Prefix = sdirectory + "/")]

    p = Path('static') / 'uploads' / sdirectory # the relative path of where our files are temp locally stored - defined as p
    filepaths = [x for x in p.iterdir() if x.is_file()] # getting filename paths
    
    paths_predictions = custom_vgg.predict_images(filepaths)

    return render_template("result.html", paths_predictions = paths_predictions)





# api endpoint to see results of SENSE FASHION image recognition
@app.route('/fashion')
def fashion():
    
    # getting session directory:
    if 'sdirectory' in session: # getting s3 folder name
        sdirectory = session.get('sdirectory', None)
    else:
        sdirectory = '__undefined'

    p = Path('static') / 'uploads' / sdirectory # the relative path of where our files are temp locally stored - defined as p
    filepaths = [x for x in p.iterdir() if x.is_file()] # getting filename paths
    
    # getting predictions. this part takes a while since I cannot figure out how to pass three models and three graphs without tensorflow flipping out on me...so - might want to build a progress bar:
        # progress bar: https://stackoverflow.com/questions/24251898/flask-app-update-progress-bar-while-function-runs
    paths_predictions = custom_fashion.predict_images(filepaths)

    return render_template("fashion.html", paths_predictions = paths_predictions)



if __name__ == "__main__":
    app.run(debug=True)