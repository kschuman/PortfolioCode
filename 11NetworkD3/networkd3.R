# Kira Schuman
# HW - Part 2

# Set directory
setwd('~/PortfolioCode/11NetworkD3')
# Libraries
library(igraph)
library(extrafont)
library(RColorBrewer)
library(colorspace)
library(grDevices)
library(networkD3)
library(plyr)

# Read data
edges <- read.table("KS_Edges2b.txt", header=T, sep='\t')
nodes <- read.table("KS_Nodes2.txt", header=T, sep='\t')[,0:5]
#edges <- read.table("1_edges.txt", header=T, sep='\t')
#nodes <- read.table("1_nodes.txt", header=T, sep='\t')[,0:5]
names(edges) <- c('Winner', 'Loser', 'ScoreDiff')
nodes$ID <- c(0:(length(nodes$Team)-1))
names(nodes) <- c('Team', 'C.Rank', 'AP.Rank', 'Conf', 'ConfNum', 'ID')
rownames(nodes) <- nodes$ID

# Simplify
g <- simplify(graph.data.frame(edges, directed=TRUE))

# Node function
get.NodeID <- function(x){
  which(x == nodes$Team) - 1
}

# Add Team IDs
edges <- merge(edges, nodes[,c('Team', 'ID')], by.x = 'Loser', by.y = 'Team')
names(edges) <- c('Loser', 'Winner', 'ScoreDiff', 'LoserID')
edges <- merge(edges, nodes[,c('Team', 'ID')], by.x = 'Winner', by.y = 'Team')
names(edges) <- c('Winner', 'Loser', 'ScoreDiff', 'LoserID', 'WinnerID')

# Add node degree
nodes <- cbind(nodes, nodeDegree = igraph::degree(g, v = V(g), mode = "out"))

# Betweenness
between <- igraph::betweenness(g, v = V(g), directed = TRUE) / 
  (((igraph::vcount(g) - 1) * (igraph::vcount(g)-2)) / 2)

between.norm <- (between - min(between))/(max(between) - min(between))
nodes <- cbind(nodes, nodeBetweenness=100*between.norm) 

# Dice Similarity
dice.sim <- igraph::similarity.dice(g, vids = igraph::V(g), mode = "out")
(head(dice.sim))

# Function to calculate dice similarity
F1 <- function(x) {data.frame(diceSim = dice.sim[x$WinnerID +1, x$LoserID + 1])}

# Add Dice Sim column
edges <- ddply(edges, .variables=names(edges), 
                        function(x) data.frame(F1(x)))

# Colors
F2 <- colorRampPalette(c("#faff00", "#008cff"), bias = nrow(edges), space = "rgb", interpolate = "linear")
colCodes <- F2(length(unique(edges$ScoreDiff)))
edges_col <- sapply(edges$ScoreDiff, function(x) colCodes[which(sort(unique(edges$ScoreDiff)) == x)])


# Node Size
nodes$Size <- (27 - c(nodes$C.Rank))*1.5

# D3 Plot
D3_network_LM <- forceNetwork(Links = edges, # data frame that contains info about edges
                                         Nodes = nodes, # data frame that contains info about nodes
                                         Source = "WinnerID", # ID of source node 
                                         Target = "LoserID", # ID of target node
                                         Value = "ScoreDiff", # value from the edge list (data frame) that will be used to value/weight relationship amongst nodes
                                         NodeID = "Team", # value from the node list (data frame) that contains node description we want to use (e.g., node name)
                                         Nodesize = "Size",  # value from the node list (data frame) that contains value we want to use for a node size
                                         Group = "Conf",  # value from the node list (data frame) that contains value we want to use for node color
                                         height = 500, # Size of the plot (vertical)
                                         width = 1000,  # Size of the plot (horizontal)
                                         fontSize = 20, # Font size
                                         linkDistance = networkD3::JS("function(d) { return 10*d.value; }"), # Function to determine distance between any two nodes, uses variables already defined in forceNetwork function (not variables from a data frame)
                                         linkWidth = networkD3::JS("function(d) { return d.value/5; }"),# Function to determine link/edge thickness, uses variables already defined in forceNetwork function (not variables from a data frame)
                                         opacity = 0.9, # opacity
                                         zoom = TRUE, # ability to zoom when click on the node
                                         opacityNoHover = 0.5, # opacity of labels when static
                                         linkColour = edges_col, # edge colors
                                          arrows=TRUE)

# Plot network
D3_network_LM 

# Save HTML
networkD3::saveNetwork(D3_network_LM, "KS_D3Network.html", selfcontained = TRUE)




