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

import numpy as np
import pyqtgraph as pg
import ismrmrd
from PyQt5.QtWidgets import QWidget, QComboBox, QPushButton, QHBoxLayout, QVBoxLayout, QLabel

class ISMRMRDPlotWidget(QWidget):
    def __init__(self,tableModel,tableView,parent=None):
        super(ISMRMRDPlotWidget,self).__init__(parent)

        self.tableModel = tableModel
        self.tableView = tableView

        # coil data plot selection drop down
        self.rawCB = QComboBox()
        self.rawCB.addItem('')
        self.rawCB.addItem('Magnitude')
        self.rawCB.addItem('Real')
        self.rawCB.addItem('Imag')
        self.rawCB.addItem('FFT (magnitude)')
        self.rawCB.addItem('Phase')
        self.rawCB.addItem('Phase (unwrapped)')
        self.rawCB.setCurrentIndex(1)

        # trajectory plot selection drop down
        self.trajCB = QComboBox()
        self.trajCB.addItem('')
        self.trajCB.addItem('Magnitude')
        self.trajCB.addItem('FFT (magnitude)')
        self.trajCB.setCurrentIndex(1)

        # show XML button
        self.btnXML = QPushButton('Show XML header')

        # control bar layout
        self.ctrlBarBox = QHBoxLayout()
        self.ctrlBarBox.setContentsMargins(0,0,0,0)
        self.ctrlBarBox.addWidget(QLabel('Raw plot:'))
        self.ctrlBarBox.addWidget(self.rawCB)
        self.ctrlBarBox.addWidget(QLabel('Trajectory plot:'))
        self.ctrlBarBox.addWidget(self.trajCB)
        self.ctrlBarBox.addWidget(QLabel('  '))
        self.ctrlBarBox.addWidget(self.btnXML)
        self.ctrlBarBox.addStretch(1)
        
        # create raw and trajectory plot widgets
        self.rawPlot = pg.PlotWidget()
        self.rawPlot.hide()
        self.trajPlot = pg.PlotWidget()
        self.trajPlot.hide()

        # create and set overall layout (vertical box)
        vbox = QVBoxLayout()
        vbox.setContentsMargins(0,0,0,0)
        vbox.addLayout(self.ctrlBarBox)
        vbox.addWidget(self.rawPlot,1)
        vbox.addWidget(self.trajPlot,1)
        self.setLayout(vbox)

        self.resize(self.sizeHint())
        tabelHeight = self.tableView.height()
        self.rawPlot.setMinimumHeight(tabelHeight/2)
        self.trajPlot.setMinimumHeight(tabelHeight/2)

        # connect combobox change events to plot update function
        self.rawCB.currentIndexChanged.connect(self.updatePlot)
        self.trajCB.currentIndexChanged.connect(self.updatePlot)


    def updatePlot(self, *args):

        rawIndex = self.rawCB.currentIndex()
        trajIndex = self.trajCB.currentIndex()

        if rawIndex != 0 or trajIndex != 0:
            # get currently selected row and column from table view
            row = self.tableView.currentIndex().row()
            col = self.tableView.currentIndex().column()
            #print('(' + str(row) + ',' + str(col) + ')')

            # read corresponding acquisiton from table model buffer
            aq = ismrmrd.Acquisition(self.tableModel.rbuffer.getCell(row)['head'])

        # update raw data plot
        if rawIndex != 0:
            self.rawPlot.show()

            # get the data
            data = self.tableModel.rbuffer.getCell(row)['data'].view(np.complex64).reshape((aq.active_channels, aq.number_of_samples))[:]
        
            # apply visualization selection
            if self.rawCB.currentText() == 'Real':
                dataOut = np.real(data)
            elif self.rawCB.currentText() == 'Imag':
                dataOut = np.imag(data)
            elif self.rawCB.currentText() == 'FFT (magnitude)':
                dataOut = abs(np.fft.fftshift(np.fft.fft(data)))
            elif self.rawCB.currentText() == 'Phase':
                dataOut = np.angle(data)
            elif self.rawCB.currentText() == 'Phase (unwrapped)':
                dataOut = np.unwrap(np.angle(data))
            else:
                dataOut = abs(data)
        
            # remove old plots and legend entries
            for item in self.rawPlot.items():
                self.rawPlot.removeItem(item)
            try:
                self.rawPlot.legend.scene().removeItem(self.rawPlot.legend)
            except Exception as e:
                print(e)

            #self.plotWidget.rawPlot.clear()
            self.rawPlot.setTitle('Coil data')
            self.rawPlot.legend = self.rawPlot.addLegend()

            for ind in range(0,len(dataOut)):
                color = pg.intColor(ind)
                self.rawPlot.plot(dataOut[ind,:],pen=pg.mkPen(color),name=' Channel ' + str(ind))
        else:
            self.rawPlot.hide()


        # update trajectory plot
        if self.trajCB.currentIndex() != 0 and aq.traj.size > 0:
            self.trajPlot.show()

            # get the data
            data = self.tableModel.rbuffer.getCell(row)['traj'].reshape((aq.number_of_samples,aq.trajectory_dimensions))[:]
        
            # apply visualization selection
            if self.trajCB.currentText() == 'FFT (magnitude)':
                dataOut = abs(np.fft.fft(data))
            else:
                dataOut = data
        
            # remove old plots and legend entries
            for item in self.trajPlot.items():
                self.trajPlot.removeItem(item)
            try:
                self.trajPlot.legend.scene().removeItem(self.trajPlot.legend)
            except Exception as e:
                print(e)

            #self.plotWidget.trajPlot.clear()
            self.trajPlot.setTitle('Trajectory data')
            self.trajPlot.legend = self.trajPlot.addLegend()

            for ind in range(0,dataOut.shape[1]):
                color = pg.intColor(ind)
                self.trajPlot.plot(dataOut[:,ind],pen=pg.mkPen(color),name=' Channel ' + str(ind))
        else:
            self.trajPlot.hide()

