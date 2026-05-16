import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

movies = pd.read_csv("movies.csv")
movies["genres"] = movies["genres"].str.replace("|", " ") # data cleaning for tf-idf (genre vectorization). Since the vertical bar interferes with this process, we replace it with a blank space.
movies["clean_titles"] = movies["title"].str[:-7].str.lower().str.strip()

tfidf = TfidfVectorizer()
tfidf_matrix = tfidf.fit_transform(movies["genres"]) # aforementioned vectorization
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix) # computing similarity with cosine similarity (comparing each movie to each other movie)
# ------MATHEMATICAL EXPLANATION------
# tf = frequency of a term in a document (in this case, # of times a genre appears in the genre list for each movie)
# idf = log(# of documents / # of documents containing the term). genres that appear less frequently across all movies have a higher idf value (or higher importance), thus contributing more to the tf-idf score
# multiply tf by idf for the tf-idf score

# next, cosine similarity is the product of the two vectors (for this project, the genre vectors for each movie) and dividing them by the product of their absolute values.
# this will return a value between 0 and 1, where 0 is absolutely no similarity and 1 is identical.

idx = pd.Series(movies.index, index = movies["clean_titles"]).drop_duplicates() # Creates a series that replaces the default integer index (0, 1, 2, etc). with the title of the movie. Allows for easy movie indexing when recommending. Drop duplicates to prevent bugs that could potentially arise from movies w/ same/similar titles.

# Recommendation function. Input a movie title and return 5 similar movies based on genre similarity.
def recommend(movie_title, cosine_sim = cosine_sim) :
    index = idx[movie_title] # integer index of movie that matches the title
    sim_scores = list(enumerate(cosine_sim[index])) # creates a tuple list (movie_index, sim_score) for the input movie as well as all other movies
    sim_scores = sorted(sim_scores, key = lambda x: x[1], reverse = True) # sorts the aforementioned list  in descending order
    sim_scores = sim_scores[1:6] # first 5 movies based on similarity (skipping the first as it is the input movie itself)
    movie_idx = [i[0] for i in sim_scores] # integer index of each of the 5 recommended movies (integer so the iloc function works)
    return movies["title"].iloc[movie_idx] # Title of the 5 recommended movies

movie_title = input("Enter a movie title to get 5 similar movies based on genre similarity: ")
movie_title = movie_title.strip().lower()

if movie_title in movies["clean_titles"].values :
    print("I recommend the following movies: ")
    print(recommend(movie_title))
else :
    print("Invalid movie title, please try again.")