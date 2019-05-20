from flask import Flask, render_template, request
from flask import redirect, url_for, jsonify
import pandas as pd
import numpy as np
import os
from google.cloud import bigquery
import json

# custom imports:

app=Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True



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


@app.route('/index')
@app.route('/')
def index():
    return render_template("index.html")


# when the form press submit, it links it to the redirect which will be sent here and then passes the prediction variable to the results page after back-end recommendation logic completed:
@app.route('/myredirect', methods = ['POST'])
def my_redirect():
    global data
    global movie_dict
    if request.method == 'POST':
        # from the request form, convert it to a dictionary saved as this variable
        _features = request.form.to_dict()

        ### converting inputs to their correct value types:
        _features['movie_1'] = int(_features['movie_1'])
        _features['movie_2'] = int(_features['movie_2'])
        _features['movie_3'] = int(_features['movie_3'])
        _features['movie_4'] = int(_features['movie_4'])

        # get the values and turn it into a list
        _features=list(_features.values())

        # get our recommendation movie_ids:
        movie_ids = recommend_engine.your_item_to_item_recommendations(_features, data)

        # convert them to movie titles:
        predictions = [movie_dict[id] for id in movie_ids]

        # send it as a proper JSON dumps string for the redirect routing so that it can be unpacked using a JSON loads:
        predictions = json.dumps(predictions)

        # passing our predictions JSON dump and an achor to the result url.
        return redirect(url_for('result', predictions = predictions, _anchor='services'))



# Wanted to redirect so that it can pass the anchor of where I want to land in the results page (services subsection of page).
# Thank you to this code to help pass the redirect variable to this result route: 
# https://stackoverflow.com/questions/26954122/how-can-i-pass-arguments-into-redirecturl-for-of-flask
@app.route('/result/<predictions>')
def result(predictions):

    # taking our passed json dump and loading it back out as a list to pass to our results template
    predictions = json.loads(predictions)

    return render_template("result.html", predictions = predictions)

if __name__ == "__main__":
    app.run(debug=True)