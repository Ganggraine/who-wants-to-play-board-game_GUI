import streamlit as st
import requests
import pandas as pd
import os
from pages.moreGameInfo import show_more_game_info

from constant.params import *

#-------------------------------------------------------------------------
#
#     CONSTANTS
#
#-------------------------------------------------------------------------
# OPTION_OFFER_TO_NEPHEW = "What can I offer to my nephew?"
# OPTION_PLAYLIST_FOR_TONIGHT = "What's 'play'-list for tonight?"
# OPTION_BOARD_GAME_LIBRARY = "What game I must have in my board game library?"
OPTION_OFFER_TO_NEPHEW = "Game for a friend"
OPTION_PLAYLIST_FOR_TONIGHT = "Games for tonight"
OPTION_BOARD_GAME_LIBRARY = "Based on my BGG"

ERROR_API_RESPONSE_FORMAT = "The API response is not in the expected format."
ERROR_INVALID_BGG_USER_ID = "Please enter a valid BGG user ID!"

BASE_ENDPOINTS_URL = "https://api-326525614739.europe-west1.run.app/"

#-------------------------------------------------------------------------
#
#     FUNCTIONS
#
#-------------------------------------------------------------------------
@st.cache_data
def load_parquet_data():
    file_path_category = './categories_data/category_data.parquet'
    file_path_family = './categories_data/family_data.parquet'
    file_path_mechanic = './categories_data/mechanic_data.parquet'

    df_category = pd.read_parquet(file_path_category)
    df_family = pd.read_parquet(file_path_family)
    df_mechanic = pd.read_parquet(file_path_mechanic)

    return df_category, df_family, df_mechanic

def get_user_input():
    user_id = st.text_input("BGG user ID:", key="user_id")
    game_option = st.selectbox(
        "Choose an option:",
        ("Both", "Play one of my games", "Play to buy a new game"),
        key="game_option"
    )
    return user_id, game_option

def get_game_details():
    cluster = st.selectbox("Select Game Cluster:", list(CLUSTER_MAP.values()), key="cluster")
    playingtime = st.selectbox("Playing Time (in minutes):", list(PLAYING_TIME.keys()), key="playingtime")
    minplayers = st.number_input("Minimum Players:", min_value=1, value=1, step=1, key="minplayers")
    age = st.selectbox("Minimum Age:", list(AGE.keys()), key="age")
    yearpublished = st.selectbox("Year Published:", list(YEAR_PUBLISHED.keys()), key="yearpublished")

    df_category, df_family, df_mechanic = load_parquet_data() # Done once only!

    category_options = [""] + df_category['boardgamecategory'].dropna().unique().tolist()
    mechanic_options = [""] + df_mechanic['boardgamemechanic'].dropna().unique().tolist()
    family_options = [""] + df_family['boardgamefamily'].dropna().unique().tolist()

    boardgamecategory = st.multiselect("Select category:", category_options,  help="Select a category")
    boardgamemechanic = st.multiselect("Select mechanic:", mechanic_options,  help="Select a mechanic")
    boardgamefamily = st.multiselect("Select family:", family_options,  help="Select a family")

    return {
        "cluster": cluster,
        "playingtime": playingtime,
        "minplayers": minplayers,
        "age": age,
        "yearpublished": yearpublished,
        "boardgamecategory": boardgamecategory,
        "boardgamemechanic": boardgamemechanic,
        "boardgamefamily": boardgamefamily
    }

def make_api_call(endpoint, params):
    url = f"{st.secrets.cloud_api_uri}{endpoint}"
    response = requests.get(url, params=params)
    print(response.url)
    return response

def handle_api_response(response):
    if response.status_code == 200:
        games = response.json()
        if isinstance(games, list) and all(isinstance(game, dict) for game in games):
            st.session_state['games_list'] = games
        else:
            st.session_state['games_list'] = []
            st.error(ERROR_API_RESPONSE_FORMAT)
    else:
        st.session_state['games_list'] = []
        st.error(f"API call error: {response.status_code}")

def show_predict_games():
    #-------------------------------------------------------------------------
    #
    #     Graphical User Interface (GUI) with Streamlit
    #
    #-------------------------------------------------------------------------
    # --- TOP BAR ---
    with st.container():
        # Top Row Layout
        col1, col2, col3 = st.columns([1, 6, 1])

        with col1:
            if os.path.exists("media/logo.png"):
                st.image("media/logo.png",width=150)
            else:
                st.markdown("<div class='emoji-box'>🎮</div>", unsafe_allow_html=True)

        with col2:
            st.markdown("<h1 style='text-align: center;'>MEEPLE'S GAMELIST</h1>", unsafe_allow_html=True)

        with col3:
            if st.button("🏠 Back home", key="Home", use_container_width=True):
                try:
                    st.switch_page('app.py')
                except:
                    pass

    if 'games_list' not in st.session_state:
        st.session_state['games_list'] = []

    # Layout with two columns
    col1, col2 = st.columns([1, 3])

    with col1: # LEFT PANEL
        choices = [OPTION_BOARD_GAME_LIBRARY, OPTION_OFFER_TO_NEPHEW, OPTION_PLAYLIST_FOR_TONIGHT]
        option = st.segmented_control("", choices,default = st.session_state['type_from_home'], selection_mode="single")

        if option == OPTION_BOARD_GAME_LIBRARY:
            user_id, game_option = get_user_input()
        elif option == OPTION_PLAYLIST_FOR_TONIGHT:
            user_id, game_option = get_user_input()
            game_details = get_game_details()
            ratio_filter = st.slider(label="Ratio filtered games/User games (%)", min_value=10,max_value=90,value=90, step=5)
        else: # "What can I offer to my nephew?"
            game_details = get_game_details()

        col_left, col_right = st.columns([3, 1])
        with col_right:
            if st.button("Find games"):
                if option == OPTION_BOARD_GAME_LIBRARY:
                    if user_id:
                        params = {
                            "userID": user_id,
                            "predict_option": game_option
                        }

                        response = make_api_call("predict_userID", params)
                        handle_api_response(response)
                    else:
                        st.session_state['games_list'] = []
                        st.warning(ERROR_INVALID_BGG_USER_ID)
                elif option == OPTION_PLAYLIST_FOR_TONIGHT:
                    if user_id:
                        # Get the cluster index from the selection
                        selected_cluster = next(key for key, value in CLUSTER_MAP.items() if value == game_details["cluster"])
                        # Extract average and usersrated from CLUSTER_CENTERS
                        average, usersrated = CLUSTER_CENTERS[selected_cluster]

                        # API call to retrieve games
                        params = {
                            "average": average,
                            "usersrated": float(usersrated),
                            "playingtime": PLAYING_TIME[game_details["playingtime"]],
                            "minplayers": game_details["minplayers"],
                            "age": AGE[game_details["age"]],
                            "yearpublished": YEAR_PUBLISHED[game_details["yearpublished"]],
                            "boardgamecategory": str(game_details["boardgamecategory"]),
                            "boardgamemechanic": str(game_details["boardgamemechanic"]),
                            "boardgamefamily": str(game_details["boardgamefamily"]),
                            "userID": user_id,
                            "predict_option": game_option,
                            "ratio_filter": float(ratio_filter/100)
                        }

                        response = make_api_call("predict_party", params)
                        handle_api_response(response)

                    else:
                        st.session_state['games_list'] = []
                        st.warning(ERROR_INVALID_BGG_USER_ID)
                else: # "What can I offer to my nephew?"
                    # Get the cluster index from the selection
                    selected_cluster = next(key for key, value in CLUSTER_MAP.items() if value == game_details["cluster"])
                    # Extract average and usersrated from CLUSTER_CENTERS
                    average, usersrated = CLUSTER_CENTERS[selected_cluster]

                    # API call to retrieve games
                    params = {
                        "average": average,
                        "usersrated": float(usersrated),
                        "playingtime": PLAYING_TIME[game_details["playingtime"]],
                        "minplayers": game_details["minplayers"],
                        "age": AGE[game_details["age"]],
                        "yearpublished": YEAR_PUBLISHED[game_details["yearpublished"]],
                        "boardgamecategory": str(game_details["boardgamecategory"]),
                        "boardgamemechanic": str(game_details["boardgamemechanic"]),
                        "boardgamefamily": str(game_details["boardgamefamily"]),
                    }

                    response = make_api_call("predict_filters", params)

                    handle_api_response(response)

        with col2: # RIGHT AREA TO DISPLAY GAMES
            st.write(f"## {option}")

            if st.session_state['games_list']:
                for game in st.session_state['games_list']:
                    col_img, col_details, col_button = st.columns([1, 4, 1])
                    with col_img:
                        if game.get('image'):
                            st.image(game['thumbnail'], width=100)
                        else:
                            st.write("No image available.")
                    with col_details:
                        st.markdown(f"**Name:** {game.get('name', 'N/A')}")
                        st.markdown(f"**Age:** {game.get('age', 'Not specified')}")
                        st.markdown(f"**Description:** {game.get('description', 'No description available')[:100]}...")

                        bgg_url = f"https://boardgamegeek.com/boardgame/{game.get('@objectid')}"

                    with col_button :
                        if st.button('More infos',key = game.get('@objectid')):
                            st.session_state['current_id'] = game.get('@objectid')
                            st.switch_page('pages/moreGameInfo.py')
                        st.markdown(f" <a href='{bgg_url}' target='_blank'>BGG Info</a>", unsafe_allow_html=True)
            else:
                st.info("No games to display at the moment.")

# if __name__ == "__main__":
show_predict_games()
