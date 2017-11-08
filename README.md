# ISMRMRD-Viewer
ISMRM Raw Data Viewer

Create pyqt resource file (icons and images):
pyrcc5 -o images_qr.py images.qrc

Compile for distribution:
pyinstaller.exe --noconsole --windowed --icon=icon_256.ico .\ISMRMRDViewer.py

