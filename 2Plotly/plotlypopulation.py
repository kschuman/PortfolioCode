import plotly.plotly as py
import plotly.graph_objs as go
import pandas as pd

popfile = '../Data/population.txt'

countriesfile = '../Data/countrylist.csv'

# Combine country long and lats
pop = pd.read_csv(popfile)
countries = pd.read_csv(countriesfile)
pop = pop.merge(countries, left_on='Country.Code', right_on='Alpha-3 code', how='left')

#pop2012 = pop[pop['year'] == 2012]
#pop20 = pop[pop['year'].isin([2011, 2012, 2013])] # years 2011 - 2013


cases = []
colors = ['rgb(149, 216, 158)','rgb(107,174,214)','rgb(193, 48, 48)']
yrs = {2011:'2011',2012:'2012',2013:'2013'}
yrs2 = {2011: '1965', 2012: '1985', 2013: '2005'}


for i in range(2011,2014)[::-1]:
    cases.append(go.Scattergeo(
        lon = pop[ pop['year'] == int(yrs2[i]) ]['Longitude (average)'], #-(max(range(6,10))-i),
        lat = pop[ pop['year'] == int(yrs2[i]) ]['Latitude (average)'],
        text = pop[ pop['year'] == int(yrs2[i]) ]['population'],
        name = yrs2[i],
        marker = dict(
            size = pop[ pop['year'] == int(yrs2[i]) ]['population']/1000000,
            color = colors[i-2013],
            line = dict(width = 0),
            opacity=1
        ),
    ))

cases[0]['text'] = pop[ pop['year'] == 2005 ]['Country.Name'] + '<br>' \
                   + pop[ pop['year'] == 2005 ]['population'].map('{:,}'.format)\
                       .astype(str).apply(lambda x: x.strip('.0'))
cases[1]['text'] = pop[ pop['year'] == 1985 ]['population'].map('{:,}'.format)\
                       .astype(str).apply(lambda x: x.strip('.0'))
cases[2]['text'] = pop[ pop['year'] == 1965 ]['population'].map('{:,}'.format)\
                       .astype(str).apply(lambda x: x.strip('.0'))

#cases[0]['text'] = '{}\n{}'.format(pop[ pop['year'] == 2005 ]['population'], pop[ pop['year'] == 2005 ]['Country.Name'])

#cases[0]['text'] = pop[ pop['year'] == 1965 ]['Country.Name']
cases[0]['mode'] = 'markers+text'

cases[0]['textposition'] = 'bottom center'

inset_locs = ['Guinea', 'Sierra Leone', 'Liberia', 'Burkina Faso', "Cote d'Ivoire",
                     'Ghana', 'Togo', 'Benin', 'Nigeria', 'Cameroon', 'Equatorial Guinea',
                     'Sao Tome and Principe', 'Gabon']
inset_locs.sort()
afr = pop[ pop['Country.Name'].isin(inset_locs)]


inset = [
    go.Choropleth(
        locationmode = 'country names',
        locations = inset_locs,
        z = afr[afr['year'] == 2005]['population'],
        #text = 'X', #pop[ pop['year'] == 2005 ]['Country.Name'],
        colorscale = [[0,'rgb(0, 0, 0)'],[1,'rgb(0, 0, 0)']],
        autocolorscale = False,
        showscale = False,
        geo = 'geo2'
    ),
    go.Scattergeo(
        lon = [24.0936],
        lat = [15.1881],
        text = ['Africa'],
        mode = 'text',
        showlegend = False,
        geo = 'geo2'
    )
]

layout = go.Layout(
    title = 'Population, 1965 - 2005',
    geo = dict(
        resolution = 50,
        scope = 'africa',
        showframe = False,
        showcoastlines = True,
        showland = True,
        landcolor = "rgb(229, 229, 229)",
        countrycolor = "rgb(255, 255, 255)" ,
        coastlinecolor = "rgb(255, 255, 255)",
        projection = dict(
            type = 'Mercator'
        ),
        lonaxis = dict( range= [ -15.0, 15.0 ] ),
        lataxis = dict( range= [ -5.0, 14.0 ] ),
        domain = dict(
            x = [ 0, 1 ],
            y = [ 0, 1 ]
        )
    ),
    geo2 = dict(
        scope = 'africa',
        showframe = False,
        showland = True,
        landcolor = "rgb(229, 229, 229)",
        showcountries = False,
        domain = dict(
            x = [ 0, 0.4 ],
            y = [ 0, 0.4 ]
        ),
        bgcolor = 'rgba(255, 255, 255, 0.0)',
    ),
    legend = dict(
           traceorder = 'reversed'
    )
)

fig = go.Figure(layout=layout, data=cases+inset)
py.iplot(fig, validate=False, filename='Population65-05')





