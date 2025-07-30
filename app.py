import streamlit as st
import pandas as pd
import pickle # Used for loading data

# --- Streamlit App Layout Configuration (MUST BE THE FIRST STREAMLIT COMMAND) ---
st.set_page_config(layout="wide", page_title="Movie Recommendation System")

# --- Load the pickled data ---
try:
    with open('movie_data.pkl', 'rb') as file:
        movies, cosine_sim = pickle.load(file)
    # st.success("Movie data loaded successfully!") # You can remove this; app will proceed if successful
except FileNotFoundError:
    st.error("Error: 'movie_data.pkl' not found. Please run Movie_Recommendation_System.ipynb first.")
    st.stop()
except Exception as e:
    st.error(f"Error loading movie data: {e}")
    st.stop()

# --- Create a Series to map movie titles to their index ---
indices = pd.Series(movies.index, index=movies['title']).drop_duplicates()

# --- Recommendation Function ---
def recommend(title, num_recommendations=5):
    """
    Recommends movies similar to the given title.

    Args:
        title (str): The title of the movie to get recommendations for.
        num_recommendations (int): The number of recommendations to return.

    Returns:
        pandas.DataFrame: A DataFrame containing 'title', 'movie_id', and 'poster_path'
                          of the recommended movies. Returns an empty DataFrame if
                          the input movie title is not found.
    """
    if title not in indices:
        st.warning(f"Movie '{title}' not found in our database. Please select from the list.")
        return pd.DataFrame()

    idx = indices[title]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Get the scores of the N most similar movies. Skip the first one (the movie itself).
    sim_scores = sim_scores[1:num_recommendations+1]

    movie_indices = [i[0] for i in sim_scores]

    # Return a DataFrame with the necessary info for display
    recommended_movies_df = movies.iloc[movie_indices][['title', 'movie_id', 'poster_path']]
    return recommended_movies_df

# --- Streamlit App UI ---
st.title("🎬 Movie Recommendation System")
st.markdown("---") # Visual separator

# Dropdown for movie selection
selected_movie = st.selectbox("Select a movie from the list:", movies['title'].values)

# Button to trigger recommendations
if st.button("Get Recommendations"):
    if selected_movie:
        # Call the recommend function
        recommendations_df = recommend(selected_movie, num_recommendations=5)

        if not recommendations_df.empty:
            st.subheader(f"Recommendations similar to **{selected_movie}**:")

            # Create columns to display movies horizontally
            num_cols = len(recommendations_df)
            cols = st.columns(num_cols)

            for i, (index, row) in enumerate(recommendations_df.iterrows()):
                with cols[i]: # Place content in the i-th column
                    st.markdown(f"**{row['title']}**") # Display title above poster
                    if row['poster_path'] and row['poster_path'] != '':
                        full_poster_url = f"https://image.tmdb.org/t/p/w500{row['poster_path']}"
                        st.image(
                            full_poster_url,
                            caption=f"({row['title']})",
                            # FIX: Changed 'use_column_width' to 'use_container_width'
                            use_container_width=True
                        )
                    else:
                        st.image(
                            "https://via.placeholder.com/500x750.png?text=No+Poster",
                            caption=f"No poster available for {row['title']}",
                            # FIX: Changed 'use_column_width' to 'use_container_width'
                            use_container_width=True
                        )
        else:
            st.warning("Sorry! No recommendations found for this movie or movie not in database.")
    else:
        st.info("Please select a movie from the dropdown to get recommendations.")

st.markdown("---")
st.markdown("💡 This is a content-based recommendation system based on movie genres, keywords, cast, and crew (director).")
st.markdown("Created with ❤️ by Your Name/Team Name") # Remember to personalize this!