import streamlit as st
import pickle
import pandas as pd
from itertools import chain
import os

# -----------------------
# Page config
# -----------------------
st.set_page_config(layout="wide")

# -----------------------
# Session state
# -----------------------
if "selected_movie" not in st.session_state:
    st.session_state.selected_movie = "-- Select a movie --"

if "page" not in st.session_state:
    st.session_state.page = 0

if "entered_app" not in st.session_state:
    st.session_state.entered_app = False



# -----------------------
# Landing Page
# -----------------------

# -----------------------
# Landing Page
# -----------------------
if not st.session_state.entered_app:

    # Landing Page Description + Images
    st.markdown(
        """
        <h1 style='text-align:center; font-size:48px;'>🎬 Movie Recommendation System</h1>

        <p style='text-align:center; font-size:20px; margin-top:-10px;'>
            A personalized movie discovery engine powered by <b>Content-Based Filtering</b>
        </p>

        <br>

        <h2 style='font-size:30px;'>📌 What is a Recommendation System?</h2>

        <p style='font-size:18px; line-height:1.6;'>
            A recommendation system is an intelligent algorithm that suggests items a user is likely to enjoy —
            such as movies, music, products, or restaurants. It enhances user experience by reducing
            search effort and delivering personalized content.
        </p>

        <br>

        <h2 style='font-size:26px;'>🧠 Types of Recommendation Systems</h2>

        <h3 style='font-size:22px;'>Content-Based Filtering</h3>
        <p style='font-size:18px; line-height:1.6;'>
            Recommends movies based on their attributes — genre, cast, director, and storyline.
            <br><b>Example:</b> If you enjoy Sci-Fi films starring Tom Cruise, similar movies are recommended.
        </p>

        <div style='text-align:left;'>
            <img src='https://www.stratascratch.com/_next/image?url=https%3A%2F%2Fcdn.sanity.io%2Fimages%2Foaglaatp%2Fproduction%2Fa2fc251dcb1ad9ce9b8a82b182c6186d5caba036-1200x800.png&w=3840&q=75' 
                style='width:55%; border-radius:10px; margin: 15px 0;'>
        </div>

        <h3 style='font-size:22px;margin-top:35px;'>Collaborative Filtering</h3>
        <p style='font-size:18px; line-height:1.6;'>
            Recommends movies based on what similar users enjoyed.
            <br><b>Example:</b> "Users similar to you enjoyed these movies."
        </p>

        <div style='text-align:left;'>
            <img src='https://i0.wp.com/spotintelligence.com/wp-content/uploads/2024/04/user-based-collaborative-filtering.jpg?resize=1024%2C576&ssl=1' 
                style='width:55%; border-radius:10px; margin: 15px 0;'>
        </div>

        <br>

        <h2 style='font-size:26px;'>🔧 How This Project Works</h2>

        <p style='font-size:18px; line-height:1.6;'>
            This project uses <b>Content-Based Filtering</b> and follows these steps:
            <ul style='font-size:18px; line-height:1.7;'>
                <li><b>Dataset Preparation:</b> Movie metadata (movie overview, cast, director, genres, production companies).</li>
                <li><b>Preprocessing:</b> Cleaning & normalizing text.</li>
                <li><b>Feature Engineering:</b> TF-IDF vectorization across 5 text fields.</li>
                <li><b>Similarity:</b> Cosine similarity for movie-to-movie matching.</li>
                <li><b>Frontend:</b> Streamlit UI with search, filters, posters & details.</li>
            </ul>
        </p>

        <br><br>
        """,
        unsafe_allow_html=True
    )

    # Center Explore Button (Bigger + Styled)
    button_style = """
    <style>
    .center-btn-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-top: 20px;
    }
    
    div.stButton > button {
        font-size: 24px !important;
        padding: 15px 35px !important;
        border-radius: 10px !important;
        background-color: #ff4b4b !important;
        color: white !important;
        font-weight: 600 !important;
        border: none !important;
    }
    
    div.stButton > button:hover {
        background-color: #ff1f1f !important;
    }
    </style>
    """
    st.markdown(button_style, unsafe_allow_html=True)
    
    st.markdown("<div class='center-btn-container'>", unsafe_allow_html=True)
    
    if st.button("🎥 Explore Recommendations", key="enter_btn"):
        st.session_state.entered_app = True
        st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

    st.stop()
# -----------------------
# Load data
# -----------------------

movies = pickle.load(open('movies.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

st.markdown(
    """
    <h1 style='text-align: center;'>🎬 Movie Recommender</h1>
    """,
    unsafe_allow_html=True
)

# -----------------------
# Helper functions
# -----------------------
def recommend(movie):
    index = movies[movies['title'] == movie].index

    if len(index) == 0:
        return []

    index = index[0]
    distances = similarity[index]

    movies_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:11]

    return [movies.iloc[i[0]].title for i in movies_list]


def format_title(title, max_len=20):
    return title if len(title) <= max_len else title[:18] + "..."


def split_column(col):
    return col.fillna("").apply(lambda x: [i.strip() for i in x.split(",")])


def get_unique(col):
    return sorted(set(chain.from_iterable(movies[col])) - {''})


# -----------------------
# Preprocess filter columns
# -----------------------
movies['genres_list'] = split_column(movies['genres'])
movies['cast_list'] = split_column(movies['cast'])
movies['production_list'] = split_column(movies['production_companies'])
movies['director_list'] = split_column(movies['director'])

all_genres = get_unique('genres_list')
all_cast = get_unique('cast_list')
all_directors = get_unique('director_list')
all_production = get_unique('production_list')

# -----------------------
# Sidebar Filters
# -----------------------
st.sidebar.header("🔍 Filter Movies")

selected_genres = st.sidebar.multiselect("Genres", all_genres)
selected_cast = st.sidebar.multiselect("Cast", all_cast)
selected_director = st.sidebar.multiselect("Director", all_directors)
selected_production = st.sidebar.multiselect("Production Company", all_production)

# -----------------------
# Reset page when filters change
# -----------------------
current_filter_state = (
    tuple(selected_genres),
    tuple(selected_cast),
    tuple(selected_director),
    tuple(selected_production)
)

if "last_filter_state" not in st.session_state:
    st.session_state.last_filter_state = current_filter_state

if st.session_state.last_filter_state != current_filter_state:
    st.session_state.page = 0
    st.session_state.last_filter_state = current_filter_state

# -----------------------
# Dropdown Search
# -----------------------
selected_movie = st.selectbox(
    "Search for a movie",
    ["-- Select a movie --"] + list(movies['title'].values),
    index=(["-- Select a movie --"] + list(movies['title'].values)).index(st.session_state.selected_movie)
)

if selected_movie != st.session_state.selected_movie:
    st.session_state.selected_movie = selected_movie
    st.rerun()

# -----------------------
# MOVIE DETAIL VIEW
# -----------------------
if st.session_state.selected_movie != "-- Select a movie --":
        # Hide sidebar in movie detail view
    hide_sidebar = """
        <style>
            section[data-testid="stSidebar"] {
                display: none;
            }
            div[data-testid="stAppViewBlockContainer"] {
                padding-left: 1rem !important;
            }
        </style>
    """
    st.markdown(hide_sidebar, unsafe_allow_html=True)

    movie_df = movies[movies['title'] == st.session_state.selected_movie]

    if not movie_df.empty:
        movie_data = movie_df.iloc[0]

        # Back button
        if st.button("⬅️ Back to Explore"):
            st.session_state.selected_movie = "-- Select a movie --"
            st.rerun()

        col1, col2 = st.columns([1, 2])

        with col1:
            st.image(movie_data['poster_url'], use_container_width=True)

        with col2:
            st.subheader(st.session_state.selected_movie)
            st.write(f"<div style='font-size:20px;'><u><b>Overview:</b></u> {movie_data['overview']}</div>", unsafe_allow_html=True)
            st.write(f"<div style='font-size:20px;margin-top:10px;'><u><b>Cast:</b></u> {movie_data['cast']}</div>", unsafe_allow_html=True)
            st.write(f"<div style='font-size:20px;margin-top:10px;'><u><b>Director:</b></u> {movie_data['director']}</div>", unsafe_allow_html=True)
            st.write(f"<div style='font-size:20px;margin-top:10px;'><u><b>Genres:</b></u> {movie_data['genres']}</div>", unsafe_allow_html=True)
            st.write(f"<div style='font-size:20px;margin-top:10px;'><u><b>Production Companies:</b></u> {movie_data['production_companies']}</div>", unsafe_allow_html=True)

            imdb_url = f"https://www.imdb.com/title/{movie_data['imdb_id']}/"

            st.markdown(
                f"""
                <a href="{imdb_url}" target="_blank" 
                   style="display:inline-block; margin-top:20px; 
                          font-size:20px; font-weight:600; 
                          color:#F5C518; text-decoration:none;">
                   ⭐ View on IMDb
                </a>
                """,
                unsafe_allow_html=True
            )

        st.markdown("---")
        st.markdown("## 🎥 Explore Similar Movies")

        recommendations = recommend(st.session_state.selected_movie)

        cols = st.columns(5)


        
        for i, movie in enumerate(recommendations):
            movie_row = movies[movies['title'] == movie]

            if not movie_row.empty:
                movie_row = movie_row.iloc[0]

                with cols[i % 5]:
                    st.markdown(
                        f"""
                        <div style="
                            width:180px;
                            height:270px;
                            display:flex;
                            align-items:center;
                            justify-content:center;
                            overflow:hidden;
                            margin:auto;
                        ">
                            <img src="{movie_row['poster_url']}" 
                                title="{movie_row['title']}"
                                 style="height:100%; width:100%; object-fit:cover; border-radius:10px; cursor:pointer;">
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    

                    if st.button(format_title(movie), key=f"rec_{i}", help="", use_container_width=True):
                        st.session_state.selected_movie = movie
                        st.rerun()

# -----------------------
# EXPLORE / FILTER VIEW
# -----------------------
else:
    filtered_movies = movies.copy()

    if selected_genres:
        filtered_movies = filtered_movies[
            filtered_movies['genres_list'].apply(lambda x: any(i in x for i in selected_genres))
        ]

    if selected_cast:
        filtered_movies = filtered_movies[
            filtered_movies['cast_list'].apply(lambda x: any(i in x for i in selected_cast))
        ]

    if selected_director:
        filtered_movies = filtered_movies[
            filtered_movies['director_list'].apply(lambda x: any(i in x for i in selected_director))
        ]

    if selected_production:
        filtered_movies = filtered_movies[
            filtered_movies['production_list'].apply(lambda x: any(i in x for i in selected_production))
        ]

    st.markdown("## 🧐 Explore Movies")

    if len(filtered_movies) > 0:

        # Pagination
        movies_per_page = 20
        total_pages = (len(filtered_movies) - 1) // movies_per_page + 1

        start = st.session_state.page * movies_per_page
        end = start + movies_per_page

        page_movies = filtered_movies.iloc[start:end]

        cols = st.columns(5)

        for i, row in enumerate(page_movies.itertuples()):
            with cols[i % 5]:
                st.markdown(
                    f"""
                    <div style="
                        width:180px;
                        height:270px;
                        display:flex;
                        align-items:center;
                        justify-content:center;
                        overflow:hidden;
                        margin:auto;
                    ">
                        <img src="{row.poster_url}"
                            title="{row.title}"
                             style="height:100%; width:100%; object-fit:cover; border-radius:10px; cursor:pointer;">
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)


                if st.button(format_title(row.title), key=f"filter_{start+i}",use_container_width=True):
                    st.session_state.selected_movie = row.title
                    st.rerun()

                st.markdown("</div>", unsafe_allow_html=True)

        # Pagination controls
        col1, col2, col3 = st.columns([1, 2, 1])

        with col1:
            if st.button("⬅️ Prev") and st.session_state.page > 0:
                st.session_state.page -= 1
                st.rerun()

        with col3:
            if st.button("Next ➡️") and st.session_state.page < total_pages - 1:
                st.session_state.page += 1
                st.rerun()

        with col2:
            st.write(f"Page {st.session_state.page + 1} of {total_pages}")

    else:
        st.write("No movies match your filters.")