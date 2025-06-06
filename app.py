import streamlit as st
from streamlit_extras.colored_header import colored_header
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.grid import grid

import matplotlib.pyplot as plt
import get_data
import score
import match_agent

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

# Streamlit app
st.set_page_config(page_title="Football Match Chatbox", layout="wide", initial_sidebar_state="expanded")
st.title("Football Match Chatbox")

# Set up the sidebar
with st.sidebar:
    # Image
    st.image("assets/FootballChatbox.jpg")

    st.toast(f'Getting Competitions List !:page_facing_up:')
    # Get all competition info
    competitions_dict = get_data.getCompet()

    # Selection of competitions
    selected_compet = st.selectbox('Select a competition', list(competitions_dict.keys()), index=None)

    if selected_compet != None:
        st.toast(f'Getting Seasons Played !:calendar:')
        # Get competition ID
        competition_id = competitions_dict[selected_compet]

        # Get seasons for the selected competition
        seasons_dict = get_data.getSeasons(competition_id)

        # Season selection
        selected_season = st.selectbox('Select a season :spiral_calendar_pad:', list(seasons_dict.keys()), index=None)

    if "selected_season" in locals() and selected_season != None:
        st.toast(f'Getting Match Played in the season !')
        # Get the season ID
        season_id = seasons_dict[selected_season]

        # Get matches played in that season
        matches_dict = get_data.getMatches(competition_id, season_id)

        # Match selection
        selected_match = st.selectbox('Select a match', list(matches_dict.keys()), index=None)


if "selected_match" in locals() and selected_match != None:
    st.toast(f'Getting Match Event Data !:card_file_box:')
    # Get the Match ID
    match_id = matches_dict[selected_match][0]

    # Get Teams names
    home_team = matches_dict[selected_match][1]
    away_team = matches_dict[selected_match][2]

    # Get match score
    home_score = matches_dict[selected_match][3]
    away_score = matches_dict[selected_match][4]

    # Get match info
    match_info = get_data.getMatchinfo(compet_id=competition_id, season_id=season_id, match_id=match_id)

    # Get match event data
    Events_data = get_data.getEvents(match_id)

    # Get teams lineups data
    home_lineup = get_data.getLineups(match_id=match_id, team_name=home_team)
    away_lineup = get_data.getLineups(match_id=match_id, team_name=away_team)



if "Events_data" in locals() and "home_lineup" in locals() and "away_lineup" in locals() and "match_info" in locals() and "match_id" in locals():
    # Get match score
    scores = score.count_goals(Events_data, home_team, away_team)
    # Displaying the match score
    score.display_score(home_team, away_team, scores[home_team], scores[away_team])

    # Dataframes list for the agent
    df_list = [Events_data, home_lineup, away_lineup]

    # Initialize the chatbox memory
    if "memory" not in st.session_state:
        st.session_state.memory = None

    # Initialize the chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

        st.session_state.messages.append(SystemMessage("Act like a sport reporter"))

    # Initialize the current match_id
    if "current_match_id" not in st.session_state:
        st.session_state.current_match_id = match_id


    # Clean chatbox memory and chat history if match change
    if st.session_state.current_match_id != match_id:
        st.session_state.memory = None
        st.session_state.messages = []
        st.session_state.current_match_id = match_id


    # Get match agent
    initial_response, agent = match_agent.match_agent(match_info=match_info, df_list=df_list)

    # Display the match context
    st.markdown(initial_response)


    # display chat messages from history on app rerun
    for message in st.session_state.messages:
        if isinstance(message, HumanMessage):
            with st.chat_message("user"):
                st.markdown(message.content)
        elif isinstance(message, AIMessage):
            with st.chat_message("assistant"):
                st.markdown(message.content)

    # create the bar where we can type messages
    prompt = st.chat_input("Ask me your question ...")

    # did the user submit a prompt?
    if prompt:
        # add the message from the user (prompt) to the screen with streamlit
        with st.chat_message("user"):
            st.markdown(prompt)

            st.session_state.messages.append(HumanMessage(prompt))
        # create the echo (response)
        if st.session_state.memory is None:
            result, new_memory = match_agent.match_chat(match_summary=initial_response, agent=agent,
                                                        user_question=prompt)
            st.session_state.memory = new_memory
        else:
            result, new_memory = match_agent.match_chat(agent=agent, user_question=prompt,
                                                        memory=st.session_state.memory)
            st.session_state.memory = new_memory

        with st.chat_message("assistant"):
            st.markdown(result)

            st.session_state.messages.append(AIMessage(result))
