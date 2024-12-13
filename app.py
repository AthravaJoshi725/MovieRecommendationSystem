import streamlit as st
import pickle
import requests
import pandas as pd

# Load data and similarity matrix
try:
    similarity = pickle.load(open('similarity.pkl', 'rb'))
    movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
    movies = pd.DataFrame(movies_dict)
except FileNotFoundError as e:
    st.error("Required data files not found. Please ensure 'similarity.pkl' and 'movies_dict.pkl' are available.")
    st.stop()

def get_poster(id):
    """Fetches the poster for a movie using TMDb API."""
    url = f"https://api.themoviedb.org/3/movie/{id}/images"
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJlNmViMGMwNTAxOGZhY2FhZGM0MWJkMjNiZTEyYzA5OCIsIm5iZiI6MTczNDA2NDg0MS44OTUsInN1YiI6IjY3NWJiYWM5MTZlOTYzZGRhZjBkZDYyMSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.HLrnRx8-HV3PO3tKPSMPtg-2eVFcvWBjctnEOrEsBn8"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        # Handle missing poster gracefully
        if not data.get('posters'):
            return "https://via.placeholder.com/220x330?text=No+Image+Available"

        return 'https://media.themoviedb.org/t/p/w220_and_h330_face/' + data['posters'][0]['file_path']
    except Exception as e:
        st.warning(f"Error fetching poster: {e}")
        return "https://via.placeholder.com/220x330?text=No+Image+Available"

def recommend(movie):
    """Fetches recommended movies and their posters."""
    if movie not in movies['title'].values:
        st.error(f"Movie '{movie}' not found in the dataset.")
        return [], []

    try:
        movie_index = movies[movies['title'] == movie].index[0]
        distances = similarity[movie_index]
        movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

        recom_movies = []
        recom_movies_poster = []

        for i in movies_list:
            id = movies.iloc[i[0]]['id']  
            recom_movies.append(movies.iloc[i[0]]['title'])
            recom_movies_poster.append(get_poster(id))

        return recom_movies, recom_movies_poster
    except Exception as e:
        st.error(f"Error during recommendation: {e}")
        return [], []

# Streamlit app layout
st.title('Movie Recommender System')

sel_movie = st.selectbox(
    'Select a movie',
    movies['title'].values
)

if st.button('Recommend'):
    names, posters = recommend(sel_movie)

    if names and posters:
        cols = st.columns(5)

        for i, col in enumerate(cols):
            if i < len(names):
                with col:
                    st.text(names[i])
                    st.image(posters[i])
            else:
                with col:
                    st.empty()
    else:
        st.info("No recommendations to display.")
