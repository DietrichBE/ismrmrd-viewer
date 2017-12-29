# Copyright (C) 2005-2007 Carabos Coop. V. All rights reserved
# Copyright (C) 2008-2017 Vicent Mas. All rights reserved
# Copyright (C) 2017 Institute for Biomedical Engineering, Swiss Federal
# Institute of Technology Zurich (ETH Zurich). All rights reserved.
#
# This module is adapted from leaf_model.py of the vitables package
# by Carabos Coop. V. and Vincent Mas.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Author: Benjamin Dietrich, dietrich@biomed.ee.ethz.ch

"""
This module implements a model (in the `MVC` sense) for the real data stored
in a `ismrmrd.Dataset`.
"""

from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt
import TableBuffer
import ismrmrd

#: The maximum number of rows to be read from the data source.
CHUNK_SIZE = 1000

class TableModel(QAbstractTableModel):
    """
    The model for real data contained in ismrmrd datasets.

    The data is read from data sources (i.e., `ismrmrd.Dataset` nodes) by
    the model.
    The dataset number of rows is potentially huge but tables are read and
    displayed in chunks.

    :param parent:
        The parent of the model, passed as is in the superclass.
    :attribute dset:
        the underlying ismrmrd.Dataset
    :attribute rbuffer:
        Code for chunking and inspecting the undelying data.
    :attribute leaf_numrows:
        the total number of rows in the underlying data
    :attribute numrows:
        The number of rows visible which equals the chunking-size.
    :attribute numcols:
        The total number of columnss visible, equal to those visible.
    :attribute start:
        The zero-based starting index of the chunk within the total rows.

    """

    def __init__(self, dset, parent=None):
        """Create the model.
        """

        # The model data source (a ISMRMRD dataset) and its access buffer
        self.dset = dset
        self.rbuffer = TableBuffer.TableBuffer(dset)

        self.leaf_numrows = self.rbuffer.total_nrows()
        self.numrows = min(self.leaf_numrows, CHUNK_SIZE)
        self.start = 0

        # get number of columns (ismrmrd acquisition header and encoding
        # counter fields)
        self.colnames = []
        
        fields = ismrmrd.EncodingCounters._fields_
        for item in fields:
            self.colnames.append(item[0])

        self.numcolsIdx = len(self.colnames)

        fields = ismrmrd.AcquisitionHeader._fields_
        for item in fields:
            self.colnames.append(item[0])

        self.colnames.remove('idx')
        self.numcols = len(self.colnames)

        # track selected cell
        self.selected_cell = {'index': QModelIndex(), 'buffer_start': 0}

        # populate the model with the first chunk of data
        self.loadData(0, self.numrows)

        super(TableModel, self).__init__(parent)

    def columnCount(self, index=QModelIndex()):
        """The number of columns of the given model index.

        Overridden to return 0 for valid indices because they have no children;
        otherwise return the total number of *columns* exposed by the model.

        :param index:
            the model index being inspected.
        """

        return 0 if index.isValid() else self.numcols

    def rowCount(self, index=QModelIndex()):
        """The number of columns for the children of the given index.

        Overridden to return 0 for valid indices because they have no children;
        otherwise return the total number of *rows* exposed by the model.

        :Parameter index: the model index being inspected.
        """

        return 0 if index.isValid() else self.numrows

    def loadData(self, start, length):
        """Load the model with fresh data from the buffer.

        :param start:
            the document row that is the first row of the chunk.
        :param length:
            the buffer size, i.e. the number of rows to be read.

        :return:
            a tuple with tested values for the parameters of the read method
        """

        # Enforce scrolling limits.
        start = max(start, 0)
        stop = min(start + length, self.leaf_numrows)

        # Ensure buffer filled when scrolled beyond bottom.
        actual_start = stop - self.numrows
        start = max(min(actual_start, start), 0)

        self.rbuffer.readBuffer(start, stop)
        self.start = start

    def get_corner_span(self):
        """Must return ``(row_span, col_span)`` tuple for the top-left cell."""
        return 1, 1

    def headerData(self, section, orientation, role):
        """Returns the data for the given role and section in the header
        with the specified orientation.

        This is an overwritten method.

        :Parameters:

        - `section`: the header section being inspected
        - `orientation`: the header orientation (horizontal or vertical)
        - `role`: the role of the header section being inspected
        """

        # The section alignment
        if role == Qt.TextAlignmentRole:
            if orientation == Qt.Horizontal:
                return Qt.AlignLeft | Qt.AlignVCenter
            return Qt.AlignRight | Qt.AlignVCenter

        if role != Qt.DisplayRole:
            return None

        # Columns-labels
        if orientation == Qt.Horizontal:
            # For tables horizontal labels are column names, for arrays
            # the section numbers are used as horizontal labels
            #if hasattr(self.leaf, 'description'):
            #    return str(self.leaf.colnames[section])
            #return str(section)
            return self.colnames[section]

        # Rows-labels
        return str(self.start + section)

    def data(self, index, role=Qt.DisplayRole):
        """Returns the data stored under the given role for the item
        referred to by the index.

        This is an overwritten method.

        :Parameters:

        - `index`: the index of a data item
        - `role`: the role being returned
        """
        row, col = index.row(), index.column()

        if not index.isValid() or not (0 <= row < self.numrows):
            return None

        if role == Qt.DisplayRole:

            if col < self.numcolsIdx: # index fields
                aq = ismrmrd.Acquisition(self.rbuffer.getCell(row)['head'])
                cell = getattr(aq.idx,self.colnames[col])
                
            else: # header fields
                aq = ismrmrd.Acquisition(self.rbuffer.getCell(row)['head'])
                cell = getattr(aq,self.colnames[col])

            # check if the current cell is the encoding counter field
            if isinstance(cell,ismrmrd.EncodingCounters):
                return None
            else: # otherwise no special treatment
                # check what kind of data we have at hand (array or scalar)
                try:
                    # if no error => we have an array => fromat as such
                    ret = '['
                    cellIterator = iter(cell)
                    firstItem = next(cellIterator)
                    ret += str(firstItem)

                    for item in cellIterator:
                        ret += ',' + str(item)

                    ret += ']'
            
                except Exception as e:
                    # if error => we have a scalar
                    ret = str(cell)

                return ret

        if role == Qt.TextAlignmentRole:
            return Qt.AlignLeft | Qt.AlignCenter

        return None




