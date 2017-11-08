# -*- mode: python -*-

block_cipher = None


a = Analysis(['ISMRMRDViewer.py'],
             pathex=['C:\\Users\\dietricb\\Documents\\Visual Studio 2015\\Projects\\ISMRMRDViewer\\ISMRMRDViewer'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='ISMRMRDViewer',
          debug=False,
          strip=False,
          upx=True,
          console=False , icon='icon_256.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='ISMRMRDViewer')
