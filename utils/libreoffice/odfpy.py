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
            if len(cells) == 1:  # ignore blank rows
                continue
            else:
                # for each cell
                for cell in cells:
                    textContent = ""
                    # repeated value?
                    repeat = cell.getAttribute("numbercolumnsrepeated")
                    if(not repeat):
                        repeat = 1
                    ps = cell.getElementsByType(P)
                    if len(ps) == 0:
                        for rr in range(int(repeat)):  # repeated blank cells
                            print "blank"
                    else:
                        for p in ps:
                            for n in p.childNodes:
                                if (n.nodeType == 3):
                                    textContent = n.data
#                                     textContent = unicode(n.data)
                        if(textContent):
                            if(textContent[0] != "#"):  # ignore comments cells
                                for rr in range(int(repeat)):  # repeated cells
                                    if textContent != "":
                                        print textContent

if __name__ == "__main__":
    ODSReader("test.ods")
# improvement
# 1, can not read blanks at the begin or end of cells
