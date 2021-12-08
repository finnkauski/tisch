import pandas as pd



class Table:

    def __init__(self, data):
        self.frame = data
        self.data_html = data.to_html()

    @property
    def html(self):
        return self.data_html

    def to_file(self, filepath):
        with open(filepath, "w+") as handle:
            handle.write(self.html)
