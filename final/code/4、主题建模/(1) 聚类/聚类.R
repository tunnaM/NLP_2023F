#install.packages("factoextra", dependencies = T)
library(factoextra) # clustering algorithms & visualization
library(tidyverse)  # data manipulation
library(cluster)    # clustering algorithms
#install.packages("broom", dependencies = T)
library(broom)
library(ISLR2)
library(readxl)
library(dplyr)
#install.packages("ISLR", dependencies = T)
rm(list=ls())

df<-read_excel("好大夫数据.xlsx",1)
head(df)
df <- na.omit(df) # omit missing values

df <- df %>%
  mutate("职称级别" = case_when(
    str_detect(df$职级, "主治") ~ 2,
    str_detect(df$职级, "副主任") ~ 3,
    str_detect(df$职级, "主任") ~ 4,
    str_detect(df$职级, "主管") ~ 2,
    TRUE ~ 1  # 默认值，可以根据需要修改
  ))

df <- df %>%
  mutate("问诊价格" = as.numeric(str_extract_all(df$在线问诊, "\\d+")))

library(lubridate)

df <- df %>%
  mutate("开通年数" = year(Sys.Date()) - year(ymd(df$开通时间)))

df <- df %>%
  mutate("上次在线" = as.numeric(str_extract_all(df$上次在线时间, "\\d+")))

df <- df[, c("总访问量", "职称级别", "问诊价格","病友推荐度","总文章数","开通年数","昨日访问","上次在线")]

# 中心化
# df <- df %>%
 # mutate_all(~(.- mean(., na.rm = TRUE)) / (max(., na.rm = TRUE) - min(., na.rm = TRUE)))

# For k-means
head(df)

distance <- get_dist(df) # distance calculation
#heat map
fviz_dist(distance, 
          gradient = list(low = "#00AFBB", 
                          mid = "white", 
                          high = "#FC4E07"))
k2 <- kmeans(df, centers = 2, nstart = 25)
str(k2)
k2
fviz_cluster(k2, data = df)

k3 <- kmeans(df, centers = 3, nstart = 25)
str(k3)
k3
fviz_cluster(k3, data = df)


k3 <- kmeans(df, centers = 3, nstart = 25)
k4 <- kmeans(df, centers = 4, nstart = 25)
k5 <- kmeans(df, centers = 5, nstart = 25)

# plots to compare
p1 <- fviz_cluster(k2, geom = "point", data = df) + ggtitle("k = 2")
p2 <- fviz_cluster(k3, geom = "point",  data = df) + ggtitle("k = 3")
p3 <- fviz_cluster(k4, geom = "point",  data = df) + ggtitle("k = 4")
p4 <- fviz_cluster(k5, geom = "point",  data = df) + ggtitle("k = 5")

library(gridExtra)
grid.arrange(p1, p2, p3, p4, nrow = 2)


set.seed(123)

# function to compute total within-cluster sum of square 
wss <- function(k) {
  kmeans(df, k, nstart = 10 )$tot.withinss
}

# Compute and plot wss for k = 1 to k = 15
k.values <- 1:15

# extract wss for 2-15 clusters
wss_values <- map_dbl(k.values, wss)

plot(k.values, wss_values,
     type="b", pch = 19, frame = FALSE, 
     xlab="Number of clusters K",
     ylab="Total within-clusters sum of squares")

set.seed(123)

fviz_nbclust(df, kmeans, method = "wss")


num_clusters <- 4
kmeans_result <- kmeans(df, centers = num_clusters)
kmeans_result$cluster
kmeans_result$centers