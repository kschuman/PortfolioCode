from bokeh.io import show, output_file
from bokeh.layouts import column
from bokeh.models import (
    ColumnDataSource,
    HoverTool,
    LogColorMapper
)
from bokeh.palettes import Plasma as palette
from bokeh.palettes import Spectral as pal2
from bokeh.plotting import figure
import pandas as pd
from bokeh.transform import factor_cmap
import numpy as np

from bokeh.sampledata.us_counties import data as counties


#output_file = '../Graphics/bokeh1.html'
#output_file('../Graphics/bokeh1.html')

palette=palette[6]
palette.reverse()
color_mapper = LogColorMapper(palette=palette)


# County data
county_xs = [county["lons"] for county in counties.values()]
county_ys = [county["lats"] for county in counties.values()]
county_names = [county['name'] for county in counties.values()]
countiesdf = pd.DataFrame(counties).transpose()
countiesdf['state'] = countiesdf['state'].str.upper()
countiesdf['id'] = countiesdf[['name', 'state']].apply(lambda x: ' '.join(x), axis=1)

# Education data
edu = pd.read_csv('../Data/Education.csv', skiprows=4)
edu = edu[edu['State'] != 'PR']
edu = edu.dropna()
edu['Area name'] = edu['Area name'].apply(lambda x: x.split(' County')[0])
edu['id'] = edu[['Area name', 'State']].apply(lambda x: ' '.join(x), axis=1)
edu = edu.merge(countiesdf, how='left', on='id')
edu = edu.dropna()

data1 = "Percent of adults with a bachelor's degree or higher, 2011-2015"
data2 = 'Percent of adults with less than a high school diploma, 2011-2015'

#state = edu[edu['State'].isin(['NY', 'NJ', 'CT', 'PA', 'MA' ,'RI', 'NH', 'VT', 'ME', 'DE' ])]
states = edu[edu['State'] != 'HI']
#state = edu[edu['State'].isin(['MD'])]
d1 = list(states[data1])
d2 = list(states[data2])
lats = list(states['lats'])
lons = list(states['lons'])
names = list(states['name'])

source = ColumnDataSource(data=dict(
    x=lons,
    y=lats,
    name=names,
    rate=d1,
    rate2 = d2
))

TOOLS = "wheel_zoom,zoom_in,reset,hover,save"

p1 = figure(
    title="Percent of Adults with a Bachelor's Degree, 2015", tools=TOOLS,
    x_axis_location=None, y_axis_location=None, plot_width=1100, plot_height=700
)
p1.grid.grid_line_color = None

p1.patches('x', 'y', source=source,
          fill_color={'field': 'rate', 'transform': color_mapper},
          fill_alpha=0.7, line_color="white", line_width=0.1)

hover = p1.select_one(HoverTool)
hover.point_policy = "follow_mouse"
hover.tooltips = [
    ("County", "@name"),
    ("Bachelor Degree Rate", "@rate%"),
    ('No High School Degree Rate', "@rate2%")

]




source = ColumnDataSource(data=dict(
    x=lons,
    y=lats,
    name=names,
    rate=d1,
    rate2 = d2
))

TOOLS = "pan,wheel_zoom,reset,hover,save"

p2 = figure(
    title="Percent of Adults with No High School Diplmoa, 2015", tools=TOOLS,
    x_axis_location=None, y_axis_location=None, plot_width=1100, plot_height=700
)
p2.grid.grid_line_color = None

p2.patches('x', 'y', source=source,
          fill_color={'field': 'rate2', 'transform': color_mapper},
          fill_alpha=0.7, line_color="white", line_width=0.1)

hover = p2.select_one(HoverTool)
hover.point_policy = "follow_mouse"
hover.tooltips = [
    ("County", "@name"),
    ('No High School Degree Rate', "@rate2%"),
    ("Bachelor Degree Rate", "@rate%")
]

#show(p2)
p = column(p1, p2)

#show(p)





# Bokeh 2
output_file('../Graphics/bokeh2.html')

edu15cols = ['State', 'Area name' , '2013 Rural-urban Continuum Code', '2013 Urban Influence Code', 'Less than a high school diploma, 2011-2015',
       'High school diploma only, 2011-2015',
       "Some college or associate's degree, 2011-2015",
       "Bachelor's degree or higher, 2011-2015",
       'Percent of adults with less than a high school diploma, 2011-2015',
       'Percent of adults with a high school diploma only, 2011-2015',
       "Percent of adults completing some college or associate's degree, 2011-2015",
       "Percent of adults with a bachelor's degree or higher, 2011-2015"]


edu15 = edu[edu15cols]
edu15.columns = ['State', 'County' , 'RuralUrabnCode', 'UrbanInfCode', '<HS', 'HS', '<Bach', 'Bach', '<HS%', 'HS%', '<Bach%', 'Bach%']
for col in ['<HS', 'HS', '<Bach', 'Bach']:
    edu15[col] = edu15[col].str.replace(',', '')

regions = pd.read_csv('../Data/statesregions.txt')
edu15 = edu15.merge(regions, how='left', on='State')


TOOLS="hover,crosshair,pan,box_zoom,undo,redo,reset,save,box_select,poly_select"


col_map = {}
i=0
for region in edu15['Region'].unique():
    col_map[region] = pal2[10][i]
    i+=1

edu15['Color'] = edu15['Region'].map(col_map)


source2 = ColumnDataSource(data=dict(
    x=list(edu15['<HS%']),
    y=list(edu15['Bach%']),
    state=list(edu15['State']),
    color=list(edu15['Color']),
    name=list(edu15['County']),
    reg=list(edu15['Region']),
    #size=4
))

a = figure(tools = TOOLS, title='Education Levels Around the US, 2011 - 2015',
           x_axis_label='% Adults Without HS Diploma', y_axis_label="% Adults With Bachelor's Degree")
a.scatter(x='x', y='y', source=source2, fill_color='color', line_color='color', size=6, fill_alpha=.7)

hover = a.select_one(HoverTool)
hover.point_policy = "follow_mouse"
hover.tooltips = [
    ("Location", "@name, @state"),
    #("State", "@state"),
    ("Region","@reg"),
    ('No High School Degree Rate', "@x%"),
    ("Bachelor Degree Rate", "@y%")
]


show(a)

# Save rural
rural = edu[['FIPS Code', 'id', 'State', 'name', '2013 Rural-urban Continuum Code']].drop_duplicates()
rural.to_csv( '../Data/rural.csv')