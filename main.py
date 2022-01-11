import pandas as pd
from tisch import Table
from tisch.exporters.html import HTMLExporter


data = pd.read_csv("https://people.sc.fsu.edu/~jburkardt/data/csv/cities.csv")
table = Table(data)
table.add_title("This is my table")
table.add_subtitle("My subtitle")
table.merge_cells(0, 2, 5)
table.add_rowgroup(2)
table.add_rowgroup(5)
table.add_rowgroup(8)
table.add_source("Source: Data Science Campus")

print(table)
exporter = HTMLExporter(table)
print(exporter)
exporter.to_file("check.html")
