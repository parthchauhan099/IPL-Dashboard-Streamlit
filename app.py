import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px


# load data
delivery_df = pd.read_csv('E:\Projects\ML\IPL DataAnalysis\deliveries.csv')
match_df = pd.read_csv('E:\Projects\ML\IPL DataAnalysis\matches.csv')
img = 'E:\Projects\ML\IPL DataAnalysis\ipl-logo.jpg'

# data pre-processing
match_df.replace({'season':
                  {'2007/08':'2008',
                  '2009/10':'2010',
                  '2020/21':'2020'}}, inplace=True)
match_df.replace({'team1':
            {'Delhi Daredevils':'Delhi Capitals',
            'Gujarat Lions':'Gujarat Titans',
            'Kings XI Punjab':'Punjab Kings',
            'Royal Challengers Bangalore':'Royal Challengers Bengaluru'}}, inplace=True)
match_df.replace({'team2':
            {'Delhi Daredevils':'Delhi Capitals',
            'Gujarat Lions':'Gujarat Titans',
            'Kings XI Punjab':'Punjab Kings',
            'Royal Challengers Bangalore':'Royal Challengers Bengaluru'}}, inplace=True)
match_df.replace({'toss_winner':
            {'Delhi Daredevils':'Delhi Capitals',
            'Gujarat Lions':'Gujarat Titans',
            'Kings XI Punjab':'Punjab Kings',
            'Royal Challengers Bangalore':'Royal Challengers Bengaluru'}}, inplace=True)

# list of unique teams
teams = ['Royal Challengers Bengaluru','Mumbai Indians', 'Kolkata Knight Riders','Rajasthan Royals',
        'Chennai Super Kings','Sunrisers Hyderabad','Delhi Capitals','Punjab Kings','Lucknow Super Giants', 'Gujarat Titans']

st.title("🏏 IPL Data Analysis")
st.divider()

players = pd.concat([delivery_df['batter'], delivery_df['bowler']])
all_players = sorted(players.unique())
all_season = sorted(match_df['season'].unique(), reverse=True)

st.sidebar.image(plt.imread(img), use_container_width=True)
radio = st.sidebar.radio(
    'Select Option',
    ['Overview', 'Batting Metrics', 'Bowling Metrics'])

if radio == 'Overview':
  st.subheader('Total Matches Per Season')
  matches_per_season = match_df['season'].value_counts().sort_index()
  fig = px.bar(x=matches_per_season.index, y=matches_per_season.values, labels={'x':'Season', 'y':'Matches'})
  st.plotly_chart(fig, use_container_width=True)
  
  st.subheader('IPL Winners')
  winning_teams = match_df[match_df['match_type']=='Final']['winner'].value_counts().sort_index()
  fig = px.bar(x=winning_teams.values, y=winning_teams.index, orientation='h',
                labels={'y':'Teams','x':'Wins'})
  st.plotly_chart(fig, use_container_width=True)
  
  col1, col2 = st.columns(2, gap='small')
  with col1:
      st.subheader('Top 10 Batsman')
      top_batsman = delivery_df.groupby('batter')['batsman_runs'].sum().sort_values(ascending=False).head(10)
      top_batsman.rename('Total Runs', inplace=True)
      st.table(top_batsman)
  with col2:
      st.subheader('Top 10 Bowler')
      top_bowler = delivery_df.groupby('bowler')['is_wicket'].sum().sort_values(ascending=False).head(10)
      top_bowler.rename('Total Wickets', inplace=True)
      st.table(top_bowler)    
  
  st.subheader('Toss win vs match win analysis')
  toss_match_win = match_df[match_df['toss_winner'] == match_df['winner']]
  percent = len(toss_match_win) / len(match_df) * 100
  st.metric(label='Toss Winner Also Won Match', value=f"{percent:.2f}%",
            delta=f"{len(toss_match_win)}/{len(match_df)}")
  
elif radio == 'Batting Metrics':
  selected_season = st.sidebar.selectbox(
    'Select Season',all_season)
  selected_player = st.sidebar.selectbox(
    'Select Player',all_players)

  delivery_filter = delivery_df.groupby(['match_id','batter','bowling_team','bowler']).agg({'total_runs': 'sum','ball': 'count'}).reset_index()
  match_filter = match_df[['id','venue','season']]
  batting_df = pd.merge(delivery_filter, match_filter, left_on='match_id', right_on='id')
  batting_df['fifty'] = (batting_df['total_runs']>=50) & (batting_df['total_runs']<=100)
  batting_df['hundred'] = batting_df['total_runs']>=100

  st.subheader(f"{selected_player} Performance in Season {selected_season}")
  col1, col2, col3, col4, col5 = st.columns(5)
  with col1:
    # Matches Played
    matches_played = batting_df[(batting_df['batter']=='V Kohli') & (batting_df['season']=='2023')]['match_id'].unique()
    st.metric('Matches Played', len(matches_played))
  with col2:
    # Total Runs
    total_runs = batting_df[(batting_df['batter']==selected_player) & (batting_df['season']==selected_season)]['total_runs'].sum()
    st.metric('Total Runs', total_runs)
  with col3:
    # Strike Rate
    total_ball_faced = batting_df[(batting_df['batter']==selected_player) & (batting_df['season']==selected_season)]['ball'].sum()
    strike_rate = round((total_runs / total_ball_faced) * 100, 2)
    st.metric('Stike Rate', strike_rate)
  with col4:
    # Fifty
    century_df = batting_df.groupby(['season','match_id','batter']).sum('total_runs').reset_index()
    century_df['fifty'] = (century_df['total_runs']>=50) & (century_df['total_runs']<=100)
    century_df['hundred'] = (century_df['total_runs']>=100)
    fifty = century_df[(century_df['batter']==selected_player) & (century_df['season']==selected_season) & (century_df['fifty'])]['fifty'].count()
    st.metric('Half Century', fifty)
  with col5:
    # Century
    hundred = century_df[(century_df['batter']==selected_player) & (century_df['season']==selected_season) & (century_df['hundred'])]['hundred'].count()
    st.metric('Century', hundred)

  # Runs per Season
  st.subheader(f'{selected_player} Runs per Season')
  season_runs = batting_df.groupby(['season','batter']).sum('total_runs').reset_index()
  runs = season_runs[season_runs['batter']==selected_player][['season','total_runs']]
  fig = px.line(runs, x='season', y='total_runs', labels={'total_runs':'Total Runs'})
  st.plotly_chart(fig, use_container_width=True)

  col1, col2 = st.columns(2, gap='small')
  with col1:
    # Runs against teams
    st.subheader(f'{selected_player} against Team')
    team = batting_df.groupby(['bowling_team','batter','season']).agg({'total_runs':'sum','match_id':'count'}).reset_index()
    team.rename(columns={'match_id':'match_played'}, inplace=True)
    team_stats = team[(team['batter']==selected_player) & (team['season']==selected_season)][['bowling_team','total_runs']].reset_index(drop=True)
    st.table(team_stats)

  with col2:
    # Runs against Bowler
    st.subheader(f'{selected_player} Vs Bowlers')
    runs_bowler_df = batting_df.groupby(['season','batter','bowler']).sum('total_runs').reset_index()
    bowler_stats = runs_bowler_df[(runs_bowler_df['batter']==selected_player) & (runs_bowler_df['season']==selected_season)][['bowler','total_runs']].sort_values(by='total_runs', ascending=False).reset_index(drop=True)
    st.table(bowler_stats.head(8))
  
  # Venue
  st.subheader(f'{selected_season} {selected_player} Performance by Stadium')
  stadium_df = batting_df.groupby(['season','batter','venue']).sum('total_runs').reset_index()
  stadium_stats = stadium_df[(stadium_df['batter']==selected_player) & (stadium_df['season']==selected_season)]
  fig = px.bar(stadium_stats, x='venue', y='total_runs', labels={'total_runs':'Runs'})
  st.plotly_chart(fig, use_container_width=True)

elif radio == 'Bowling Metrics':
  selected_season = st.sidebar.selectbox(
    'Select Season',all_season)
  selected_player = st.sidebar.selectbox(
    'Select Player',all_players)

  delivery_filter1 = delivery_df.groupby(['match_id','bowler']).agg({'is_wicket':'sum', 'ball':'count', 'total_runs':'sum', 'extra_runs':'sum'}).reset_index()
  match_filter1 = match_df[['id','venue','season']]
  bowling_df = pd.merge(delivery_filter1, match_filter1, left_on='match_id', right_on='id')
  bowling_df['over'] = bowling_df['ball'] // 6

  st.subheader(f"{selected_player} Performance in Season {selected_season}")
  col1, col2, col3, col4, col5 = st.columns(5)
  with col1:
    # Matches Played
    matches_played = bowling_df[(bowling_df['bowler']==selected_player) & (bowling_df['season']==selected_season)]['match_id'].count()
    st.metric('Matches Played', matches_played)
  with col2:
    # Total Wickets
    total_wickets = bowling_df[(bowling_df['bowler']==selected_player) & (bowling_df['season']==selected_season)]['is_wicket'].sum()
    st.metric('Total Wickets', total_wickets)
  with col3:
    # Total runs given
    total_runs_given = bowling_df[(bowling_df['bowler']==selected_player) & (bowling_df['season']==selected_season)]['total_runs'].sum()
    st.metric('Total Runs Given', total_runs_given)
  with col4:
    # Economy
    total_overs = bowling_df[(bowling_df['bowler']==selected_player) & (bowling_df['season']==selected_season)]['over'].sum()
    economy = round(total_runs_given / total_overs,2)
    st.metric('Economy', economy)
  with col5:
    # SR
    total_balls = bowling_df[(bowling_df['bowler']==selected_player) & (bowling_df['season']==selected_season)]['ball'].sum()
    SR = round(total_balls / total_wickets,2)
    st.metric('Strike Rate', SR)

  # Wickets per Season
  st.subheader(f'{selected_player} Wickets per Season')
  wicket_df = bowling_df.groupby(['season','bowler']).sum('is_wicket').reset_index()
  bowler_wicket = wicket_df[wicket_df['bowler']==selected_player]
  fig = px.line(bowler_wicket, x='season', y='is_wicket', labels={'is_wicket':'Wickets'})
  st.plotly_chart(fig, use_container_width=True)

  col1, col2 = st.columns(2)
  with col1:
    # Wicket against Team
    st.subheader(f'{selected_player} Wickets per Team in {selected_season}')
    delivery_df1 = pd.merge(delivery_df, match_filter1, left_on='match_id', right_on='id')
    wicket_per_team = delivery_df1[(delivery_df1['bowler']==selected_player) & (delivery_df1['season']==selected_season) & (delivery_df1['is_wicket'])]['batting_team'].value_counts().reset_index()
    wicket_per_team.rename(columns={'batting_team':'Batting Team', 'count':'Wickets'}, inplace=True)
    st.table(wicket_per_team)
  with col2:
    st.subheader(f'{selected_player} Wickets Type in {selected_season}')
    dismissal_type = delivery_df1[(delivery_df1['bowler']==selected_player) & (delivery_df1['season']==selected_season) & (delivery_df1['is_wicket'])]['dismissal_kind'].value_counts().reset_index()
    dismissal_type.rename(columns={'dismissal_kind':'Wicket Type', 'count':'Wickets'}, inplace=True)
    st.table(dismissal_type)

