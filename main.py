from flask import Flask, render_template, request
from flask import redirect, url_for, session
from flask_dropzone import Dropzone

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
    
    # getting predictions. this part takes a while - might want to build a progress bar:
        # progress bar: https://stackoverflow.com/questions/24251898/flask-app-update-progress-bar-while-function-runs
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
    
    # getting filepaths of our s3 bucket
    # s3 = boto3.resource('s3')
    # my_bucket = s3.Bucket(S3_BUCKET)
    # When a list of objects is retrieved from Amazon S3, they Key of the object is always its full path:
    # https://stackoverflow.com/questions/27292145/python-boto-list-contents-of-specific-dir-in-bucket
    # https://stackoverflow.com/questions/36205481/read-file-content-from-s3-bucket-with-boto3
    # s3filepaths = [obj.key for obj in my_bucket.objects.filter(Prefix = sdirectory + "/")]

    p = Path('static') / 'uploads' / sdirectory # the relative path of where our files are temp locally stored - defined as p
    filepaths = [x for x in p.iterdir() if x.is_file()] # getting filename paths
    
    # getting predictions. this part takes a while - might want to build a progress bar:
        # progress bar: https://stackoverflow.com/questions/24251898/flask-app-update-progress-bar-while-function-runs
    paths_predictions = custom_fashion.predict_images(filepaths)

    return render_template("fashion.html", paths_predictions = paths_predictions)



if __name__ == "__main__":
    app.run(debug=True)