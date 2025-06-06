import streamlit as st

def count_goals(data, home_team, away_team):
    # Filter for goals
    goal_events = data[data['shot_outcome'] == 'Goal']

    # Defining a dictionnary to store the scores
    scores = {home_team: 0, away_team: 0}

    for i, goal in goal_events.iterrows():
        if goal['team'] == home_team:
            scores[home_team] += 1
        else:
            scores[away_team] += 1

    return scores

def display_score(home_team, away_team, home_score, away_score):

    st.markdown(f"""
    <h1 style="text-align: center;">
        ⚽️ {home_team} 🟥 **{home_score} - {away_score}** 🟦 {away_team} ⚽️
    </h1>
    """, unsafe_allow_html=True)