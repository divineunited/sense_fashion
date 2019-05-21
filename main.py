from flask import Flask, render_template, request
from flask import redirect, url_for, jsonify
from flask import flash
from flask import send_from_directory
import pandas as pd
import numpy as np
import os
# from google.cloud import bigquery
import json
from werkzeug.utils import secure_filename

# custom imports:


UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app=Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# #### QUERY OUR TRANSACTION AND MOVIE DATA FROM GOOGLE BIG QUERY:
# # AUTHENTIFICATION:
# path = os.getcwd()
# path += '\classicmovies-5e206ef6ea35.json'
# os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = path
# client = bigquery.Client()

# # GET DATA
# movie_dicts, movie_dict = query_data.get_movie(client) # movie_dicts is an array of dictionaries for a JSON table (next level filtering of movies). movie_dict is just a dictionary of movie_ids as keys and movie_titles as corresponding values.
# # SOURCE for Dropdown Creation:
# # https://stackoverflow.com/questions/45877080/how-to-create-dropdown-menu-from-python-list-using-flask-and-html
# # NEXT LEVEL:
# # https://stackoverflow.com/questions/44646925/flask-dynamic-dependent-dropdown-list
# # ACCESSING DICTIONARY IN JINJA:
# # https://stackoverflow.com/questions/24727977/get-nested-dict-items-using-jinja2-in-flask
# data = query_data.get_data(client) # dataframe of transaction data for our recommendation systems


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
    # return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    # send it as a proper JSON dumps string for the redirect routing so that it can be unpacked using a JSON loads:
    # predictions = json.dumps(predictions)
    # taking our passed json dump and loading it back out as a list to pass to our results template
    # predictions = json.loads(predictions)
    image_path = "\\" + os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return render_template("result.html", image_path = image_path)


if __name__ == "__main__":
    app.run(debug=True)