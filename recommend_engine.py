import pandas as pd
import numpy as np
from scipy.spatial.distance import hamming 

##--------HELPER FUNCTION: FIND NEAREST ITEM NEIGHBOURS

def nearestneighbours(movie_id, k, userItemRatingMatrix, distance_measure = hamming):
    '''This helper function finds the K nearest neighbor item to a specific user's item using a selected distance measure.''' 

    # create a movie df that contains all movies except the selected movie input
    allMovies = pd.DataFrame(userItemRatingMatrix.index)
    # allMovies = allMovies[allMovies.movie_id != movie_id]
    
    # Add a column to this df which contains distance of active movie to each and every movie
    allMovies["distance"] = allMovies["movie_id"].apply(lambda x: distance_measure(userItemRatingMatrix.loc[movie_id], userItemRatingMatrix.loc[x]))
    
    # sort the values of all movies based on the distance metric
    sortedMovies = allMovies.sort_values(["distance"],ascending=True)["movie_id"][:k]
    return list(sortedMovies)


####------MAIN FUNCTION TO GET RANKED RECOMMENDATIONS

def your_item_to_item_recommendations(movie_ids, data):
    '''This function requires the user to input a list of 4 favourite movie ids. It makes use of the helper function nearestneighbours that finds the K nearest neighbor items of each movie. These items are added to a recommendation list and a ranked recommendation list is returned''' 

    # We create userItemRatingMatrixforItem where index is movie_id 
    userItemRatingMatrix = pd.pivot_table(data, values='rating',
                                    index=['movie_id'], columns=['user_id'])
    
    # Loop through my favourites list and use movie_id as inputs into nearestneighbours function. 
    # Create empty list of recommendation
    # Append the function's output (sortedMovies) to the recommendations list

    recommendations= []
    for movie_id in movie_ids:
        sortedMovies = nearestneighbours(movie_id, 10, userItemRatingMatrix, distance_measure = hamming) 
        recommendations += sortedMovies
    
    # we want to sort according to the movies that appeared in all 4 recommendation list
    recommendations=sorted(recommendations, key=recommendations.count, reverse=True)

    # removing duplicates:
    recommendations = list(dict.fromkeys(recommendations))

    return recommendations