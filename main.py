from flask import Flask, render_template, request
from flask import redirect, url_for
from flask_dropzone import Dropzone

### COMMON IMPORTS:
import json
# import os
from pathlib import Path

### CUSTOM IMPORTS:
import custom_preprocess
import custom_w3

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

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
dropzone = Dropzone(app)


def allowed_file(filename):
    '''This function checks to make sure the uploaded image files have allowed filenames and extensions'''
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        f = request.files.get('file')
        filename = f.filename
        # reorienting file if needed, and changing it to a PIL Image object
        f = custom_preprocess.fix_orientation(f)
        # saving file onto server (or uploading to s3 - later) (using pathlib Path object)
        f.save(Path('static') / 'uploads' / filename)
        return 'OK' # flask needs a return statement to be happy.
    else:
        # clearing out the uploads folder everytime we load this page a new batch:
        custom_w3.wipe_folder(app.config['UPLOAD_FOLDER'])
        return render_template("index.html")


# if our index is a POST request, it will save the image, and then redirect to this page and serve up the image.
@app.route('/result')
def result():
    # dirname = os.path.dirname(os.path.abspath(__file__)) # getting the directory of this script
    # relpath = os.path.join(dirname, 'static', 'uploads') # adding the relative path of where our files are
    # backpaths = [] # getting array of filepaths for back-end processing
    # # preprocessing and image recognition
    # frontpaths = [url_for('static', filename=f'uploads/{f}') for f in os.listdir(relpath)] # getting array of filepaths for front-end display

    p = Path('static') / 'uploads'
    filenames = [x for x in p.iterdir() if x.is_file()]
    print(filenames)
    return render_template("result.html", filenames = filenames)


if __name__ == "__main__":
    app.run(debug=True)