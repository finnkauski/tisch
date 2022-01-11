# Tisch

<img height="200px" src="logo.svg">

This simple library solves a very specific problem

> How do I quickly format and publish tables from a dataframe?

This is useful for analysts aiming to quickly add formatting, titles, subtitles, footnotes as well as source information to a given table.

Goals:

- simple API
- easy extensibility

Currently supported export formats:
- HTML

## Example

```python
import pandas as pd
import tisch

# Perform basic operations
data = pd.read_csv("https://people.sc.fsu.edu/~jburkardt/data/csv/cities.csv")
data.tisch.add_title("This is my table")
data.tisch.add_subtitle("My subtitle")
data.tisch.merge_cells(0, 2, 5)
data.tisch.add_rowgroup(2)
data.tisch.add_rowgroup(5)
data.tisch.add_rowgroup(8)
data.tisch.add_source("Source: Data Science Campus")
data.tisch.html.to_file("check.html")
```
