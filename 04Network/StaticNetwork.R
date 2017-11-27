setwd('Documents/ANLY503/Portfolio')

# Libraries
library(igraph)
library(extrafont)
library(RColorBrewer)
library(colorspace)
library(grDevices)
library(networkD3)
library(plyr)
library(scales)


pdf('Graphics/StaticNetwork.pdf', height=20, width=30)

# Read data
edges <- read.table("Data/1_Edges.txt", header=T, sep='\t')
nodes <- read.table("Data/1_Nodes.txt", header=T, sep='\t')
names(edges) <- c('Winner', 'Loser', 'ScoreDiff')
nodes$ID <- c(0:(length(nodes$Team)-1))
#names(nodes) <- c('Team', 'C.Rank10', 'C.Rank11', 'AP.Rank10', 'AP.Rank11', 'Conf', 'ConfNum', 'ID')

rownames(nodes) <- nodes$ID

###### --------------------
# Set up network
g <- graph.data.frame(edges, nodes, directed=T)


# Edge label is score differential
E(g)$label <- edges$ScoreDiff
E(g)$label.cex <- .8


# Vertex colors based on conference
#col.a <- palette(rainbow_hcl(length(unique(nodes$ConfNum)), start = 10, end = 440))
#col.a <- palette(c(brewer.pal(n = 10, name = "Set3"), brewer.pal(n = 8, name = "Set1")))
col.a <- palette(c('darkseagreen', 'indianred3', 'powderblue', 'royalblue2',
                   'yellowgreen', 'tan1', 'cornflowerblue', ' plum3', 'rosybrown3',
                   'darkolivegreen1', 'lightpink2', 'lightseagreen', 'lightsteelblue2',
                   'salmon', 'pink2', 'tomato2', 'slateblue2', 'gold', 'mediumpurple1', 'cadetblue'))

V(g)$color <- col.a[V(g)$Conference.Num]

# Vertex size by rank
V(g)$size <- with(nodes, ifelse(College.Football.Playoff.Ranking < 25, 8, 3))


# Bigger labels for highly ranked schools
V(g)$label.cex <- with(nodes, ifelse(College.Football.Playoff.Ranking < 25, 1, .5))


# Rescale to 0 -> 1
E(g)$arrow.size <- rescale(edges$ScoreDiff)/2

# Plot
plot(g, main='NCAA Week 10 Football Games')
legend('bottomleft', unique(V(g)$Conference),
       pch=21,col=col.a, pt.bg=col.a, pt.cex=1.5, cex=1, bty="n",
       ncol=1, title = 'Conference')


dev.off()


