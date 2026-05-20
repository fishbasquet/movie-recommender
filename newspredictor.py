import pandas as pd

fake = pd.read_csv("Fake.csv")
real = pd.read_csv("True.csv")

fake["label"] = 0
real["label"] = 1 # All fake and real news articles are labeled as either 0 or 1, respectively. This will be used to train the model to detect whether the headline is real or fake.
 
news = pd.concat([fake, real])
news = news[["text", "label"]] # All unnecessary data removed from the table after concatenating the two datasets.
news = news.sample(frac = 1).reset_index(drop = True) # Shuffles 100% of the rows of data (denoted by frac = 1) and resets the index to ensure proper ordering. the sample function normally keeps the original index, so resetting it solves this problem.

print(news.head()) 