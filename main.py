from flask import Flask, render_template, request
from flask import redirect, url_for
from flask import flash # for upload flash messages 
from werkzeug.utils import secure_filename # for flask uploads

### COMMON IMPORTS:
import json
import os

### CUSTOM IMPORTS:
import custom_preprocess
import custom_w3

UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


app=Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    '''This function checks to make sure the uploaded image files have allowed filenames and extensions'''
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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
            # reorienting file if needed, and changing it to a PIL Image object
            fi = custom_preprocess.fix_orientation(fi)
            # clearing out the uploads folder before saving this one:
            custom_w3.wipe_folder(os.path.join(app.config['UPLOAD_FOLDER']))
            # saving file onto server (or uploading to s3 - later)
            fi.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                # If it was converted to a io.BytesIO() data stream:
                # with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), "wb") as f:
                #     f.write(fi.getvalue())
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
    return render_template("result.html", image_path = "\\" + image_path)


if __name__ == "__main__":
    app.run(debug=True)