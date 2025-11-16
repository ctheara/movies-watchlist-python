import pandas as pd
import numpy as np

df = pd.read_csv("IMBD.csv")
print(df.head())

# Remove commas from votes and convert to int
df["votes"] = df["votes"].str.replace(",", "")
df["votes"] = pd.to_numeric(df["votes"], errors='coerce')
df["votes"] = df["votes"].astype('Int64')
# Convert rating to float
df["rating"] = df["rating"].astype(float)
# Strip whitespace from genre
df["genre"] = df["genre"].str.strip()

# Print the cleaned DataFrame
print("after cleaning:")
print(df.head())

# Average rating
average_rating = df["rating"].mean()
# Most frequent genre
most_frequent_genre = df["genre"].mode()[0]
# Total number of movies
total_movies = len(df)
# Number of movies above 8.0 rating
high_rating_count = (df["rating"] > 8.0).sum()
# Top 10 movies by rating, with unique titles
top_10_movies = df.sort_values(by="rating", ascending=False).drop_duplicates(subset=["title"]).head(10)

print(f"Average rating: {average_rating}")
print(f"Most frequent genre: {most_frequent_genre}")
print(f"Total movies: {total_movies}")
print(f"Movies with rating > 8: {high_rating_count}")
print("Top 10 movies by rating:")
print(top_10_movies[["title", "rating"]])

# Top 5 genres by count, group the titles
# get unique titles first, then count
unique_titles = df.drop_duplicates(subset=["title"])
top_genres = unique_titles["genre"].value_counts().head(5)
print("Top 5 genres by count:")
print(top_genres)

# Average rating per genre
unique_titles = df.drop_duplicates(subset=["title"])
avg_rating_by_genre = unique_titles.groupby("genre")["rating"].mean().sort_values(ascending=False)
print(avg_rating_by_genre.head())