# third party
from bs4 import BeautifulSoup as Soup
from . import Exporter


HEADER_ATTRS = {"id": "header"}
FOOTER_ATTRS = {"id": "footer"}
TITLE_ATTRS = {"id": "title"}
SUBTITLE_ATTRS = {"id": "subtitle"}


class HTMLExporter(Exporter):
    def __init__(self, table):
        self.tsoup = TableSoup(table)

    def to_file(self, filepath):
        with open(filepath, "w+") as handle:
            handle.write(self.tsoup.prettify())


class TableSoup(Soup):
    def __init__(self, table):
        self.table = table
        # run this to instantiate all the tags within the html
        self.__render()

    def __render(self):
        """Copies all the additional state added to a table and renders
        them into the overall HTML representation as appropriate tags.

        Essentially this method is the key method of translation from the
        table object to the TableSoup object. It combines copying state and
        rendering it as appropriate."""

        self._raw_html = self.table.data.to_html(border=0, index=False)
        super().__init__(self._raw_html, features="html.parser")

        self.header = self.new_tag("div", attrs=HEADER_ATTRS)
        self.insert(0, self.header)

        self.footer = self.new_tag("div", attrs=FOOTER_ATTRS)
        self.append(self.footer)

        if self.table.title:
            self.title = self.new_tag("h1", attrs=TITLE_ATTRS)
            self.title.string = self.table.title
            self.select_one(f"#{self.header['id']}").insert(0, self.title)

        if self.table.subtitle:
            self.subtitle = self.new_tag("h2", attrs=SUBTITLE_ATTRS)
            self.subtitle.string = self.table.subtitle

            subtitle_id = f"#{self.header['id']} > #{self.title['id']}"
            self.select_one(subtitle_id).insert_after(self.subtitle)

        # TODO: add source attrs
        if self.table.source:
            self.source = self.new_tag("p")
            self.source.string = self.table.source

            self.select_one(f"#{self.footer['id']}").insert(0, self.source)

        if len(self.table.merge_operations):
            self.merge_all()

        if len(self.table.row_groups):
            self.insert_all_rowgroups()

    def insert_all_rowgroups(self):
        # TODO: on each iteration it doesn't respect the original ordering of rows.
        # What happens is that if we add a row in say 2, then the next attempt
        # to add a row in 4 will add it early. Anyway, this needs to be resolved.
        for rowgroup in self.table.row_groups:
            self._insert_rowgroup(rowgroup)

    def _insert_rowgroup(self, after_row, text=None):
        row = self.rows[after_row]
        attrs = {"colspan": len(row.select("td")), "class": "rowgroup"}
        td = self.new_tag("td", attrs=attrs)
        # TODO: to just keep the height of the row correct
        # TODO: this isn't a great solution
        td.string = "⠀" if not text else text
        row_group = self.new_tag("tr")
        row_group.append(td)
        row.insert_after(row_group)

    def merge_all(self):
        for cells in self.table.merge_operations:
            self._merge(cells)

    def _merge(self, cells):
        # temporary check to tell the user we only support merging rows for now
        i = None
        for cell in cells:
            if i is None:
                i = cell[0]
            if cell[0] != i:
                raise ValueError(
                    "Could not merge cells across multiple rows. Unsupported for now."
                )

        row = cells[0][0]
        row = self[row]
        # TODO: maybe specifying this in spans would make more sense as the implementation is heading
        # that way anyway
        # we keep it empty or if an index into the cell list is provided we will use the
        # value of that cell as the placeholder
        # TODO: itemgetter
        key = lambda t: t[1]
        ordered = sorted(cells, key=key)
        starting_col = row[min(ordered, key=key)[1]]
        starting_col["colspan"] = len(cells)
        starting_col.string = ""

        for _, ix in ordered[1:]:
            row[ix].decompose()

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
