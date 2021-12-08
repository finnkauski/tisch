import pandas as pd
from bs4 import BeautifulSoup as Soup
#from tisch import Table

HEADER_ATTRS = {"id":"header"}
TITLE_ATTRS = {"id":"title"}
SUBTITLE_ATTRS = {"id":"subtitle"}

class Table:

    def __init__(self, data, **kwargs):
        self.data = data
        self._frame_to_data_html(**kwargs)
        self.soup = Soup(self.data_html)
        self._setup()

    def _setup(self):
        # Add a container to contain the header
        self._header = self.soup.new_tag("div", attrs=HEADER_ATTRS)
        self.soup.insert(0, self._header)

        # Initialise the individual parts
        self._title = None
        self._subtitle = None


    def _frame_to_data_html(self, **kwargs):
        self.data_html = self.data.to_html(border=0, **kwargs)

    def add_title(self, text, html_tag="h1", attrs=TITLE_ATTRS):
        self._title = self.soup.new_tag(html_tag, attrs=attrs)
        self._title.string = text
        self.soup.select_one(f"#{self._header['id']}").insert(0, self._title)

    def add_subtitle(self, text, html_tag="h2", attrs=SUBTITLE_ATTRS):
        # TODO: could support direct tag addition rather than just text
        title_id = f"#{self._header['id']} > #{self._title['id']}"
        if self._title is None:
            # TODO: add custom errors
            raise ValueError("Could not find a title, add title using `.add_title` first.")
        self._subtitle = self.soup.new_tag(html_tag, attrs=attrs)
        self._subtitle.string = text
        self.soup.select_one(title_id).insert_after(self._subtitle)

    def to_file(self, filepath):
        with open(filepath, "w+") as handle:
            handle.write(self.soup.prettify())




data = pd.read_csv("https://people.sc.fsu.edu/~jburkardt/data/csv/cities.csv")
table = Table(data, index=False)
table.add_title("This is my table")
table.add_subtitle("My subtitle")
table.to_file("name.html")
