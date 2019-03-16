# Lumiere Editor interface for Cinema 4D, runs a PySide app with
# common pipeline functionality and grants access to the global
# Logiciel and Tubulent Vision asset library, the script requires
# PySide, Qt.py (https://github.com/mottosso/Qt.py) USD, MaterialX,
# Alembic, certifi, chardet, idna requests, urllib3, and requests
# python libaries to be placed in your local Maxon site-packages
# directory to function

import c4d, os, sys, json, loutils, requests
import MaterialX as mx

from Qt import QtWidgets, QtGui, QtCore

def main():
    cwd = os.path.dirname(os.path.abspath(__file__))

    #resp = requests.get('http://lumiere-editor.lolumi.com/api/asset?type=1')
    #print resp
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication(sys.argv)

    app.setQuitOnLastWindowClosed(True)
    qssFile = open(os.path.join(cwd,'lumi_editor_theme.qss')).read()
    lumiMain = QtWidgets.QWidget(windowTitle='Lumiere Editor')
    lumiMain.setStyleSheet(qssFile)
    # image contact sheet TODO: we'll load our assets forom the web this way, it'll probably
    # involve requests downloading them to a cache the user sets
    img_dir = 'H:/Documents/asset_library/10ravens/024_modern_dining_funiture/renders'

    hbox = QtWidgets.QHBoxLayout(lumiMain)


    glayout = QtWidgets.QGridLayout()
    scroll = QtWidgets.QScrollArea()
    assetArea = QtWidgets.QWidget()
    assetArea.resize(400, 400)
    assetArea.setLayout(glayout)
    
    row = 0
    col = 0
    for img in os.listdir(img_dir):
        img_path = os.path.join(img_dir, img)

        pixmap = QtGui.QPixmap(img_path)
        lbl = QtWidgets.QLabel()
        lbl.setPixmap(pixmap.scaled(64,64, QtCore.Qt.KeepAspectRatio))

        glayout.addWidget(lbl, row, col)
        col += 1
        if col == 4:
            col = 0
            row += 1

    scroll.setWidget(assetArea)
    layout = QtWidgets.QVBoxLayout()
    hbox.addWidget(scroll)
    hbox.addLayout(layout)
    exassetBtn = QtWidgets.QPushButton('Export Assets')
    bforaiBtn = QtWidgets.QPushButton('Arnold Swap Bitmap for Image')
    reobjpadBtn = QtWidgets.QPushButton('Rename Objs with padding')
    polybkBtn = QtWidgets.QPushButton('Polyselection Break')
    layout.addWidget(exassetBtn)
    layout.addWidget(bforaiBtn)
    layout.addWidget(reobjpadBtn)
    layout.addWidget(polybkBtn)

    reobjpadDiag = QtWidgets.QWidget(windowTitle='Rename Objs with padding')
    layout = QtWidgets.QVBoxLayout(reobjpadDiag)
    l1 = QtWidgets.QLabel('New Name')
    reobjpadnameEdit = QtWidgets.QLineEdit()
    l2 = QtWidgets.QLabel('Amount of padding')
    reobjpadpadEdit = QtWidgets.QLineEdit()
    reobjpadexecBtn = QtWidgets.QPushButton('Execute')
    layout.addWidget(l1)
    layout.addWidget(reobjpadnameEdit)
    layout.addWidget(l2)
    layout.addWidget(reobjpadpadEdit)
    layout.addWidget(reobjpadexecBtn)

    reobjpadexecBtn.clicked.connect(lambda: loutils.renameObjsPadding(doc, reobjpadnameEdit.text(), int(reobjpadpadEdit.text())))
    bforaiBtn.clicked.connect(loutils.swapC4DBitmapforArnoldImage)
    reobjpadBtn.clicked.connect(reobjpadDiag.show)
    exassetBtn.clicked.connect(lambda: loutils.exportAssets(doc))
    polybkBtn.clicked.connect(lambda: loutils.polyselectionbreak(doc, op))

    lumiMain.show()
    app.exec_()

if __name__=='__main__':
    main()