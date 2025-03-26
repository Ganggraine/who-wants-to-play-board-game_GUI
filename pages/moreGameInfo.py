import streamlit as st
import requests
import xmltodict
import os


def show_banner():
    # --- TOP BAR ---
    with st.container():
        # Top Row Layout
        col1, col2, col3 = st.columns([1, 6, 1])

        with col1:
            if os.path.exists("media/logo.png"):
                st.image("media/logo.png")
            else:
                st.markdown("<div class='emoji-box'>🎮</div>", unsafe_allow_html=True)

        with col2:
            st.markdown("<h1 style='text-align: center;'>MEEPLE'S GAMELIST</h1>", unsafe_allow_html=True)

        with col3:
            st.markdown("""
                        <div style="text-align:center;">
                        <button onclick="window.parent.postMessage({type: 'streamlit:setSessionState',
                        key: 'page', value: 'Home'}, '*')"
                        style="font-size:100px; background:none; border:none; cursor:pointer;" title="Back to Home">
                        🏠</button></div>""",
                        unsafe_allow_html=True
                        )

def show_bloc_game_info(game_id):
        @st.cache_data
        def game_info(game_id):
            '''
            Retrieve games information from a list of game IDs.
            - Takes a list of game IDs
            - Requests BGG API
            - Returns data as a list of dictionaries
            '''
            # list_column = ['@objectid', 'yearpublished', 'minplayers', 'maxplayers', 'playingtime',
            #     'minplaytime', 'maxplaytime', 'age', 'name', 'description', 'thumbnail',
            #     'image', 'boardgameaccessory', 'boardgamepublisher', 'cardset',
            #     'boardgamepodcastepisode', 'boardgamehonor', 'boardgamecategory',
            #     'videogamebg', 'boardgamedesigner', 'boardgameartist',
            #     'boardgameversion', 'boardgamefamily', 'boardgamemechanic',
            #     'boardgamesubdomain', 'boardgameimplementation', 'poll', 'poll-summary',
            #     'rpgpodcastepisode']
            list_column = ['@objectid','yearpublished',
                        'minplayers', 'maxplayers',
                        'playingtime','minplaytime',
                        'maxplaytime', 'age', 'name',
                        'description', 'thumbnail', 'image',
                        'boardgamepublisher','boardgamedesigner', 'boardgameartist',
                        'boardgamehonor', 'boardgamecategory',
                        'boardgamefamily', 'boardgamemechanic','boardgamesubdomain',
                            'statistics'
                        ]
            BASE_URL_BGG_GAME = 'https://boardgamegeek.com/xmlapi/boardgame/'
            response = requests.get(BASE_URL_BGG_GAME +str(game_id)+'?stats=1')

            if response.status_code != 200:
                print(f"Request failed with status code {response.status_code}")
                return []

            data_dict = xmltodict.parse(response.content)

            games = data_dict.get('boardgames', {}).get('boardgame', [])
            if not isinstance(games, list):
                games = [games]  # Ensure it's always a list

            result = []
            for game in games:
                entry = {}
                for key in list_column:
                    value = game.get(key, '')
                    if isinstance(value, dict):
                        # If the value is a dictionary, get the '#text' field
                        if key == 'statistics':
                            entry['average'] = value.\
                                get('ratings','').\
                                get('average','')
                            entry['averageweight'] = value.\
                                get('ratings','').\
                                get('averageweight','')
                        else:
                            entry[key] = value.get('#text', '')
                    elif isinstance(value, list):
                        # If the value is a list, take the first element's '#text' field
                        # entry[key] = value[0].get('#text', '') if value else ''
                        if key == 'name':
                            for v in value:
                                if v.get('@primary', ''):
                                    entry['main_name'] = v.get('#text', '')

                        entry[key] = [v.get('#text', '') for v in value]
                    else:
                        # Keep the value or default to an empty string
                        entry[key] = value or ''
                result.append(entry)
            # print(result)
            return result
        st.session_state['current_id'] = None

        game = game_info(game_id)[0]

        col1,col2 = st.columns([1,2])
        col1.image(game['image'],use_container_width = True)
        col2.header(f"**{game['main_name']}**")
        bgg_url = f"https://boardgamegeek.com/boardgame/{game.get('@objectid')}"
        col2.markdown(f"*<a href='{bgg_url}' target='_blank'>Find more infos on boardgamegeek.com</a>*", unsafe_allow_html=True)

        if game.get('name'):
            with col2.container():
                st.write("Other names")
                st.write("*"+', '.join(game['name'])+"*")


        st.markdown("""
                    #### General infos:
                    """)
        col1,col2 = st.columns([1,2])

        with col1.container(height = 500 ,border=True):

            list_numerical = [["average","Average rating"],
                            ["averageweight","Complexity rating"],
                            ["yearpublished","Year published"],
                            ["minplayers","Minimun number of players"],
                            ["maxplayers","Maximun number of players" ],
                            ["age", "Age"],
                            ["playingtime","Playing time"]]

            for num in list_numerical:
                if game.get(num[0]):
                    st.markdown(f"""
                            __{num[1]}__\n
                                {round(float(game.get(num[0])),1)}
                            """)


        with col2.container(height = 500 ,border=True):
            list_info = [
            [
                [
                    ["description","Description"]
                ],"Description"
            ],
            [
                [
                    ["boardgamecategory","Categories"],
                    ["boardgamefamily","Families"],
                    ["boardgamemechanic","Mechanics"],
                ],"Categories"
            ],
            [
                [
                    ["boardgamepublisher",'Publishers'],
                    ["boardgamedesigner",'Designers'],
                    ["boardgameartist",'Artists']
                ]
                ,"They work on it"
            ],
            [
                [
                    ["boardgamehonor",'Honors'],
                ]
                ,"More"
            ]
        ]
            name = []
            for idx in range(len(list_info)):
                name.append(list_info[idx][1])
            tab = st.tabs(name)

            for idx in range(len(list_info)):
                topics = list_info[idx][0]
                for item in topics :
                    title = item[1]
                    key_dic = item[0]
                    if game.get(key_dic):
                        tab[idx].markdown(f"__{title}__")
                        if isinstance(game.get(key_dic), list):
                            for li_ in game.get(key_dic):
                                tab[idx].markdown("- " + li_)
                        else :
                            tab[idx].markdown(f"{game.get(key_dic)}")

def show_more_game_info(game_id: int = 224517):
    st.set_page_config(
        page_title="MG - Game infos",
        page_icon="💬",
        layout="wide",
        initial_sidebar_state="auto",
        menu_items=None
    )
    show_banner()
    if st.session_state['current_id']:
        show_bloc_game_info(st.session_state['current_id'])
    else:
        show_bloc_game_info('284818')


if __name__ == '__main__':

    show_more_game_info()
