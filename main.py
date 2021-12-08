import pandas as pd
from bs4 import BeautifulSoup as Soup

from abc import ABC, abstractmethod

#from tisch import Table

HEADER_ATTRS = {"id":"header"}
TITLE_ATTRS = {"id":"title"}
SUBTITLE_ATTRS = {"id":"subtitle"}

class Operation(ABC):

    @abstractmethod
    def apply(self):
        pass

class MergeCells(Operation):

    def __init__(self, merge_spec, table):
        self.table = table
        self.merge_spec = merge_spec

    def apply(self):
        pass


class TableSoup(Soup):

    @property
    def table_body(self):
        return self.select_one("tbody")

    @property
    def table_head(self):
        return self.select_one("thead")

    def __clean_rows(self):
        "Bs4 Gives us `\n` as seperate tags. We filter them out to just keep table rows"
        row_condition = lambda row: isinstance(row, bs4.element.Tag)
        return list(filter(row_condition, self.tbody.contents))


    def __getrow__(self, ix):
        return self.__clean_rows()[ix]

    def __getcol__(self, ix):
        return [row.contents[ix] for row in self.__clean_rows()]

    def __getitem__(self, key):
        if isinstance(key, tuple):
            row, column = key
            print(row)
            print(self.__getcol__(row))
            return  self.__getrow__(row)



class Table:
    title = None
    subtitle = None
    merge_operations = []


    def __init__(self, data, **kwargs):
        # TODO: add data setter
        self.data = data
        self._frame_to_data_html(**kwargs)
        self.tsoup = TableSoup(self.data_html)
        self._setup()

    def _setup(self):
        # Add a container to contain the header
        self.header = self.tsoup.new_tag("div", attrs=HEADER_ATTRS)
        self.tsoup.insert(0, self.header)

    def _frame_to_data_html(self, **kwargs):
        # TODO: unclear if this should sit in table soup
        self.data_html = self.data.to_html(border=0, **kwargs)

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

    def merge_cells(self, merges=[]):
        # TODO: need to add validation to make sure cells are adjascent
        for merge_spec in merges:
            self.merge_operations.append(MergeCells(merge_spec, self))

    def render(self):
        # add title
        self.tsoup.select_one(f"#{self.header['id']}").insert(0, self.title)

        # add subtitle
        subtitle_id = f"#{self.header['id']} > #{self.title['id']}"
        self.tsoup.select_one(subtitle_id).insert_after(self.subtitle)

    def to_file(self, filepath):
        self.render()
        with open(filepath, "w+") as handle:
            handle.write(self.tsoup.prettify())



data = pd.read_csv("https://people.sc.fsu.edu/~jburkardt/data/csv/cities.csv")
table = Table(data, index=False)
table.add_title("This is my table")
table.add_subtitle("My subtitle")
table.merge_cells([(0, 2), (0,3)])
row = table.tsoup[1,2]
table.to_file("name.html")
