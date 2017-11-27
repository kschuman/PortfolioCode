library(ggplot2)
library(scales)
library(ggalt)
theme_set(theme_classic())

m15 <- read.table('Data/murder2015.csv', sep=',', header=T)
m16 <- read.table('Data/murder2016.csv', sep=',', header=T)

m15$X2014_murders <- m15$X2014_murders + 1
m15$X2015_murders <- m15$X2015_murders + 1
m16$X2015_murders <- m16$X2015_murders + 1
m16$X2016_murders <- m16$X2016_murders + 1

# Percent change
m15$perc <- 100*round((m15$X2015_murders - m15$X2014_murders)/(m15$X2014_murders), 3)
m16$perc <- 100*round((m16$X2016_murders - m16$X2015_murders)/(m16$X2015_murders), 3)

# Above/below flag
m15$perc_type <- ifelse(m15$perc < 0, "below", "above")
m16$perc_type <- ifelse(m16$perc < 0, "below", "above")

plusminus = function(x) {sprintf("%+.1f", x)}
m15$lab <- paste(plusminus(m15$perc), '%')
m16$lab <- paste(plusminus(m16$perc), '%')


# Sort
m15 <- m15[order(m15$perc),]
m16 <- m16[order(m16$perc),]

m15$city <- factor(m15$city, levels = m15$city)
m16$city <- factor(m16$city, levels = m16$city)

ggplot(m15, aes(x = city, y = change, label = change)) + 
  geom_bar(stat='identity', aes(fill=perc_type), width=.5) + 
  scale_fill_manual(name='', labels = c('Increase', 'Decrease'),
                    values = c("above"="#f8766d", "below"="#00ba38"))  +
  coord_flip() +
  geom_text( color='navy', size=2, label = m15$lab) +
  labs(title='Change in Murder Rate from 2014 to 2015', subtitle='Actual and Percent Differences per City') +
  xlab('City') + ylab('Change in Number of Murders')



m15 <- read.table('Data/murder2015.csv', sep=',', header=T)
m16 <- read.table('Data/murder2016.csv', sep=',', header=T)

murders <- merge(m15, m16, by = 'city')

murders <- murders[order(murders$X2014_murders),]

murders$city <- factor(murders$city, levels = as.character(murders$city))
murders$city



ggplot(murders, aes(x=X2014_murders, xend=X2016_murders, y = city, group = city)) +
  geom_dumbbell(color="#a3c4dc", size=0.75, colour_xend="#0e668b", show.legend=T) +
  scale_x_continuous(name='Number of Murders', expand=c(0,10))  +
  labs(x=NULL, y=NULL, title="Changes in Murder Counts, 2014 vs. 2016") + 
  geom_text(aes(x=333, y='New York', label='2014'),  
            color="#a3c4dc", hjust=1, size=2, nudge_y=1) +
  geom_text(aes(x=252, y='New York', label='2016'),  
            color="#0e668b", hjust=1, size=2, nudge_y=1, nudge_x = 15) +
  theme(legend.position="none") + theme(plot.background=element_rect(fill = "grey93", colour = "grey93")) +
  theme(plot.title=element_text(size = 11, face = "bold", hjust = 0)) + 
  theme(axis.text.x=element_text(size = 8)) + 
  theme(axis.text.y=element_text(size = 8)) + 
  theme(axis.title.x=element_text(size = 9))  + 
  theme(axis.title.y=element_text(size=9)) + 
  theme(axis.ticks=element_blank()) + 
  theme(panel.grid.major.y=element_blank()) + 
  theme(plot.margin=margin(30,30,30,30)) 

