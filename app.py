import os
import pandas as pd
import streamlit as st

from pages.home import show_home
from pages.predictGames import show_predict_games
from pages.moreGameInfo import show_more_game_info

# Define the base URI of the API
#   - Potential sources are in `.streamlit/secrets.toml` or in the Secrets section
#     on Streamlit Cloud
#   - The source selected is based on the shell variable passend when launching streamlit
#     (shortcuts are included in Makefile). By default it takes the cloud API url
if 'API_URI' in os.environ:
    BASE_URI = st.secrets[os.environ.get('API_URI')]
else:
    BASE_URI = st.secrets['cloud_api_uri']
# Add a '/' at the end if it's not there
BASE_URI = BASE_URI if BASE_URI.endswith('/') else BASE_URI + '/'
# Define the url to be used by requests.get to get a prediction (adapt if needed)
url = BASE_URI + 'predict'

# Just displaying the source for the API. Remove this in your final version.
# st.markdown(f"Working with {url}")

# st.markdown("Now, the rest is up to you. Start creating your page.")

import streamlit as st

# Sidebar navigation
st.sidebar.title("Home")
page = st.sidebar.radio("Go to", ["Home", "Predict games", "More game info"])

# Display selected page
if page == "Home":
    show_home()
elif page == "Predict games":
    show_predict_games()
elif page == "More game info":
    show_more_game_info()
