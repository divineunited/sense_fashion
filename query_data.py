import os
from google.cloud import bigquery

# # Perform a query for 10 random movies:
# # SOURCE: https://stackoverflow.com/questions/23375456/random-sampling-in-google-bigquery
# my_query = '''
# SELECT movie_id, movie_title, rand() as rand
# FROM `classicmovies.classicmovies.movies` 
# ORDER BY rand
# LIMIT 10;
# '''

# GET MOVIE DATA:
def get_movie(client):
    '''This function requires an authenticated google bigquery client and returns an array of hashtables with year, (genre), movie_ids, and movie_titles as keys and their corresponding values from Google Big Query. It also returns a dictionary of movie_ids as keys and movie_titles as values'''

    # get the GENRE later - need to unpivot first
    # source: unpivot of genre columns: https://stackoverflow.com/questions/16784999/sql-get-column-names-when-value-is-1
    movie_query = 'SELECT movie_id, movie_title, EXTRACT(YEAR FROM release_date) as year FROM `classicmovies.classicmovies.movies` ORDER BY YEAR ASC'
    QUERY = (movie_query)
    query_job = client.query(QUERY)  # API request
    rows = query_job.result()  # Waits for query to finish

    array = []
    movies = {}

    for row in rows:
        movie_dict = {}
        movie_dict['movie_id'] = row.movie_id
        movie_dict['movie_title'] = row.movie_title
        movie_dict['movie_year'] = row.year
        array.append(movie_dict)
        movies[row.movie_id] = row.movie_title

    # now, you can take each of these dictionaries in this array, and convert it to JSON using json.dumps(dict) and display in dropdown - that's for later when we want to filter our results for the user. Now, we create drop down of ALL movies using the dictionary mocies.
    return array, movies


# GET TRANSACTION DATA:
def get_data(client):
    '''This function requires an authenticated google bigquery client and returns a Pandas dataframe of transactions.'''

    # get the GENRE later - need to unpivot first
    # source: unpivot of genre columns: https://stackoverflow.com/questions/16784999/sql-get-column-names-when-value-is-1
    my_query = 'SELECT user_id, movie_id, rating FROM `classicmovies.classicmovies.transactions`'
    QUERY = (my_query)
    query_job = client.query(QUERY)  # API request
    rows = query_job.result()  # Waits for query to finish

    
    # now, you can take each of these dictionaries in this array, and convert it to JSON using json.dumps(dict)
    return rows.to_dataframe()


### AUTHENTIFICATION:
path = os.getcwd()
path += '\classicmovies-5e206ef6ea35.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = path
client = bigquery.Client()

# print(get_movie(client))
# print(get_data(client).head())