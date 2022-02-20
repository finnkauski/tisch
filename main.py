import pandas as pd
import tisch

# API EXAMPLE--simple table
data = pd.read_csv("https://people.sc.fsu.edu/~jburkardt/data/csv/cities.csv")
data = data.iloc[:10]

data.tisch.add_title("This is my table")
data.tisch.add_subtitle("My subtitle")
data.tisch.merge_cells(0, 2, 5)  # Changing my view on whether this is really needed, at least in a first cut
data.tisch.add_rowgroup(2)  # Would it be better to implement with pandas before export (leaving irrelevant cells with empty strings?)
data.tisch.add_rowgroup(5)
data.tisch.add_rowgroup(8)
data.tisch.add_source("Source: Data Science Campus")
# Print to screen (uses html if in an interactive jupyter session)
data.tisch
# Save to file
data.tisch.html.to_file("check.html")

# API example--a cross tabulation with two rows of column headings, stubhead,
# index, and summary rows on both axes.
# Current issues with this example:
# - index disappears when using .tisch accessor
# - final summary row disappears when using .tisch accessor
# - footnotes overwrites source.
# NB: https://github.com/statsmodels/statsmodels/blob/77bb1d276c7d11bc8657497b4307aa7575c3e65c/statsmodels/iolib/table.py#L125
# has some very useful stuff on exporting and formatting weirdly shaped tables
df = pd.read_csv("https://vincentarelbundock.github.io/Rdatasets/csv/palmerpenguins/penguins.csv", index_col=False)
df_table = pd.crosstab(df["species"], [df["sex"], df["island"]], margins=True)

df_table.tisch.add_title("This is my table")
df_table.tisch.add_subtitle("My subtitle")
df_table.tisch.add_source("Source: Data Science Campus")
df_table.tisch.add_footer("footnotes")
# Print to screen (uses html if in an interactive jupyter session)
df_table.tisch