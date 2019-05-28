from flask import Flask, render_template, request
from flask import redirect, url_for
from flask_dropzone import Dropzone

### COMMON IMPORTS:
import json
from pathlib import Path

### CUSTOM IMPORTS:
import custom_image
import custom_w3


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
def upload():
    if request.method == 'POST':
        f = request.files.get('file')
        filename = f.filename
        # reorienting file if needed, and changing it to a PIL Image object
        f = custom_image.fix_orientation(f)
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
    p = Path('static') / 'uploads' # the relative path of where our files are - defined as p
    filepaths = [x for x in p.iterdir() if x.is_file()] # getting filename paths
    
    # getting predictions. this part takes a while - might want to build a progress bar:
        # progress bar: https://stackoverflow.com/questions/24251898/flask-app-update-progress-bar-while-function-runs
    paths_predictions = custom_image.predict_images(filepaths) 

    return render_template("result.html", paths_predictions = paths_predictions)



if __name__ == "__main__":
    app.run(debug=True)