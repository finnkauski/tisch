import pandas as pd
from bs4 import BeautifulSoup as Soup

from abc import ABC, abstractmethod

#from tisch import Table

# TODO: consider subclassing tags into custom tags - like rowgroup
# TODO: add a - from config json so that someone can have a default json parameterisation of the pipeline

MOCK_CSS = """
body {
    background: red;
}

"""
HEADER_ATTRS = {"id":"header"}
TITLE_ATTRS = {"id":"title"}
SUBTITLE_ATTRS = {"id":"subtitle"}

class Operation(ABC):

    @abstractmethod
    def apply(self):
        pass

class MergeCells(Operation):

    def __init__(self, cells, table, keep_value):
        self.table = table
        self.cells = cells
        self.keep_value = keep_value

        # confirm that the keep value is within the range
        if self.keep_value < 0 or self.keep_value >= len(self.cells):
            raise ValueError("Your keep value is not within the range of the cells you're merging.")



    def apply(self):
        # NOTE: this can change the state of the table, if you are getting
        # changes to your table and unsure where its coming from, consider this
        # as it can be working in place.

        # temporary check to tell the user we only support merging rows for now
        check_row = False
        i = None
        for cell in self.cells:
            if i is None:
                i = cell[0]
                continue
            if cell[0] != i:
                raise ValueError("Could not merge cells across multiple rows. Unsupported for now.")

        row = self.cells[0][0]
        row = self.table.tsoup[row]
        # TODO: maybe specifying this in spans would make more sense as the implementation is heading
        # that way anyway
        # we keep it empty or if an index into the cell list is provided we will use the
        # value of that cell as the placeholder
        # TODO: itemgetter
        key = lambda t: t[1]
        ordered = sorted(self.cells, key=key)

        value = "" if self.keep_value is None else row[ordered[self.keep_value][1]].string

        starting_col = row[min(ordered, key=key)[1]]
        starting_col["colspan"] = len(self.cells)
        starting_col.string = value

        for _, ix in ordered[1:]:
            row[ix].decompose()

class TableSoup(Soup):

    @property
    def table_body(self):
        return self.select_one("tbody")

    @property
    def table_head(self):
        return self.select_one("thead")

    @property
    def rows(self):
        return self.tbody.select("tr")

    @staticmethod
    def __col_given_row(row, ix):
        return row.select("td")[ix]

    def __getrow__(self, ix):
        return self.rows[ix]

    def __getcol__(self, ix):
        # TODO: could this be easier to do if we flattened the structure first
        # then calculated the index like row * col and just indexed that? one select
        # in that case
        return [self.__col_given_row(row, ix) for row in self.rows]

    def __getitem__(self, key):
        if isinstance(key, tuple):
            row, col = key
            # This only works when row is provided
            if row is not None:
                return self.__col_given_row(self.__getrow__(row), col)
            else:
                return self.__getcol__(col)

        elif isinstance(key, int):
           return self.__getrow__(key).select("td")

@pd.api.extensions.register_dataframe_accessor("tisch")
class Table:


    def __init__(self, pandas_df):
        # TODO: add data setter
        self.data = pandas_df
        self._setup()

    def _setup(self):

        self.title = None
        self.subtitle = None
        self.css = None

        # Intialise this here as to not have the class list that stuff gets added
        # to. Common trap with mutable lists as defaults
        self.merge_operations = []

        # Set up a new soup
        self._frame_to_data_html()
        self.tsoup = TableSoup(self.data_html)

        # Add a container to contain the header
        self.header = self.tsoup.new_tag("div", attrs=HEADER_ATTRS)
        self.tsoup.insert(0, self.header)


    def _frame_to_data_html(self, **kwargs):
        # TODO: unclear if this should sit in table soup
        self.data_html = self.data.to_html(border=0, index=False, **kwargs)

    def add_title(self, text, html_tag="h1", attrs=TITLE_ATTRS):
        self.title = self.tsoup.new_tag(html_tag, attrs=attrs)
        self.title.string = text

    def add_subtitle(self, text, html_tag="h2", attrs=SUBTITLE_ATTRS):
        # TODO: could support direct tag addition rather than just text
        if self.title is None:
            # TODO: add custom errors
            raise ValueError("Could not find a title, add title using `.add_title` first.")
        self.subtitle = self.tsoup.new_tag(html_tag, attrs=attrs)
        self.subtitle.string = text

    def add_rowgroup(self, after_row, text=None):
        row = self.tsoup.rows[after_row]
        attrs = {
            "colspan":len(row.select("td")),
            "class":"rowgroup"
        }
        td = self.tsoup.new_tag("td", attrs=attrs)
        # TODO: to just keep the height of the row correct
        # TODO: this isn't a great solution
        td.string = "⠀" if not text else text
        row_group = self.tsoup.new_tag("tr")
        row_group.append(td)
        row.insert_after(row_group)

    def embed_css(self, css=None, filepath=None):
        self.css = self.tsoup.new_tag("style")
        if css:
            self.css.string = css
        elif filepath:
            with open(filepath, "r") as handle:
                self.css.string = handle.read()
        else:
            # TODO: change to logging and warnings
            print("No css provided and hence nothing was embedded")


    def merge_cells(self, row, first, last, keep_value=None):
        # TODO: need to add validation to make sure cells are adjascent
        # TODO: avoid this kind of thing, implement this in the mergecells
        cells = list(range(first, last+1))
        cells = list(zip([row]*len(cells), cells))

        self.merge_operations.append(MergeCells(cells, self, keep_value))

    def reset(self, what=None):
        self._setup()

    def render(self):
        # add title
        if self.title:
            self.tsoup.select_one(f"#{self.header['id']}").insert(0, self.title)

        # add subtitle
        if self.title and self.subtitle:
            subtitle_id = f"#{self.header['id']} > #{self.title['id']}"
            self.tsoup.select_one(subtitle_id).insert_after(self.subtitle)

        if self.css:
            self.tsoup.insert(0, self.css)

        if self.merge_operations:
            # do the merges
            for merge in self.merge_operations:
                merge.apply()

    def to_html(self, filepath):
        # TODO: maybe this should have the default settings for the setup
        # and the setup only happens after this is called
        self.render()
        with open(filepath, "w+") as handle:
            handle.write(self.tsoup.prettify())



data = pd.read_csv("https://people.sc.fsu.edu/~jburkardt/data/csv/cities.csv")
table = Table(data)
table.add_title("This is my table")
table.add_subtitle("My subtitle")
table.merge_cells(0, 2, 5, keep_value=2)
table.add_rowgroup(2)
table.add_rowgroup(5)
table.add_rowgroup(8)
table.embed_css(filepath="test.css")
table.to_html("name.html")
