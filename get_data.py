import pandas as pd
import json
from statsbombpy import sb


def getCompet():
    # Retrieve all competitions
    competitions = sb.competitions()

    # Convert competition data to DataFrame
    df = pd.DataFrame(competitions)

    # Create an empty dictionary to store unique competition names and IDs
    competitions_dict = {}

    # Populate the dictionary with unique competition names and IDs
    for i, season in df.iterrows():
        competition_id = season['competition_id']
        competition_name = season['competition_name']

        # Check if the competition name already exists in the dictionary
        if competition_name not in competitions_dict:
            competitions_dict[competition_name] = competition_id

    return competitions_dict


def getSeasons(compet_id):
    # Retrieve information about all competitions
    competitions = sb.competitions()

    # Convert competition data to DataFrame
    df = pd.DataFrame(competitions)

    # Find the desired competition by its ID
    df_compet = df[df['competition_id'] == compet_id]

    # Create an empty dictionary to store unique season names and IDs
    seasons_dict = {}

    # Populate the dictionary with unique season names and IDs
    for i, season in df_compet.iterrows():
        season_id = season['season_id']
        season_name = season['season_name']

        # Check if the season name already exists in the dictionary
        if season_name not in seasons_dict:
            seasons_dict[season_name] = season_id

    return seasons_dict


def getMatches(compet_id, season_id):
    # Retrieve match data for the specific competition and season
    matches = sb.matches(competition_id=compet_id, season_id=season_id)

    # Convert match data to DataFrame
    df = pd.DataFrame(matches)

    # Create an empty dictionary to store matches names and IDs
    matches_dict = {}

    # Populate the dictionary with matches names and IDs
    for i, match in df.iterrows():
        match_id = match['match_id']
        match_name = f"{match['home_team']} VS {match['away_team']}"
        home_score = match['home_score']
        away_score = match['away_score']

        matches_dict[match_name] = [match_id, match['home_team'], match['away_team'], home_score, away_score]

    return matches_dict

def getMatchinfo(compet_id, season_id, match_id):
    # Retrieve match data for the specific competition and season
    matches = sb.matches(competition_id=compet_id, season_id=season_id)

    # Convert match data to DataFrame
    df = pd.DataFrame(matches)

    # Convert the match_id row to JSON
    row_json = df.loc[df['match_id'] == match_id].to_dict()

    # Transform the row python dict into a string JSON
    json_string = json.dumps(row_json, indent=2)

    return json_string

def getTeams(match_id):
    # Retrieve event data for the specific match
    events = sb.events(match_id=match_id)

    # Convert events data to DataFrame
    df = pd.DataFrame(events)

    # Extract teams from the event data
    teams_dict = {}

    # Populate the dictionary with teams names and IDs
    for i, event in df.iterrows():
        team_name = event['team']
        team_ID = event['team_id']

        # Check if the team name already exists in the dictionary
        if team_name not in teams_dict:
            teams_dict[team_name] = team_ID

    return teams_dict


def getEvents(match_id):
    # Access event data for a specific match
    events = sb.events(match_id=match_id)

    # Convert events data to DataFrame
    df = pd.DataFrame(events)

    return df

def getLineups(match_id, team_name):
    # Access team lineup and players info for a specific match
    lineup = sb.lineups(match_id=match_id)[team_name]

    # Convert lineup data to DataFrame
    df_lineup = pd.DataFrame(lineup)

    return df_lineup
