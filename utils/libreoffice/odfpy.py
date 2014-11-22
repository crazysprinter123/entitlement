# pip install odfpy

import odf.opendocument
from odf.table import *
from odf.text import P

class ODSReader:

    # loads the file
    def __init__(self, file):
        self.doc = odf.opendocument.load(file)
        self.SHEETS = {}
        for sheet in self.doc.spreadsheet.getElementsByType(Table):
            self.readSheet(sheet)

    def readSheet(self, sheet):
        rows = sheet.getElementsByType(TableRow)
        # for each row
        for row in rows:
            cells = row.getElementsByType(TableCell)
            # for each cell
            for cell in cells:
                ps = cell.getElementsByType(P)
                # for each text node
                for p in ps:
                    for n in p.childNodes:
                        print n.data

if __name__ == "__main__":
    ODSReader("test.ods")
