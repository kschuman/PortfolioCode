import plotly.plotly as py
import plotly.graph_objs as go
import pandas as pd
import math
import sklearn.preprocessing

popfile = '../Data/population.txt'
countriesfile = '../Data/countrylist.csv'
incomefile = '../Data/countryincome.txt'

# Combine country long and lats
pop = pd.read_csv(popfile)
countries = pd.read_csv(countriesfile)
incomes = pd.read_csv(incomefile, sep='\t')
countries = countries.merge(incomes, left_on='Alpha-3 code', right_on='Country Code', how='left')
pop = pop.merge(countries, left_on='Country.Code', right_on='Alpha-3 code', how='left')
pop = pop.rename(columns = {'Country_x': 'Country', 'Latitude (average)': 'lat',
                            'Longitude (average)': 'long', 'IncomeGroup': 'income'})


def calculate_initial_compass_bearing(pointA, pointB):
    """
    From: https://gist.github.com/jeromer/2005586

    Calculates the bearing between two points.
    The formulae used is the following:
        θ = atan2(sin(Δlong).cos(lat2),
                  cos(lat1).sin(lat2) − sin(lat1).cos(lat2).cos(Δlong))
    :Parameters:
      - `pointA: The tuple representing the latitude/longitude for the
        first point. Latitude and longitude must be in decimal degrees
      - `pointB: The tuple representing the latitude/longitude for the
        second point. Latitude and longitude must be in decimal degrees
    :Returns:
      The bearing in degrees
    :Returns Type:
      float
    """
    if (type(pointA) != tuple) or (type(pointB) != tuple):
        raise TypeError("Only tuples are supported as arguments")

    lat1 = math.radians(pointA[0])
    lat2 = math.radians(pointB[0])

    diffLong = math.radians(pointB[1] - pointA[1])

    x = math.sin(diffLong) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1)
            * math.cos(lat2) * math.cos(diffLong))

    initial_bearing = math.atan2(x, y)

    # Now we have the initial bearing but math.atan2 return values
    # from -180° to + 180° which is not what we want for a compass bearing
    # The solution is to normalize the initial bearing as shown below
    initial_bearing = math.degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360

    return compass_bearing


def get_compass_val(row):
    pointA = (0, 0)
    pointB = (row['lat'], row['long'])
    cmp = calculate_initial_compass_bearing(pointA, pointB)
    return cmp


# Look at 2012 Only
cols = ['Country.Code', 'Country.Name', 'year', 'population', 'Country',
        'Alpha-3 code', 'Numeric code', 'lat', 'long', 'Region', 'income']
pop12 = pop[pop['year'] == 2012][cols].dropna()
dirs = ['NNW', 'NW', 'WNW', 'WSW', 'SW', 'SSW', 'SSE', 'SE', 'ESE', 'ENE', 'NE', 'NNE']

# Add cardinal direction
pop12['compass'] = pop.apply(lambda row: get_compass_val(row), axis=1)


labels = ['North', 'NE', 'East', 'SE', 'South', 'SW', 'West', 'NW', 'North2']
bins = [0,22.5, 67.5, 112.5, 157.5, 202.5, 247.5, 292.5, 337.5, 360]

pop12['card'] = pd.cut(pop12['compass'], bins=bins, labels=labels)
pop12 = pop12.replace('North2', 'North')

cardinal_pops = pd.DataFrame({'direction': dirs})

sums = pop12.groupby(['income', 'card'])['population'].sum().reset_index()
sums = sums.drop(22)

min_max = sklearn.preprocessing.MinMaxScaler()
X = sums['population']
X = X.values.reshape(-1, 1)
sums['popscaled'] = min_max.fit_transform(X)

sums['poppercent'] = sums['population']/(7128176935)

trace1 = go.Area(
    r=list(sums[sums['income'] == 'High income']['poppercent']),
    t=list(sums[sums['income'] == 'High income']['card']),
    name='High Income',
    marker=dict(
        color='#F79D84'
    )
)
trace2 = go.Area(
    r=list(sums[sums['income'] == 'Upper middle income']['poppercent']),
    t=list(sums[sums['income'] == 'Upper middle income']['card']),
    name='Upper Middle Income',
    marker=dict(
        color='#6184D8'
    )
)
trace3 = go.Area(
    r=list(sums[sums['income'] == 'Lower middle income']['poppercent']),
    t=list(sums[sums['income'] == 'Lower middle income']['card']),
    name='Lower Middle Income',
    marker=dict(
        color='rgb(203,201,226)'
    )
)
trace4 = go.Area(
    r=list(sums[sums['income'] == 'Low income']['poppercent']),
    t=list(sums[sums['income'] == 'Low income']['card']),
    name='Lower Income',
    marker=dict(
        color='#50C5B7'
    )
)
data = [trace1, trace2, trace3, trace4]
layout = go.Layout(
    title='World Population Distribution by Direction and Income, 2012',
    font=dict(
        size=16
    ),
    legend=dict(
        font=dict(
            size=16
        )
    ),
    radialaxis=dict(
        ticksuffix='%'
    ),
    orientation=270
)
fig = go.Figure(data=data, layout=layout)
py.iplot(fig, filename='PopulationIncomeCircle')


# Try another for 1992
cols = ['Country.Code', 'Country.Name', 'year', 'population', 'Country',
        'Alpha-3 code', 'Numeric code', 'lat', 'long', 'Region', 'income']
pop12 = pop[pop['year'] == 1992][cols].dropna()
dirs = ['NNW', 'NW', 'WNW', 'WSW', 'SW', 'SSW', 'SSE', 'SE', 'ESE', 'ENE', 'NE', 'NNE']

# Add cardinal direction
pop12['compass'] = pop.apply(lambda row: get_compass_val(row), axis=1)

labels = ['North', 'NE', 'East', 'SE', 'South', 'SW', 'West', 'NW', 'North2']
bins = [0,22.5, 67.5, 112.5, 157.5, 202.5, 247.5, 292.5, 337.5, 360]

pop12['card'] = pd.cut(pop12['compass'], bins=bins, labels=labels)
pop12 = pop12.replace('North2', 'North')



cardinal_pops = pd.DataFrame({'direction': dirs})

sums = pop12.groupby(['income', 'card'])['population'].sum().reset_index()
sums = sums.drop(22)

min_max = sklearn.preprocessing.MinMaxScaler()
X = sums['population']
X = X.values.reshape(-1, 1)
sums['popscaled'] = min_max.fit_transform(X)

sums['poppercent'] = sums['population']/(5504401149)

trace1 = go.Area(
    r=list(sums[sums['income'] == 'High income']['poppercent']),
    t=list(sums[sums['income'] == 'High income']['card']),
    name='High Income',
    marker=dict(
        color='#F79D84'
    )
)
trace2 = go.Area(
    r=list(sums[sums['income'] == 'Upper middle income']['poppercent']),
    t=list(sums[sums['income'] == 'Upper middle income']['card']),
    name='Upper Middle Income',
    marker=dict(
        color='#6184D8'
    )
)
trace3 = go.Area(
    r=list(sums[sums['income'] == 'Lower middle income']['poppercent']),
    t=list(sums[sums['income'] == 'Lower middle income']['card']),
    name='Lower Middle Income',
    marker=dict(
        color='rgb(203,201,226)'
    )
)
trace4 = go.Area(
    r=list(sums[sums['income'] == 'Low income']['poppercent']),
    t=list(sums[sums['income'] == 'Low income']['card']),
    name='Lower Income',
    marker=dict(
        color='#50C5B7'
    )
)
data = [trace1, trace2, trace3, trace4]
layout = go.Layout(
    title='World Population Distribution by Direction and Income, 1992',
    font=dict(
        size=16
    ),
    legend=dict(
        font=dict(
            size=16
        )
    ),
    radialaxis=dict(
        ticksuffix='%'
    ),
    orientation=270
)
fig = go.Figure(data=data, layout=layout)
py.iplot(fig, filename='PopulationIncomeCircle2')



# Try another for 1972
cols = ['Country.Code', 'Country.Name', 'year', 'population', 'Country',
        'Alpha-3 code', 'Numeric code', 'lat', 'long', 'Region', 'income']
pop12 = pop[pop['year'] == 1972][cols].dropna()
dirs = ['NNW', 'NW', 'WNW', 'WSW', 'SW', 'SSW', 'SSE', 'SE', 'ESE', 'ENE', 'NE', 'NNE']

# Add cardinal direction
pop12['compass'] = pop.apply(lambda row: get_compass_val(row), axis=1)

labels = ['North', 'NE', 'East', 'SE', 'South', 'SW', 'West', 'NW', 'North2']
bins = [0,22.5, 67.5, 112.5, 157.5, 202.5, 247.5, 292.5, 337.5, 360]

pop12['card'] = pd.cut(pop12['compass'], bins=bins, labels=labels)
pop12 = pop12.replace('North2', 'North')


cardinal_pops = pd.DataFrame({'direction': dirs})

sums = pop12.groupby(['income', 'card'])['population'].sum().reset_index()
sums = sums.drop(22)

min_max = sklearn.preprocessing.MinMaxScaler()
X = sums['population']
X = X.values.reshape(-1, 1)
sums['popscaled'] = min_max.fit_transform(X)

sums['poppercent'] = sums['population']/(3851545181)

trace1 = go.Area(
    r=list(sums[sums['income'] == 'High income']['poppercent']),
    t=list(sums[sums['income'] == 'High income']['card']),
    name='High Income',
    marker=dict(
        color='#F79D84'
    )
)
trace2 = go.Area(
    r=list(sums[sums['income'] == 'Upper middle income']['poppercent']),
    t=list(sums[sums['income'] == 'Upper middle income']['card']),
    name='Upper Middle Income',
    marker=dict(
        color='#6184D8'
    )
)
trace3 = go.Area(
    r=list(sums[sums['income'] == 'Lower middle income']['poppercent']),
    t=list(sums[sums['income'] == 'Lower middle income']['card']),
    name='Lower Middle Income',
    marker=dict(
        color='rgb(203,201,226)'
    )
)
trace4 = go.Area(
    r=list(sums[sums['income'] == 'Low income']['poppercent']),
    t=list(sums[sums['income'] == 'Low income']['card']),
    name='Lower Income',
    marker=dict(
        color='#50C5B7'
    )
)
data = [trace1, trace2, trace3, trace4]
layout = go.Layout(
    title='World Population Distribution by Direction and Income, 1972',
    font=dict(
        size=16
    ),
    legend=dict(
        font=dict(
            size=16
        )
    ),
    radialaxis=dict(
        ticksuffix='%'
    ),
    orientation=270
)
fig = go.Figure(data=data, layout=layout)
py.iplot(fig, filename='PopulationIncomeCircle3')