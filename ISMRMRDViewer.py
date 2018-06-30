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
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QSplitter, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import ismrmrd
import images_qr
import ISMRMRDTableView, ISMRMRDTableModel, ISMRMRDPlotWidgets

class ISMRMRDViewer(QMainWindow):
    def __init__(self,fileName,parent=None):
        super(ISMRMRDViewer,self).__init__(parent)

        # set icon
        self.setWindowIcon(QIcon(':/icon_256.ico'))

        # try to open ISMRMRD file
        try:
            self.dset = ismrmrd.Dataset(fileName, '/dataset', False)
        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowIcon(QIcon(':/icon_256.ico'))
            msg.setWindowTitle("ISMRMRD Viewer Error")
            msg.setText("Could not read specified file!")
            msg.exec_()
            quit()
        
        # create table model and view
        self.tableModel = ISMRMRDTableModel.TableModel(self.dset)
        self.tableView = ISMRMRDTableView.TableView(self.tableModel)

        # create plot area
        self.plotWidget = ISMRMRDPlotWidgets.ISMRMRDPlotWidget(self.tableModel,self.tableView)

        # connect table selection change event to plot update function
        self.tableView.selectionModel().selectionChanged.connect(self.plotWidget.updatePlot)

        # connect xml button click event to handler method
        self.plotWidget.btnXML.clicked.connect(self.showXML)

        # set window layout and widgets
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
        self.showMaximized()

    def showXML(self):
        # get the xml string
        xml = self.dset.read_xml_header()

        # write xml to temporary file
        tempFile = os.path.join(tempfile.gettempdir(),'ISMRMRDViewerTempXML.xml')
        with open(tempFile, "wb") as textFile:
            textFile.write(xml)

        # open xml viewer (web browser)
        webbrowser.open(tempFile)


# main application entry point
if __name__ == "__main__":
    app  = QApplication(sys.argv)
    
    # check command line arguments => we expect a filepath
    if len(sys.argv) > 1:
        fileName = sys.argv[1]

        # create application window
        appWin = ISMRMRDViewer(fileName)
        app.exec_()
    else:
        # show a message box to inform the user that he needs to supply a file
        # path as application argument
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowIcon(QIcon(':/icon_256.ico'))
        msg.setWindowTitle("ISMRMRD Viewer Error")
        msg.setText("No input file specified!")
        msg.exec_()