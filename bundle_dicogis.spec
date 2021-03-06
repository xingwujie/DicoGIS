# -*- mode: python -*-

block_cipher = None

from ConfigParser import SafeConfigParser
from os import path

# ------------ Initial settings ----------------------------------------------
config = SafeConfigParser()
config.read(path.realpath("options_TPL.ini"))
config.set("config", "basics", "filters", "database", "proxy", "isogeo")
with open(path.realpath("build\\options.ini"), "wb") as configfile:
    config.write(configfile)
# ----------------------------------------------------------------------------

added_files = [('build\\settings.ini', '.'),
               ('LICENSE', '.'),
               ('README.md', '.'),
               ('i18n\\isogeo2office.pot', 'i18n'),
               ('i18n\\fr_FR\\LC_MESSAGES\\isogeo2office.mo', 'i18n\\fr_FR\\LC_MESSAGES'),
               ('templates\\template_Isogeo.docx', 'templates'),
               ('output\\README.md', 'output'),
               ('DicoGIS.ico', '.'),
               ('data\\img\\DicoGIS_logo.gif', 'data\\img'),
               ('data\\locale\\lang_EN.xml', 'data\\locale'),
               ('data\\locale\\lang_FR.xml', 'data\\locale'),
               ('data\\locale\\lang_ES.xml', 'data\\locale'),
              ]


a = Analysis(['DicoGIS.py'],
             pathex=['C:\\Users\\julien.moura\\Documents\\GitHub\\Perso\\DicoGIS'],
             binaries=None,
             datas=added_files,
             hiddenimports=[],
             hookspath=["hooks"],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

pyz = PYZ(a.pure,
          a.zipped_data,
          cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='DicoGIS',
          debug=False,
          strip=False,
          upx=False,
          console=False,
          icon='DicoGIS.ico',
          windowed=True,
          version='bundle_version.txt')

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=False,
               name='DicoGIS',
               icon='dta\\img\\DicoGIS_logo.gif'
               )
