# third party
import pandas as pd

# project
from .exporters.html import HTMLExporter


@pd.api.extensions.register_dataframe_accessor("tisch")
class Table:
    """This represents all the individual parts of the table.

    Within this object the entire state of the additional parts
    of the table to be exported is stored. Things like titles,
    subtitles, what cells to merge etc.

    This is then used by one of the implemented exporters as a
    standard way to acquire relevant information.
    """

    def __init__(self, pandas_df):
        # TODO: add data setter
        self.data = pandas_df
        self._setup()

    def _setup(self):

        self.title = None
        self.subtitle = None
        self.header = None
        self.footer = None
        self.source = None

        # Intialise this here as to not have the class list that stuff gets added
        # to. Common trap with mutable lists as defaults
        self.merge_operations = []

        self.row_groups = []

    def add_source(self, text):
        self.source = text

    def add_footer(self, text):
        self.source = text

    def add_title(self, text):
        self.title = text

    def add_subtitle(self, text):
        # TODO: could support direct tag addition rather than just text
        if self.title is None:
            # TODO: add custom errors
            raise ValueError(
                "Could not find a title, add title using `.add_title` first."
            )
        self.subtitle = text

    def add_rowgroup(self, after_row):
        self.row_groups.append(after_row)

    def merge_cells(self, row, first, last):
        # TODO: need to add validation to make sure cells are adjascent
        # TODO: avoid this kind of thing, implement this in the mergecells
        cells = list(range(first, last + 1))
        cells = list(zip([row] * len(cells), cells))

        self.merge_operations.append(cells)

    def reset(self):
        self._setup()

    # TODO: could add an automatic way to register if a variable has changed.
    # And if it has changed, then we need to regenerate the state.
    @property
    def html(self):
        # TODO: can add a state tracker to make sure that whenever a variable
        # is changed, only then it rerenders.
        return HTMLExporter(self)

    def _repr_html_(self):
        return HTMLExporter(self).get_html()

    def __repr__(self):
        string = f"""Table:
------
title: {self.title}
subtitle: {self.subtitle}
header: {self.header}
footer: {self.footer}
merges: {self.merge_operations}
row_groups_after: {self.row_groups}
-----
source: {self.source}
        """
        return string


# TODO: consider subclassing tags into custom tags - like rowgroup
# TODO: add a - from config json so that someone can have a default json parameterisation of the pipeline
