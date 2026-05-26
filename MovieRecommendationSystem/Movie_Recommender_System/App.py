import streamlit as st
import pickle
import pandas as pd
import requests

movies_dict = pickle.load(open('movies.pkl','rb'))
movies = pd.DataFrame(movies_dict)

similarity = pickle.load(open('similarity.pkl','rb'))

def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    recommended = []
    recommended_poster = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended.append(movies.iloc[i[0]].title)
        recommended_poster.append(fetch_poster(movie_id))
    return recommended, recommended_poster

def fetch_poster(movie_id):
    response = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=89ab46c169eb38bcda724408879d6dde&language=en-US')
    data = response.json()
    return "https://image.tmdb.org/t/p/w500/" + data['poster_path']


st.title('Movie Recommender System')

option = st.selectbox(
    "Search",
    movies['title'].values
)

if st.button('Search'):
    names, posters = recommend(option)

    st.write("### Recommended Movies:")

    cols = st.columns(5)

    for i in range(5):
        with cols[i]:
            st.image(posters[i], caption=names[i], use_container_width=True)
