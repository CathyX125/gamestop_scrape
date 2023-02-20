import math
import pandas as pd
import csv
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.offline as py
import plotly.graph_objs as go 
from collections import defaultdict, OrderedDict
import datetime
import plotly.offline as of
import plotly.express as px
import os

def str_to_set(x):
    return frozenset(x.replace('\'','').replace('[','').replace(']','').split(', '))

# read data

current_path = os.getcwd()
file_name = 'scraped_data.csv'
data = pd.read_csv(current_path+'/'+file_name, header=None, names=['id', 'name', 'release_date', 'score', 'platform', 'platform_all', 'developer', 'publisher', 'genres'])
data = data.drop_duplicates()
data = data.sort_values(by=['id'])
data = data[(data['publisher'] != '[]') | (data['developer'] != '[]')]
data = data[(data['genres'] != '[]')]

# clean date
data['release_date'] = pd.to_datetime(data['release_date'], errors='coerce').dt.to_period('m')
data = data[~data.isna().any(axis=1)]

# clean score
data["score"] = pd.to_numeric(data["score"])

# clean platform
platform_abbr = {
    "AND": "Android",
    "IOS": "iOS",
    "iOS (iPhone/iPad)": "iOS",
    "PS": "PlayStation",
    "PS2": "PlayStation 2",
    "PS3": "PlayStation 3",
    "PS4": "PlayStation 4",
    "XBOX": "Xbox",
    "X360": "Xbox 360",
    "XONE": "Xbox One",
    "SNES": "Super Nintendo",
    "GC": "GameCube",
    "N64": "Nintendo 64",
    "WII": "Wii",
    "WIIU": "Wii U",
    "NS": "Nintendo Switch",
    "GBA": "Game Boy Advance",
    "VITA": "PlayStation Vita",
    "MOBI": "Mobile",
    "MAC": "Macintosh",
    "LNX": "Linux",
    "DC": "Dreamcast",
    "NGE": "N-Gage",
    "WEB": "Online/Browser"
}

def clean_plat(s):
    x = set(str_to_set(s))
    for key, value in platform_abbr.items():
        if key in x:
            x.remove(key)
            x.add(value)
    return frozenset(x)

data['platform'] = data['platform'].map(clean_plat)
data['platform_all'] = data['platform_all'].map(clean_plat)

# clean developer
data['developer'] = data['developer'].map(str_to_set)

# clean publisher
data['publisher'] = data['publisher'].map(str_to_set)

# clean genres
data['genres'] = data['genres'].map(str_to_set)

platforms = set()
for x in data['platform']:
    platforms = platforms.union(x)

genres = set()
for x in data['genres']:
    genres = genres.union(x)


year2001_to_date = pd.Period(datetime.date(2001, 1, 1), freq="M")
year2001_to_date_data = data[data['release_date'] > year2001_to_date]



platform_gp = {
    "Android": "Mobile",
    "iOS": "Mobile",
    "Amazon Fire TV": "Mobile",
    "BlackBerry": "Mobile",
    "Windows Mobile": "Mobile",
    "Macintosh": "PC",
    "NEC PC88": "PC",
    "NEC PC98": "PC",
    "Linux": "PC"
}

def group_plat(s):
    x = set(s)
    for key, value in platform_gp.items():
        if key in x:
            x.remove(key)
            x.add(value)
    return frozenset(x)

year2001_to_date_data['platform_all'] = year2001_to_date_data['platform_all'].map(group_plat)
year_platform_data = year2001_to_date_data[['name', 'release_date', 'platform_all']].drop_duplicates().sort_values(by = ['release_date'])

platforms = set()
for x in year_platform_data['platform_all']:
    platforms = platforms.union(x)

platform_years = {
    "PlayStation": (1995, 2001),
    "PlayStation 2": (2000, 2007),
    "PlayStation 3": (2006, 2014),
    "PlayStation 4": (2013, 2020),
    "PlayStation 5": (2020, 2020),
    "PlayStation Vita": (2011, 2018),
    "PSP": (2004, 2012),
    "Xbox": (2001, 2007),
    "Xbox 360": (2006, 2014),
    "Xbox One": (2013, 2020),
    "Xbox Series X": (2020, 2020),
    "NES": (1985, 1995),
    "Super Nintendo": (1990, 1997),
    "Nintendo 64": (1996, 2002),
    "GameCube": (2001, 2007),
    "Wii": (2006, 2013),
    "Wii U": (2012, 2017),
    "Nintendo Switch": (2017, 2020),
    "GB": (1989, 2003),
    "Game Boy Color": (1989, 2003),
    "Game Boy Advance": (2001, 2010),
    "DS": (2004, 2013),
    "3DS": (2011, 2020),
    "Saturn": (1994, 2000),
    "Mobile": (2007, 2020),
    "PC": (1980, 2020),
    "N-Gage": (2003, 2005),
    "Stadia": (2019, 2020)
}

# year-platform dict
year_platform_dict = defaultdict(int)
remaster_platform_dict = defaultdict(int)

for index, row in year_platform_data.iterrows():
    year = int(row['release_date'].year)
    for platform in row['platform_all']:
        if platform not in platform_years.keys():
            year_platform_dict[year, 'others'] += 1
        else:
            if platform_years[platform][0] <= year <= platform_years[platform][1]:
                year_platform_dict[year, platform] += 1
            else:
                remaster_platform_dict[year, platform] += 1


# platform-publisher dict
pc_publisher_count = defaultdict(int)
ps_publisher_count = defaultdict(int)
xb_publisher_count = defaultdict(int)
ni_publisher_count = defaultdict(int)

pc_publisher_score = defaultdict(float)
ps_publisher_score = defaultdict(float)
xb_publisher_score = defaultdict(float)
ni_publisher_score = defaultdict(float)

platform_gp2 = {
    "PlayStation": "PlayStation",
    "PlayStation 2": "PlayStation",
    "PlayStation 3": "PlayStation",
    "PlayStation 4": "PlayStation",
    "PlayStation 5": "PlayStation",
    "Xbox": "Xbox",
    "Xbox 360": "Xbox",
    "Xbox One": "Xbox",
    "Xbox Series X": "Xbox",
    "NES": "Nintendo",
    "Super Nintendo": "Nintendo",
    "Nintendo 64": "Nintendo",
    "GameCube": "Nintendo",
    "Wii": "Nintendo",
    "Wii U": "Nintendo",
    "Nintendo Switch": "Nintendo",
    "PC": "PC",
    "Online/Browser": "PC"
}

def group_plat2(s):
    x = set()
    for key, value in platform_gp2.items():
        if key in s:
            x.add(value)
    return frozenset(x)

year2001_to_date_data['platform_all'] = year2001_to_date_data['platform_all'].map(group_plat2)
publisher_plat = year2001_to_date_data[['name', 'platform_all', 'publisher','score']].drop_duplicates()

publisher_gp = {
    "EA Sports": "Electronic Arts",
    "EA Games": "Electronic Arts",
    "EA Sports Big": "Electronic Arts",
    "SCEA": "Sony",
    "SCEE": "Sony",
    "SCEI": "Sony"
}

def group_pub(s):
    x = set(s)
    for key, value in publisher_gp.items():
        if key in x:
            x.remove(key)
            x.add(value)
    return frozenset(x)

publisher_plat['publisher'] = publisher_plat['publisher'].map(group_pub)

for index, row in publisher_plat.iterrows():
    if "PC" in row['platform_all']:
        for pub in row['publisher']:
            pc_publisher_count[pub] += 1
            pc_publisher_score[pub] += row['score']
    if "PlayStation" in row['platform_all']:
        for pub in row['publisher']:
            ps_publisher_count[pub] += 1
            ps_publisher_score[pub] += row['score']
    if "Xbox" in row['platform_all']:
        for pub in row['publisher']:
            xb_publisher_count[pub] += 1
            xb_publisher_score[pub] += row['score']
    if "Nintendo" in row['platform_all']:
        for pub in row['publisher']:
            ni_publisher_count[pub] += 1
            ni_publisher_score[pub] += row['score']

pc_publisher_count_sorted = OrderedDict(sorted(pc_publisher_count.items(), key=lambda x: x[1], reverse=True))
ps_publisher_count_sorted = OrderedDict(sorted(ps_publisher_count.items(), key=lambda x: x[1], reverse=True))
xb_publisher_count_sorted = OrderedDict(sorted(xb_publisher_count.items(), key=lambda x: x[1], reverse=True))
ni_publisher_count_sorted = OrderedDict(sorted(ni_publisher_count.items(), key=lambda x: x[1], reverse=True))


publisher_score = defaultdict(list)
for index, row in publisher_plat.iterrows():
    for pub in row['publisher']:
        publisher_score[pub].append(row['score'])

publisher_score_avg = {}
for key, value in publisher_score.items():
    if len(value) > 5:
        publisher_score_avg[key] = sum(value)/len(value)

top_publishers = {
    'Sony',
    'Microsoft Game Studios',
    'Nintendo',
    'ak tronic',
    'Electronic Arts',
    'Ubisoft',
    'THQ',
    'Capcom',
    'Activision',
    'Blizzard Entertainment',
    'Take-Two Interactive',
    'Square Enix',
    'Konami',
    'Bandai Namco Games',
    'Sega'
}
top_publishers_score_avg = {key: publisher_score_avg[key] for key in top_publishers}
top_publishers_score_avg = OrderedDict(sorted(top_publishers_score_avg.items(), key=lambda x: x[1], reverse=True))



# genre_score dict
genre_gp = {
    'Pinball': "Sports",
    'Open-World': "Open-World",
    'MMO': "MMO",
    'Puzzle': "Puzzle",
    'Hidden Object': "Puzzle",
    'Baseball': "Sports",
    'Tactical': "Tactical",
    'Boxing': "Sports",
    'Trivia/Board Game': "Trivia/Board Game",
    'Basketball': "Sports",
    'Party/Minigame': "Party/Minigame",
    '"Shoot-Em-Up"': "Shooter",
    'Roguelike': "Roguelike",
    'Flight': "Flight",
    'Light-Gun': "Shooter",
    'Strategy': "Strategy",
    'VR': "VR",
    'Simulation': "Simulation",
    'Card Game': "Card Game",
    'Football (American)': "Sports",
    'Tennis': "Sports",
    'Wakeboarding/Surfing': "Sports",
    'Soccer': "Sports",
    'Action': "Action",
    'Skateboarding/Skating': "Sports",
    'Hunting/Fishing': "Simulation",
    'Compilation': "Compilation",
    'Fighting': "Fighting",
    'Management': "Management",
    'Role-Playing': "Role-Playing",
    'Platformer': "Platformer",
    'Fitness': "Fitness",
    'Snowboarding/Skiing': "Sports",
    'Edutainment': "Edutainment",
    'Matching/Stacking': "",
    '"Beat-Em-Up"': "Fighting",
    'Driving/Racing': "Driving/Racing",
    'Music/Rhythm': "Music/Rhythm",
    'Survival': "Survival",
    'Hockey': "Sports",
    'Gambling': "Gambling",
    'Sports': "Sports",
    'MOBA': "MOBA",
    'Bowling': "Sports",
    'Adventure': "Adventure",
    'Shooter': "Shooter",
    'Golf': "Sports",
    'Wrestling': "Sports",
    'Billiards': "Sports"
}
def group_genre(s):
    x = []
    for key, value in genre_gp.items():
        if key in s:
            x.append(value)
    return x
genre_score_data = year2001_to_date_data[['name', 'score', 'genres']].drop_duplicates().sort_values(by=['name'])
genre_score_data['genres'] = genre_score_data['genres'].map(group_genre)

genres_count = defaultdict(int)
for genres in genre_score_data['genres']:
    for x in genres:
        if x != '':
            genres_count[x] += 1

genres_count_data = pd.DataFrame.from_dict(genres_count, orient = 'index', columns = ['count'])
genres_score_count = defaultdict(lambda: [0,0,0,0,0,0,0,0,0,0])
for _, row in genre_score_data.iterrows():
    for x in row['genres']:
        if x == '':
            continue
        s = int(math.floor(row['score']))
        genres_score_count[x][s-1] += 1

genres_score_percent = {}
for key, value in genres_score_count.items():
    genres_score_percent[key] = [x/sum(value)*100 for x in value]

genres_score_percent_sorted = OrderedDict(sorted(genres_score_percent.items(), key=lambda x: x[1][-2]))



# draw genres heatmap
layout = go.Layout(
    font=dict(size=10)
)
fig = go.Figure(data=go.Heatmap(
    z=list(genres_score_percent_sorted.values()),
    y=list(genres_score_percent_sorted.keys()),
    x=['below 2', '2-3', '3-4', '4-5', '5-6', '6-7', '7-8', '8-9', '9-10', '10'],
    colorscale= [
        [0, 'rgb(3, 18, 41)'],
        [1./1000, 'rgb(92, 47, 96)'],
        [1./100, 'rgb(197, 69, 104)'],
        [1./10, 'rgb(255, 135, 66)'],
        [1., 'rgb(255, 233, 0)'],
    ],
))

fig.show()

# draw platform vs. year
year_platform_DF = pd.DataFrame.from_dict(year_platform_dict, orient = 'index', columns = ['count'])
year_platform_DF.index = pd.MultiIndex.from_tuples(year_platform_DF.index, names = ['year', 'platform']) 
year_platform_DF['sum'] = year_platform_DF.groupby('year')['count'].transform('sum')
year_platform_DF['percentage'] = year_platform_DF['count']/year_platform_DF['sum']*100
year_platform_DF = year_platform_DF.reset_index()

traces = []
color = {'PC': 'rgb(156, 153, 9)',
    'PlayStation': 'rgb(0, 50, 130)',
    'PlayStation 2': 'rgb(18, 82, 184)',
    'PlayStation 3': 'rgb(38, 103, 209)',
    'PlayStation 4': 'rgb(36, 120, 255)',
    'PlayStation 5': 'rgb(85, 148, 250)',
    'Xbox': 'rgb(65, 128, 13)',
    'Xbox 360': 'rgb(20, 163, 29)',
    'Xbox One': 'rgb(43, 204, 54)',
    'Xbox Series X': 'rgb(77, 255, 88)',
    'Nintendo 64': 'rgb(107, 3, 3)',
    'GameCube': 'rgb(140, 9, 9)',
    'Wii': 'rgb(176, 15, 15)',
    'Wii U':'rgb(214, 21, 21)',
    'Nintendo Switch': 'rgb(255, 28, 28)',
    'Game Boy Color': 'rgb(153, 63, 8)',
    'Game Boy Advance': 'rgb(184, 86, 26)',
    'DS': 'rgb(219, 112, 46)',
    '3DS':'rgb(225, 128, 48)',
    'PSP': 'rgb(28, 141, 201)',
    'PlayStation Vita': 'rgb(60, 183, 250)',
    'N-Gage': 'rgb(107, 15, 104)',
    'Mobile': 'rgb(163, 62, 160)',
    'Stadia': 'rgb(97, 212, 195)',
    'others': 'rgb(204, 204, 255)'
}
plot_order = ['PC', 'PlayStation', 'PlayStation 2', 'PlayStation 3', 'PlayStation 4', 'PlayStation 5',
              'Xbox', 'Xbox 360', 'Xbox One', 'Xbox Series X', 'Nintendo 64', 'GameCube', 'Wii', 'Wii U', 'Nintendo Switch',
              'Game Boy Color', 'Game Boy Advance', 'DS', '3DS', 'PSP', 'PlayStation Vita',
              'N-Gage', 'Mobile', 'Stadia', 'others']
for plat in plot_order:
    trace = go.Bar(
        x = year_platform_DF[year_platform_DF['platform'] == plat]['year'],
        y = year_platform_DF[year_platform_DF['platform'] == plat]['percentage'],
        name = plat,
        marker_color = color[plat]
    )
    traces.append(trace)

layout = go.Layout(
    barmode = 'stack',
    font=dict(size=10), xaxis=dict(title='Year'),
    yaxis=dict(title='Percentage of Each Platform per Year (%)')
)

fig = go.Figure(data = traces, layout = layout)
fig.update_layout(xaxis = dict(tickmode = 'linear', tick0 = 2001, dtick = 1))
fig.write_image(current_path +'/platform.svg')
fig.show()



# platform vs publisher
# ps data
ps_publisher_data = pd.DataFrame.from_dict(ps_publisher_count_sorted, orient = 'index', columns = ['count']).reset_index()
ps_publisher_data['percentage'] = 100 * ps_publisher_data['count']/ps_publisher_data['count'].sum()
ps_publisher_data = ps_publisher_data.iloc[0:5,[0, 2]].round(2)
ps_publisher_data['platform'] = 'PlayStation Series'
# pc data
pc_publisher_data = pd.DataFrame.from_dict(pc_publisher_count_sorted, orient = 'index', columns = ['count']).reset_index()
pc_publisher_data['percentage'] = 100 * pc_publisher_data['count']/pc_publisher_data['count'].sum()
pc_publisher_data = pc_publisher_data.iloc[0:5,[0, 2]].round(2)
pc_publisher_data['platform'] = 'PC'
# ni data
ni_publisher_data = pd.DataFrame.from_dict(ni_publisher_count_sorted, orient = 'index', columns = ['count']).reset_index()
ni_publisher_data['percentage'] = 100 * ni_publisher_data['count']/ni_publisher_data['count'].sum()
ni_publisher_data = ni_publisher_data.iloc[0:5,[0, 2]].round(2)
ni_publisher_data['platform'] = 'Nintendo Series'
# xb data
xb_publisher_data = pd.DataFrame.from_dict(xb_publisher_count_sorted, orient = 'index', columns = ['count']).reset_index()
xb_publisher_data['percentage'] = 100 * xb_publisher_data['count']/xb_publisher_data['count'].sum()
xb_publisher_data = xb_publisher_data.iloc[0:5,[0, 2]].round(2)
xb_publisher_data['platform'] = 'Xbox Series'
publisher_data = pd.concat([ps_publisher_data, pc_publisher_data, ni_publisher_data, xb_publisher_data]).round(2)
print(ps_publisher_data['index'].unique())
traces = []

color_p = {'Electronic Arts': 'rgb(205, 92, 92)',
            'Ubisoft': "rgb(69,179,157)", 
            'Activision': 'rgb(244, 208, 63)', 
            'Sony': 'rgb(189, 195, 199)',
            'Microsoft Game Studios': 'rgb(127, 140, 141)', 
            'ak tronic': 'rgb(160, 50, 38)', 
            'Nintendo': 'rgb(136, 78, 160)', 
            'Sega': 'rgb(17, 122, 101)', 
            'THQ': 'rgb(175, 96, 26)',
            'Capcom': 'rgb(255, 204, 102)'
}

trace1 = go.Bar(x=ps_publisher_data['index'].unique(), 
                y=ps_publisher_data['percentage'].round(2), 
                marker_color=[color_p[x] for x in ps_publisher_data['index'].unique()],
                text=ps_publisher_data['percentage'],
                textposition='auto')

layout = go.Layout(
    bargap = 0,
    title_text='PlayStation Series',
    yaxis=dict(title='Percentage of Each Publisher in a platform (%)')
)
fig = go.Figure(data = trace1, layout = layout)
fig.update_layout(yaxis = dict(tickmode = 'linear', range=[0,8], tick0 = 0, dtick = 4))
fig.write_image(current_path + '/PS.svg')
fig.show()

trace2 = go.Bar(x=pc_publisher_data['index'].unique(), 
                y=pc_publisher_data['percentage'].round(2), 
                marker_color=[color_p[x] for x in pc_publisher_data['index'].unique()],
                text=pc_publisher_data['percentage'],
                textposition='auto')

layout = go.Layout(
    bargap = 0,
    title_text='PC',
    yaxis=dict(title='Percentage of Each Publisher in a platform (%)')
)
fig = go.Figure(data = trace2, layout = layout)
fig.update_layout(yaxis = dict(tickmode = 'linear', range=[0,8], tick0 = 0, dtick = 4))
fig.write_image(current_path + '/PC.svg')
fig.show()

trace3 = go.Bar(x=ni_publisher_data['index'].unique(), 
                y=ni_publisher_data['percentage'].round(2), 
                marker_color=[color_p[x] for x in ni_publisher_data['index'].unique()],
                text=ni_publisher_data['percentage'],
                textposition='auto')

layout = go.Layout(
    bargap = 0,
    title_text='Nintendo Series',
    yaxis=dict(title='Percentage of Each Publisher in a platform (%)')
)
fig = go.Figure(data = trace3, layout = layout)
fig.update_layout(yaxis = dict(tickmode = 'linear', range=[0,8], tick0 = 0, dtick = 4))
fig.write_image(current_path + '/ni.svg')
fig.show()

trace4 = go.Bar(x=xb_publisher_data['index'].unique(), 
                y=xb_publisher_data['percentage'].round(2), 
                marker_color=[color_p[x] for x in xb_publisher_data['index'].unique()],
                text=xb_publisher_data['percentage'],
                textposition='auto')

layout = go.Layout(
    bargap = 0,
    title_text='Xbox Series',
    yaxis=dict(title='Percentage of Each Publisher in a platform (%)')
)
fig = go.Figure(data = trace4, layout = layout)
fig.update_layout(yaxis = dict(tickmode = 'linear', range=[0,8], tick0 = 0, dtick = 4))
fig.write_image(current_path + '/xb.svg')
fig.show()
