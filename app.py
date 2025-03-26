# import streamlit as st
# import os
# import pandas as pd
# from pages.home import show_home
# from pages.predictGames import show_predict_games
# from pages.moreGameInfo import show_more_game_info

# Define the base URI of the API
#   - Potential sources are in `.streamlit/secrets.toml` or in the Secrets section
#     on Streamlit Cloud
#   - The source selected is based on the shell variable passend when launching streamlit
#     (shortcuts are included in Makefile). By default it takes the cloud API url


# st.session_state.page = "Home"

# if st.session_state.page == "Home":
#     show_home()
# elif st.session_state.page == "Predict":
#     show_predict_games()
# elif st.session_state.page == "More":
#     show_more_game_info()

import streamlit as st
import os
import requests
import xml.etree.ElementTree as ET

if 'API_URI' in os.environ:
    BASE_URI = st.secrets[os.environ.get('API_URI')]
else:
    BASE_URI = st.secrets['cloud_api_uri']
# Add a '/' at the end if it's not there
BASE_URI = BASE_URI if BASE_URI.endswith('/') else BASE_URI + '/'
# Define the url to be used by requests.get to get a prediction (adapt if needed)
url = BASE_URI + 'predict'

# Function to fetch top 10 board games from BGG
def get_bgg_top_games(limit=10):
    """
    Fetches the top N hot games on BoardGameGeek.
    Returns a list of tuples: (title, image_url)
    """
    url = "https://boardgamegeek.com/xmlapi2/hot?type=boardgame"
    games = []

    try:
        response = requests.get(url)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            for item in root.findall("item")[:limit]:
                game_id = item.attrib["id"]
                # Fetch game details
                details_url = f"https://boardgamegeek.com/xmlapi2/thing?id={game_id}"
                details_resp = requests.get(details_url)
                if details_resp.status_code == 200:
                    details_root = ET.fromstring(details_resp.content)
                    image_url = details_root.find("item/image").text
                    title = details_root.find("item/name").attrib["value"]
                    games.append((title, image_url))
    except Exception as e:
        st.error(f"Failed to fetch game data: {e}")

    return games

# Function to generate the auto-scrolling banner with pause on hover
def generate_horizontal_scroller(games, height=250, speed=30):
    """
    Generates an auto-scrolling horizontal banner showing multiple images.
    """
    game_html = ""
    for title, image_url in games:
        game_html += f"""
        <div class="game-slide">
            <img src="{image_url}" alt="{title}" title="{title}" />
            <p>{title}</p>
        </div>
        """

    html = f"""
    <style>
    .scroll-container {{
        width: 100%;
        overflow: hidden;
        position: relative;
        background: #f9fafb; /* light gray background */
        border-radius: 10px;
        padding: 10px 0;
        border: 1px solid #e5e7eb;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);

    }}
    .scroll-track {{
        display: flex;
        width: max-content;
        animation: scroll-left {speed}s linear infinite;
    }}
    .scroll-container:hover .scroll-track {{
        animation-play-state: paused;
    }}
    .game-slide {{
        flex: 0 0 auto;
        width: 220px;
        margin: 0 10px;
        text-align: center;
        color: #111827;  /* darker text for white background */
        font-weight: 500;
    }}
    .game-slide img {{
        width: 100%;
        height: {height}px;
        object-fit: contain;
        border-radius: 8px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.4);
    }}
    @keyframes scroll-left {{
        0% {{ transform: translateX(0); }}
        100% {{ transform: translateX(-50%); }}
    }}
    </style>
    <div class="scroll-container">
        <div class="scroll-track">
            {game_html}
            {game_html} <!-- repeat to loop smoothly -->
        </div>
    </div>
    """
    return html

# Homepage function
def show_home():
    st.set_page_config(page_title="🧠 Board Game Terminal", layout="wide")

    # Custom CSS styling
    st.markdown("""
        <style>
        .main {
            background-color: #111827;
            color: white;
        }
        .stButton button {
            background-color: #2563EB;
            color: white;
            font-weight: bold;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            border: none;
        }
        .stButton button:hover {
            background-color: #1E40AF;
            transform: scale(1.02);
        }
        .emoji-box {
            font-size: 2.5rem;
            text-align: center;
            padding: 10px;
        }
        </style>
    """, unsafe_allow_html=True)

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
        # st.markdown("""
        #             <div style="text-align:center;">
        #             <button onclick="window.parent.postMessage({type: 'streamlit:setSessionState',
        #             key: 'page', value: 'Home'}, '*')"
        #             style="font-size:100px; background:none; border:none; cursor:pointer;" title="Back to Home">
        #             🏠</button></div>""",
        #             unsafe_allow_html=True
        #             )
        if st.button("🏠 Back home", key="Home", use_container_width=True):
            try:
                st.switch_page('app.py')
            except:
                pass



    # # --- Header Video ---
    # video_file = "game_over.mp4"
    # if os.path.exists(video_file):
    #     with open(video_file, "rb") as f:
    #         video_bytes = f.read()

    #     st.video(video_bytes)
    # else:
    #     st.warning("🎞️ game_over.mp4 not found.")



    # Banner Section
    st.markdown("---")
    st.markdown("## 📢 Top 10 board games from BGG")

    games = get_bgg_top_games(limit=10)
    if games:
        scroller_html = generate_horizontal_scroller(games, height=220, speed=70)
        st.components.v1.html(scroller_html, height=310)
    else:
        st.info("Could not load games from BoardGameGeek.")

    # Objective Section
    st.markdown("---")
    st.markdown("## 🎯 Mission Control: What's This App About?")
    st.markdown("""
    <div style='font-size: 1.2rem; line-height: 1.8;'>
        <ul>
            <li>🔍 <b>Explore</b> a vast galaxy of top board games</li>
            <li>🧠 <b>Predict</b> which ones will suit your style</li>
            <li>💻 <b>Find</b> the right games for the right person</li>
            <li>📊 <b>Dive</b> into geeky game insights and data</li>
        </ul>
        <p>This is your <strong>Terminal of Play</strong>.</p>
    </div>
    """, unsafe_allow_html=True)


    # Option Buttons
    st.markdown("---")
    st.markdown("## 🚀 Launch Menu")
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        if st.button("🔎 Predict which ones will suit your style"):
            st.session_state['type_from_home'] = "Based on my BGG"
            # st.session_state.page = "Predict games"
            st.switch_page('pages/predictGames.py')


    with col_b:
        if st.button("📈 Find the right games for the right person"):
            st.session_state['type_from_home'] = "Game for a friend"
            # st.session_state.page = "Predict games"
            st.switch_page('pages/predictGames.py')


    with col_c:
        if st.button("🤖 Explore a vast galaxy of top board games"):
            st.session_state['type_from_home'] = "Games for tonight"
            # st.session_state.page = "Predict games"
            st.switch_page('pages/predictGames.py')


    # Footer
    st.markdown("---")
    st.caption("👾 Built by geeks, for geeks. Powered by Streamlit. © 2025 Ganggraine Game Labs™️")

# Enable running directly
# if __name__ == "__main__":
show_home()
