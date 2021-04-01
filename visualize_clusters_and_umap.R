library(data.table)
library(pheatmap)

data <- fread('data/drums_and_features.csv')

dm <- data.matrix(data)

wavnames <- colnames(dm)

drum.categories <- unlist(lapply(wavnames, function(x){substr(x,0,2)}))

d.anno <- data.frame(drum.categories)
row.names(d.anno) <- colnames(dm)

pheatmap(dm, annotation_col = d.anno)

my_heatmap

min(dm + 39, na.rm = TRUE)

#dmc <- dm[complete.cases(dm),]

dmcs <- (dm - mean(dm, na.rm = TRUE)) / sd(dm, na.rm = TRUE)

for(i in 1:ncol(dmcs)){
  dmcs[is.na(dmcs[,i]), i] <- mean(dmcs[,i], na.rm = TRUE)
}


pheatmap(log(dmcs + 10))


for(i in 1:ncol(dm)){
  dm[is.na(dm[,i]), i] <- mean(dm[,i], na.rm = TRUE)
}

dm[is.na(dm)] = 4

hist(dm)

dm2 <- dm

dm2[dm2 < -5] <- 0.0

hist(scale(dm2), breaks = 100)

sdm2 <- scale(dm2)
sdm2[sdm2 > 1.5] <- 1.5
sdm2[sdm2 < -1.5] <- -1.5

pheatmap(sdm2, annotation_col = d.anno)

library(umap)

umap.dm <- umap(t(sdm2))

umap.dm.2 <- umap(t(dm))

dt <- data.table(x = umap.dm$layout[,1], y = umap.dm$layout[,2], sample = drum.categories)

ggplot(dt) + geom_point(aes(x = x, y = y, color = sample)) + theme_bw()
