# Copyright (C) 2005-2007 Carabos Coop. V. All rights reserved
# Copyright (C) 2008-2017 Vicent Mas. All rights reserved
# Copyright (C) 2017 Institute for Biomedical Engineering, Swiss Federal
# Institute of Technology Zurich (ETH Zurich). All rights reserved.
#
# This module is adapted from filenodebuffer.py of the vitables package
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
This module implements a buffer used to access the real data contained in
an ISMRMRD (HDF5) file.

By using this buffer we speed up the access to the stored data. As a
consequence, views (widgets showing a tabular representation of the dataset)
are painted much faster too.
"""

import numpy

class TableBuffer(object):
    """Buffer used to access the real data contained in ISMRMRD (HDF5) files.

    Note that the buffer number of rows **must** be at least equal to
    the number of rows of the table widget it is going to fill. This
    way we avoid to have partially filled tables. Also note that rows
    in buffer are numbered from 0 to N (as it happens with the data
    source).

    :Parameter dset:
        the data source (ismrmrd.Dataset instance) from which data are
        going to be read.
    """

    def __init__(self, dset):
        """
        Initializes the buffer.
        """
        self.dset = dset

        # The structure where read data will be stored.
        self.chunk = numpy.array([])
        self.total_rows = dset.number_of_acquisitions()

    def __del__(self):
        """Release resources before destroying the buffer.
        """
        # FIXME: PY3.5+ leaks resources (use finalizer instead).
        self.chunk = None

    def total_nrows(self):
        return self.total_rows

    def readBuffer(self, start, stop):
        """
        Read the selected range of ismrmrd acquisitions into memory.

        :Parameters:
        :param start: the ismrmrd dataset row that is the first row of the chunk.
        :param stop: the last row to read (inclusive).
        """

        if stop > self.total_rows:
            stop = self.total_rows

        # read acquisitions
        self.chunk = self.dset._dataset['data'][start:stop]

    def getCell(self, row):
        """
        Returns a cell of the buffer

        :Parameters:
        - `row`: the row to which the cell belongs.
        :Returns: the cell at position `(row)` of the buffer
        """

        return self.chunk[row]
