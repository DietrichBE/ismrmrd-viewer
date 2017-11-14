# ISMRMRD-Viewer
Simple python based viewing application for the [ISMRM raw data format](https://github.com/ismrmrd/ismrmrd).

ISMRMRDViewer.py is the main application entry point: `python ISMRMRDViewer.py yourData.h5`

![Main application window](https://user-images.githubusercontent.com/26109767/32781305-d89ccf00-c944-11e7-8a5d-d32514d0d3ad.png)

## Prepare for distribution
Create pyqt resource file (icons and images):
```
pyrcc5 -o images_qr.py images.qrc
```

Package using pyinstaller:
```
pyinstaller.exe --noconsole --windowed --icon=icon_256.ico .\ISMRMRDViewer.py
```
