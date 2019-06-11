from flask import Flask, render_template, request
from flask import redirect, url_for
from flask_dropzone import Dropzone

### COMMON IMPORTS:
import json
import os
from pathlib import Path
import datetime

### CUSTOM IMPORTS:
import custom_image
import custom_s3

### AWS:
from config import S3_BUCKET, S3_KEY, S3_SECRET
import boto3

# # create s3 client
# s3_resource = boto3.resource(
#    "s3",
#    aws_access_key_id=S3_KEY,
#    aws_secret_access_key=S3_SECRET
# )

# Instantiating the Flask App
app=Flask(__name__)
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
        # global variable for w3 upload directory
        w3directory = 'session_'
        w3directory += datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        return render_template("index.html")


# api endpoint for uploading pictures
@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        f = request.files.get('file')
        filename = f.filename
        
        # reorienting file if needed, and changing it to a PIL Image object - which then gets sent back as bytestream
        f = custom_image.fix_orientation(f)
        
        # saving to local upload folder temporarilly:
        localpath = Path('static') / 'uploads' / filename
        f.save(localpath)
        
        # then uploading onto server using aws s3
        w3directory = 'session_'
        custom_s3.upload_file(os.path.abspath(str(localpath)), S3_BUCKET, w3directory + '/' + filename)

        # deleting local version
        custom_s3.wipe_folder(app.config['UPLOAD_FOLDER']) 
        
        return 'OK' # flask needs a return statement to be happy.




# api endpoint to see files uploaded on s3
@app.route('/files')
def files():
    s3_resource = boto3.resource('s3')
    my_bucket = s3_resource.Bucket(S3_BUCKET)
    summaries = my_bucket.objects.all()

    return render_template('files.html', my_bucket=my_bucket, files=summaries)




# if our index is a POST request, it will save the image, and then redirect to this page and serve up the image.
@app.route('/result')
def result():
    p = Path('static') / 'uploads' # the relative path of where our files are - defined as p
    filepaths = [x for x in p.iterdir() if x.is_file()] # getting filename paths
    
    # getting predictions. this part takes a while - might want to build a progress bar:
        # progress bar: https://stackoverflow.com/questions/24251898/flask-app-update-progress-bar-while-function-runs
    paths_predictions = custom_image.predict_images(filepaths) 

    return render_template("result.html", paths_predictions = paths_predictions)




if __name__ == "__main__":
    app.run(debug=True)