import streamlit as st
import pickle
import streamlit.components.v1 as components
import random
import pandas as pd

games = pickle.load(open('games.sav', 'rb'))
cosine_sim_df = pickle.load(open('cosine_sim.sav', 'rb'))
interaction_matrix = pickle.load(open('interaction_matrix.sav', 'rb'))
games_list = games['name'].values
user_list = games['user'].values
image_dict = dict(zip(games['name'], games['image']))

imageCarouselComponent = components.declare_component("image-carousel-component", path="frontend/public")

# Filter out entries with NaN values
image_dict_clean = {k: v for k, v in image_dict.items() if pd.notna(v)}
random_image_urls = random.sample(list(image_dict_clean.values()), 10)

imageCarouselComponent(imageUrls=random_image_urls, height=300)

st.header('Xbox-360 Recommendation System')
selectvalue = st.selectbox('Select game from dropdown', games_list)

def get_similar_games(games, cosine_sim_df, top_n=5):
    """
    Get top N similar games for a given game.
    """
    if games not in cosine_sim_df.index:
        return None, "Game not in dataset."

    # Get similarity scores for the given game
    sim_scores = cosine_sim_df[games]
    
    # Sort the games based on similarity scores
    sim_scores = sim_scores.sort_values(ascending=False)
    
    # Get the scores of the top-n most similar games
    top_similar = sim_scores.head(top_n).index
    
    return top_similar

def recommend_games(user, interaction_matrix, cosine_sim_df, top_n=5):
    """
    Recommend top N games for a given user.
    """
    # Check if user exists in the interaction matrix
    if user not in interaction_matrix.columns:
        return None, "User not found in dataset."

    # Get the games interacted by the user
    interacted_games = interaction_matrix[interaction_matrix[user] > 0].index.tolist()
    
    # Store all recommendations here
    all_recommendations = pd.Series(dtype='float64')
    
    # Get top similar games for each game interacted by the user
    for game in interacted_games:
        similar_games = get_similar_games(game, cosine_sim_df, top_n)
        # Convert Index to Series and append
        all_recommendations = all_recommendations.append(pd.Series(similar_games, index=similar_games))

    # Aggregate and sort recommendations
    recommendations = all_recommendations.groupby(all_recommendations.index).sum().sort_values(ascending=False)
    
    # Filter out games the user has already interacted with
    recommendations = recommendations[~recommendations.index.isin(interacted_games)]
    
    return recommendations.head(top_n).index.tolist()

if st.button("Show Recommendations"):
    game_recommend = get_similar_games(selectvalue, cosine_sim_df)
    if not game_recommend.empty:
        # Adjust the number of columns based on the number of recommendations
        cols = st.columns(len(game_recommend))
        for i, game_name in enumerate(game_recommend):
            with cols[i]:
                if game_name in image_dict:
                    st.image(image_dict[game_name], width=200)  # Adjust width as needed
                else:
                    st.write("No image available")
                st.caption(game_name)  # Use caption for a smaller font size