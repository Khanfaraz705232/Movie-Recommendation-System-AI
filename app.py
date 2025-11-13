import streamlit as st 
import pickle
import pandas as pd
import requests
from urllib.parse import quote_plus

OMDB_API_KEY = "daf91aa9"
TMDB_API_KEY = "8265bd1679663a7ea12ac168da84d2e8"

@st.cache_data(show_spinner=False)
def fetch_poster_omdb(title):
    try:
        query = quote_plus(title.strip())
        url = f"http://www.omdbapi.com/?t={query}&apikey={OMDB_API_KEY}"
        response = requests.get(url, timeout=5)
        data = response.json()
        if data.get("Response") == "True" and data.get("Poster") != "N/A":
            return data.get("Poster"), data.get("Plot"), data.get("imdbRating")
    except:
        pass
    return None, None, None

@st.cache_data(show_spinner=False)
def fetch_poster_tmdb(title):
    try:
        query = quote_plus(title.strip())
        url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={query}"
        response = requests.get(url, timeout=5)
        data = response.json()
        if data.get("results"):
            poster_path = data["results"][0].get("poster_path")
            overview = data["results"][0].get("overview", "No plot available")
            rating = data["results"][0].get("vote_average", "N/A")
            if poster_path:
                return f"https://image.tmdb.org/t/p/w500{poster_path}", overview, rating
    except:
        pass
    return None, None, None

def fetch_poster(title):
    poster, plot, rating = fetch_poster_omdb(title)
    if not poster:
        poster, plot, rating = fetch_poster_tmdb(title)
    if not poster:
        poster = "https://via.placeholder.com/300x450?text=No+Image+Found"
        plot = "No plot available."
        rating = "N/A"
    return poster, plot, rating

def recommend(movie, num_recommendations):
    movie_index = moviess[moviess['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:num_recommendations + 1]
    recommended_movies, recommended_posters, plots, ratings = [], [], [], []
    for i in movies_list:
        title = moviess.iloc[i[0]].title
        poster, plot, rating = fetch_poster(title)
        recommended_movies.append(title)
        recommended_posters.append(poster)
        plots.append(plot)
        ratings.append(rating)
    return recommended_movies, recommended_posters, plots, ratings

moviess = pickle.load(open('movie_list.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

st.set_page_config(page_title="Movie Recommendation System", page_icon="🎬", layout="wide")

st.markdown("""
<style>
html, body, [class*="css"] {
    background-color: #000 !important;
    color: white !important;
    font-family: 'Helvetica Neue', Arial, sans-serif;
}
section.main > div {
    background-color: #000 !important;
}
[data-testid="stAppViewContainer"],
[data-testid="stHeader"],
[data-testid="stSidebar"],
[data-testid="stToolbar"],
[data-testid="stSidebarNav"] {
    background-color: #000 !important;
    color: white !important;
}
.header {
    display: flex; align-items: center; justify-content: center;
    background-color: #000;
    padding: 15px 30px;
    box-shadow: 0 2px 10px rgba(255,255,255,0.1);
}
.header h1 {
    font-weight: 800; color: white; font-size: 2rem; margin: 0;
}
.search-section { padding: 10px 30px; margin-bottom: 10px; color: white; }
.stSelectbox label, .stSlider label, .stTextInput label {
    color: white !important;
    font-weight: 600;
}
.stButton>button {
    width: 80%; background-color: #222; color: white;
    border: none; font-weight: bold; border-radius: 5px;
    padding: 8px 0; cursor: pointer; transition: 0.2s;
    display: block; margin: 0 auto;
}
.stButton>button:hover { background-color: #444; transform: scale(1.03); }
div[data-testid="stSelectbox"] {
    display: flex;
    justify-content: center;
}
/* Add horizontal spacing between label and selectbox */
div[data-testid="stSelectbox"] > label {
    margin-right: 10px;  /* space between "🔍 Search for a movie:" and selectbox */
}
div[data-testid="stSelectbox"] > div {
    width: 80% !important;
}
div[data-baseweb="select"] > div {
    background-color: #111 !important;
    color: white !important;
    border-radius: 8px;
    border: 1px solid #333;
}
/* Make typed text in the selectbox white */
div[data-baseweb="select"] input {
    color: white !important;
}
.hero {
    position: relative; height: 60vh; width: 100%;
    background-size: cover; background-position: center;
    box-shadow: inset 0 0 150px rgba(0,0,0,0.8);
    margin: 20px auto; border-radius: 10px;
}
.hero-content { position: absolute; bottom: 20px; left: 30px; max-width: 50%; }
.hero h1 { font-size: 2.5rem; font-weight: 800; color: white; }
.hero p { font-size: 1rem; color: #ccc; margin-top: 5px; }
.hero .info { font-size: 0.85rem; color: #aaa; }
.section-title {
    font-size: 1.3rem; font-weight: 700; margin: 20px 30px 15px; color: white;
}
.movie-card {
    background: #111; border-radius: 10px;
    overflow: hidden; text-align: center;
    transition: transform 0.3s; margin-bottom: 15px;
}
.movie-card:hover { transform: scale(1.05); }
.movie-card img { width: 100%; height: 280px; object-fit: cover; }
.movie-info { padding: 8px; }
.movie-info h3 { margin: 8px 0 4px; font-size: 0.95rem; color: white; }
.movie-info p { color: #ccc; font-size: 0.8rem; height: 35px; overflow: hidden; }
.movie-info .rating { color: white; font-weight: bold; }
hr { border: 0; border-top: 1px solid rgba(255,255,255,0.1); }
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='header'><h1>🎬 Movie Recommendation System</h1></div>", unsafe_allow_html=True)

st.markdown(f"""
<div class="hero" style="background-image:url('https://image.slidesdocs.com/responsive-images/background/black-black-screen-with-movie-reel-powerpoint-background_1522b0f64b__960_540.jpg');">
    <div class="hero-content">
        <h1>Featured Movie</h1>
        <div class="info">⭐ IMDb N/A | Featured</div>
        <p>Explore top movie recommendations based on your favorite films. Discover new movies and expand your watchlist!</p>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div class='search-section'>", unsafe_allow_html=True)
selected_movie_name = st.selectbox("🔍 Search for a movie:", moviess['title'].values, key="movie_search")
num_recommendations = st.slider("🎯 # of Recommendations", 5, 15, 5, key="slider_num")
recommend_button = st.button("🎬 Recommend", use_container_width=False)
st.markdown("</div>", unsafe_allow_html=True)

if recommend_button:
    with st.spinner("✨ Fetching your movie recommendations..."):
        names, posters, plots, ratings = recommend(selected_movie_name, num_recommendations)
        st.markdown(f"<div class='section-title'>Because you watched <span style='color:white'>{selected_movie_name}</span>...</div>", unsafe_allow_html=True)
        for i in range(0, len(names), 5):
            row_cols = st.columns(5)
            for j, col in enumerate(row_cols):
                if i + j < len(names):
                    col.markdown(f"""
                        <div class='movie-card'>
                            <img src='{posters[i+j]}' alt='{names[i+j]}'/>
                            <div class='movie-info'>
                                <h3>{names[i+j]}</h3>
                                <p>{plots[i+j][:100]}...</p>
                                <div class='rating'>⭐ {ratings[i+j]}</div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
