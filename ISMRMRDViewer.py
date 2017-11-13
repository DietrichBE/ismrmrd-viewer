# Copyright (C) 2017 Institute for Biomedical Engineering, Swiss Federal
# Institute of Technology Zurich (ETH Zurich). All rights reserved.
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

import sys
import os.path
import webbrowser
import tempfile
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QSplitter
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import ismrmrd
import images_qr
import ISMRMRDTableView, ISMRMRDTableModel, ISMRMRDPlotWidgets


class ISMRMRDViewer(QMainWindow):
    def __init__(self,fileName,parent=None):
        super(ISMRMRDViewer,self).__init__(parent)

        # set icon
        #self.setWindowIcon(QIcon(os.path.join(os.path.dirname(sys.modules[__name__].__file__),'icon_256.ico')))
        self.setWindowIcon(QIcon(':/icon_256.ico'))

        # open ISMRMRD data file
        try:
            self.dset = ismrmrd.Dataset(fileName, '/dataset', False)
        except Exception as e:
            print('ERROR: Could not read file!')
            quit()
        
        # create table view
        self.tableModel = ISMRMRDTableModel.TableModel(self.dset)
        self.tableView = ISMRMRDTableView.TableView(self.tableModel)

        # create plot area
        self.plotWidget = ISMRMRDPlotWidgets.ISMRMRDPlotWidget(self.tableModel,self.tableView)

        # connect table selection change to plot update function
        selectionModel = self.tableView.selectionModel()
        selectionModel.selectionChanged.connect(self.plotWidget.updatePlot)

        # connect xml button click event
        self.plotWidget.btnXML.clicked.connect(self.showXML)

        # set layout and widgets
        _widget = QWidget()
        _layout = QVBoxLayout(_widget)
        self.splitter = QSplitter()
        self.splitter.setOrientation(Qt.Vertical)
        self.splitter.addWidget(self.tableView)
        self.splitter.addWidget(self.plotWidget)
        self.splitter.setStretchFactor(0,10)
        self.splitter.setStretchFactor(1,1)
        _layout.addWidget(self.splitter)
        self.setCentralWidget(_widget)

        self.setWindowTitle('ISMRM RAW DATA VIEWER: ' + fileName)
        self.setAttribute(Qt.WA_DeleteOnClose)
        
        # show window
        #self.resize(1000,600)
        #self.show()
        self.showMaximized()

    def showXML(self):
        # get the xml string
        xml = self.dset.read_xml_header()

        # write xml to temporary file
        tempFile = tempfile.gettempdir() + '\\ISMRMRDViewerTempXML.xml'
        with open(tempFile, "wb") as textFile:
            textFile.write(xml)

        # open xml viewer (browser)
        webbrowser.open(tempFile)

 
if __name__ == "__main__":
    app  = QApplication(sys.argv)
    
    # check command line arguments => filename
    if len(sys.argv) > 1:
        fileName = sys.argv[1]

        # create application window
        appWin = ISMRMRDViewer(fileName)
        app.exec_()
    else:
        print('ERROR: Expecting an ISMRMRD file as argument!')

