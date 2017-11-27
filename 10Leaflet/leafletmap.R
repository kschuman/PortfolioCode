# LeafletMapsExample.R
#Gates

##########################################################################
##This code works well and creates an interactive layered leaflet/R map
## The map is choropleth and markered
##
## Required datasets are here:
##    CancerCountyFIPS.csv
##    CancerCountyFIPS_Breast.csv
##    LandUseDatasetREALLatlong.csv
## AND ##
############
# Download county shape file.
## !! This is important. Shape files can be found here
#https://www.census.gov/geo/maps-data/data/cbf/cbf_counties.html
#us.map <- tigris::counties(cb = TRUE, year = 2015)
#OR
# Download county shape file from Tiger.
# https://www.census.gov/geo/maps-data/data/cbf/cbf_counties.html
# I downloaded the zip and placed all files in the zip into my RStudio folder
##us.map <- readOGR(dsn = ".", layer = "cb_2016_us_county_20m", stringsAsFactors = FALSE)
#head(us.map)
###############
##Not all of these libraries are required for this code, but
## they are good for more generalized goals
############################################################################

library(leaflet)
library(sp)
library(mapproj)
library(maps)
library(mapdata)
library(maptools)
library(htmlwidgets)
library(magrittr)
library(XML)
library(plyr)
library(rgdal)
library(WDI)
library(raster)
library(noncensus)
library(stringr)
library(tidyr)
library(tigris)
library(rgeos)
library(ggplot2)
library(scales)

data(zip_codes)
data(counties)

################################################################
##https://www.statecancerprofiles.cancer.gov/incidencerates/index.php?stateFIPS=99&cancer=001&race=07&sex=0&age=001&type=incd&sortVariableName=rate&sortOrder=default#results
CancerRates <- read.csv('Data/CancerCountyFIPS.csv')
#head(CancerRates)
CancerRatesB <- read.csv('Data/CancerCountyFIPS_Breast.csv')
#head(CancerRatesB)
LandUse <- read.csv('Data/LandUseDatasetREALLatlong.csv')

rural <- read.csv('Data/rural.csv')


resevoirs <- read.csv('Data/resevoirs.txt', sep='\t', header=T, row.names=NULL)
resevoirs$lng <- -resevoirs$lng

buildings <- read.csv('Data/largefactories.txt', sep='\t', header=T, row.names=NULL)
buildings$lng <- -buildings$lng

#head(LandUse)
## Not using this dataset yet...
#PowerPlants <- read.csv("PowerPlants.csv")
#head(PowerPlants)

## Make all the column names lowercase
names(CancerRates) <- tolower(names(CancerRates))
#head(CancerRates)

# Rename columns to make for a clean df merge later.
##GEOID is the same as FIPS
colnames(CancerRates) <- c("location", "GEOID", "rate")
#head(CancerRates)
colnames(CancerRatesB) <- c("location", "GEOID", "rate")
#head(CancerRatesB)
colnames(LandUse) <- c("offset", "lat", "lng", "url", "name")
#head(LandUse)
colnames(rural) <- c('id', 'GEOID', 'countystate', 'state', 'county', 'urbanscore')

head(CancerRates)
##Add leading zeos to any FIPS code that's less than 5 digits long to get a good match.
##formatC is from C code formatting - creates a 5 digit int
CancerRates$GEOID <- formatC(CancerRates$GEOID, width = 5, format = "d", flag = "0")
#head(CancerRates)
CancerRatesB$GEOID <- formatC(CancerRatesB$GEOID, width = 5, format = "d", flag = "0")
head(CancerRatesB)
rural$GEOID <- formatC(rural$GEOID, width = 5, format = "d", flag = "0")
head(rural)

## Convert column called location to two columns: State and County
CancerRates <- separate(CancerRates, location, into = c("county", "state"), sep = ", ")
#head(CancerRates)
CancerRatesB <- separate(CancerRatesB, location, into = c("county", "state"), sep = ", ")
#head(CancerRatesB)


##Remove the (...) from the state values
CancerRates[] <- lapply(CancerRates, function(x) gsub("\\s*\\([^\\)]+\\)", "", x))
head(CancerRates)
CancerRatesB[] <- lapply(CancerRatesB, function(x) gsub("\\s*\\([^\\)]+\\)", "", x))
head(CancerRatesB)

##Remove the space# from the end of some of the values in the rate column
CancerRatesB[] <- lapply(CancerRatesB, function(x) gsub("\\#", "", x))
#CancerRatesB

# Convert full state names to abbreviations for a clean df merge later.
CancerRates$state <- state.abb[match(CancerRates$state,state.name)]
head(CancerRates)
CancerRatesB$state <- state.abb[match(CancerRatesB$state,state.name)]
head(CancerRatesB)

#Change CancerRates$rate to a number
CancerRates$rate <- as.numeric(as.character(CancerRates$rate))
#head(CancerRates)
CancerRatesB$rate <- as.numeric(as.character(CancerRatesB$rate))
#head(CancerRatesB)


# Download county shape file.
## !! This is important. Shape files can be found here
#https://www.census.gov/geo/maps-data/data/cbf/cbf_counties.html
#us.map <- tigris::counties(cb = TRUE, year = 2015)
#OR
# Download county shape file from Tiger.
# https://www.census.gov/geo/maps-data/data/cbf/cbf_counties.html
# I downloaded the zip and placed all files in the zip into my RStudio folder
#us.map <- readOGR(dsn = ".", layer = "cb_2016_us_county_20m", stringsAsFactors = FALSE)
head(us.map)
# Remove Alaska(2), Hawaii(15), Puerto Rico (72), Guam (66), Virgin Islands (78), American Samoa (60)
#  Mariana Islands (69), Micronesia (64), Marshall Islands (68), Palau (70), Minor Islands (74)
us.map <- us.map[!us.map$STATEFP %in% c("02", "15", "72", "66", "78", "60", "69",
                                        "64", "68", "70", "74"),]
#head(us.map)

# Make sure other outling islands are removed.
us.map <- us.map[!us.map$STATEFP %in% c("81", "84", "86", "87", "89", "71", "76",
                                        "95", "79"),]

# Merge spatial df with downloaded data.
## This is important
## Now we have our data and the needed carto data
cancermap <- merge(us.map, CancerRates, by=c("GEOID"))
cancermapB <- merge(us.map, CancerRatesB, by=c("GEOID"))
ruralmap <- merge(us.map, rural, by=c('GEOID'))

cancermap <- merge(cancermap, rural, by=c('GEOID'))

cancermap$urbanscore <- as.numeric(cancermap$urbanscore)

# Format popup data for leaflet map.
popup_dat <- paste0("<strong>County: </strong>", 
                    cancermap$county, 
                    "<br><strong>Cancer Rate (Age Adjusted) Out of 100,000: </strong>", 
                    cancermap$rate)

#Color Pallette
#pal <- colorQuantile("YlOrRd", NULL, n = 9)

# Render final map in leaflet.The better map is below so this is
## commented out
# leaflet(data = cancermap) %>% addTiles() %>%
#   addPolygons(fillColor = ~pal(rate), 
#               fillOpacity = 0.8, 
#               color = "#BDBDC3", 
#               weight = 1,
#               popup = popup_dat) %>% 
#   addMarkers(lat=39.8, lng=-105.2, popup="Rocky Flats SuperFund Site")


#Grouping for map options and User Choices
#https://rstudio.github.io/leaflet/showhide.html

##Make pop up for the land use sites
# Format popup data for leaflet map.
popup_LU <- paste0("<strong>Use Name: </strong>", 
                   LandUse$name, 
                   "<br><strong>Link: </strong>", 
                   LandUse$url)

popup_RES <- paste0('<strong>Resevoir: </strong>',
                   resevoirs$name)

popup_BLD <- paste0('<strong>Manufacturing Site: </strong>',
                    buildings$name)
popup_RUR <- paste0('<strong>Rural/Urban Continuum Score: </strong>',
                    cancermap$urbanscore, 
                    '<br><strong>County: </strong>',
                    cancermap$NAME)

pal <- colorQuantile("YlGnBu", NULL, n = 9)
cols = c("#253494", "#2C7FB8", "#41B6C4", "#A1DAB4", "#FFFFCC")
pal2 <- colorQuantile(cols, NULL, n = 5)

gmap <- leaflet(data = cancermap) %>%
  # Base groups
  #addTiles() %>%
  addProviderTiles(providers$CartoDB.Positron) %>% 
  setView(lng = -105, lat = 40, zoom = 4) %>% 
  addPolygons(fillColor = ~pal2(urbanscore), 
              fillOpacity = 0.8, 
              color = "#BDBDC3", 
              weight = 1,
              popup = popup_RUR,
              group='Rural Urban Continuum Codes') %>% 
  
  
  # Overlay groups
  addPolygons(fillColor = ~pal(rate),
              fillOpacity = .8,
              color='#BDBDC3',
              weight=1,
              popup = popup_dat,
              group="Cancer Rate/100,000 by Counties") %>% 
  
  #addMarkers(data=resevoirs,lat=~lat, lng=~lng, popup=popup_RES, group = "Resevoir Sites") %>% 
  addCircleMarkers(data=LandUse,lat=~lat, lng=~lng, popup=popup_LU, group = "Land Use Sites",
                   opacity=.75, fillOpacity=.4, radius=2, color='#d67b6b') %>% 
  addCircleMarkers(data=resevoirs, lat=~lat, lng=~lng, popup=popup_RES, group='Resevoir Sites',
             opacity=.75, fillOpacity=.4, radius=9) %>% 
  addCircleMarkers(data=buildings, lat=~lat, lng=~lng, popup=popup_BLD, group='Manufacturing Sites',
                   opacity=.75, fillOpacity=.4, radius=12, color='#9a329e') %>% 
  #addCircles(~long, ~lat, ~10^mag/5, stroke = F, group = "Quakes") %>%
  #addPolygons(data = outline, lng = ~long, lat = ~lat,
  #           fill = F, weight = 2, color = "#FFFFCC", group = "Outline") %>%
  
  # Layers control
  addLayersControl(
    baseGroups = c('Rural Urban Continuum Codes', 'Cancer Rate/100,000 by Counties'),
    overlayGroups = c("Land Use Sites", 'Resevoir Sites', 'Manufacturing Sites'),
    options = layersControlOptions(collapsed = FALSE)
  )
gmap
saveWidget(gmap, 'leaflet_ks.html', selfcontained = TRUE)




  
  