import pandas as pd
import tisch

# API EXAMPLE

data = pd.read_csv("https://people.sc.fsu.edu/~jburkardt/data/csv/cities.csv")
data.tisch.add_title("This is my table")
data.tisch.add_subtitle("My subtitle")
data.tisch.merge_cells(0, 2, 5)
data.tisch.add_rowgroup(2)
data.tisch.add_rowgroup(5)
data.tisch.add_rowgroup(8)
data.tisch.add_source("Source: Data Science Campus")
data.tisch.html.to_file("check.html")
