import pandas as pd
import numpy as np
import ast        # Safely converts strings of list/dict-like data (e.g., JSON) into Python objects.
import nltk       # Natural Language Toolkit used here for stemming (reducing words to their base form)
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle     # For saving trained models/data structures to disk.
from nltk.stem.porter import PorterStemmer   # Used to reduce words to their root (e.g., running → run).
Ps = PorterStemmer()     # Initialize the Porter Stemmer for text normalization

CV = CountVectorizer(max_features = 5000,stop_words =  'english')




movies = pd.read_csv('tmdb_5000_movies.csv')
credits = pd.read_csv('tmdb_5000_credits.csv')

# Merge the movies and credits datasets on the 'title' column
movies = movies.merge(credits, on='title')

movies = movies[['movie_id', 'title', 'overview', 'genres', 'keywords', 'cast', 'crew']]

movies.dropna(inplace=  True)
# print(movies.isnull().sum())
# print(movies.duplicated().sum())
# print(movies.iloc[0].genres)

def convert(obj):       # Converts a stringified list of dictionaries to an actual list of genre/keyword names.
    L=[]
    for i in ast.literal_eval(obj):
        L.append(i['name'])
    return L

#  Cast
def convertCast(obj):            # Extracts the names of the top 3 actors from the cast.
    L=[]
    counter = 0
    for i in ast.literal_eval(obj):
        if counter < 3:
            L.append(i['name'])
            counter += 1
        else:
            break
    return L


def FetchCrew(obj):         # Extracts the name of the director from the crew list
    L=[]
    for i in ast.literal_eval(obj):
        if i['job'] == 'Director':
            L.append(i['name'])
            break
    return L


def stem(text):         # Applies Porter stemming to each word in the text.
    y=[]
    for i in text.split():
        y.append(Ps.stem(i))
        
    return " ".join(y)

                             # Apply helper functions to parse stringified JSON data and convert it to list of relevant names.
movies["genres"] = movies['genres'].apply(convert)
movies['keywords'] = movies['keywords'].apply(convert)
movies['cast'] = movies['cast'].apply(convertCast)
movies['crew'] = movies['crew'].apply(FetchCrew)
movies['overview'] = movies['overview'].apply(lambda x: x.split())       # Split overview text into list of words.

                             # Remove spaces from genre, keyword, cast, and crew lists.
                             #  Remove spaces in multi-word names (e.g., "Science Fiction" → "ScienceFiction") to treat them as single tokens.
movies["genres"] = movies['genres'].apply(lambda x: [i.replace(" ", "") for i in x])
movies['keywords'] = movies['keywords'].apply(lambda x: [i.replace(" ", "") for i in x])
movies['cast'] = movies['cast'].apply(lambda x: [i.replace(" ", "") for i in x])
movies['crew'] = movies['crew'].apply(lambda x: [i.replace(" ", "") for i in x])

# Combine all relevant text fields into a single 'tags' field for each movie
movies['tags'] = movies['overview'] + movies['genres'] + movies['keywords'] + movies['cast'] + movies['crew']


movies_df = movies[['movie_id', 'title', 'tags' ]]

# ...existing code...

# Use .loc to avoid SettingWithCopyWarning
movies_df.loc[:, 'tags'] = movies_df['tags'].apply(lambda x: " ".join(x))
movies_df.loc[:, 'tags'] = movies_df['tags'].apply(lambda x: x.lower())

vectors = CV.fit_transform(movies_df['tags']).toarray()   

movies_df.loc[:, 'tags'] = movies_df['tags'].apply(stem)       # Apply stemming to the 'tags' field to reduce words to their root form.

similarity = cosine_similarity(vectors)

def recommendations(movie):
    # Find the index of the movie title
    if movie not in movies_df['title'].values:
        print(f"Movie '{movie}' not found in database.")
        return
    movie_index = movies_df[movies_df['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    for i in movies_list:
        print(movies_df.iloc[i[0]].title)

recommendations("Spider-Man")

# pickle.dump(movies_df, open('movies.pkl', 'wb'))
# pickle.dump(similarity, open('similarity.pkl', 'wb'))
