# ISMRMRD-Viewer
ISMRM Raw Data Viewer

## Prepare for distribution

* Create pyqt resource file (icons and images):
```
pyrcc5 -o images_qr.py images.qrc
```

* Package using pyinstaller
```
pyinstaller.exe --noconsole --windowed --icon=icon_256.ico .\ISMRMRDViewer.py
```