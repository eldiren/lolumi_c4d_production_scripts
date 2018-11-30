# Lumiere Editor interface for Cinema 4D, runs a PySide app with
# common pipeline functionality and grants access to the global
# Logiciel and Tubulent Vision asset library, the script requires
# PySide, USD, MaterialX, Alembic, certifi, chardet, idna
# requests, urllib3, and requests python libaries to be placed in
# your local Maxon site-packages directory to function
 
import c4d, os, sys, json, loutils, requests
import MaterialX as mx

from Qt import QtWidgets
    
def main():
    resp = requests.get('http://lumiere-editor.lolumi.com/api/asset?type=1')
    print resp
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication(sys.argv)
    
    app.setQuitOnLastWindowClosed(True)
    lumiMain = QtWidgets.QWidget(windowTitle='Lumiere Editor')
    layout = QtWidgets.QVBoxLayout(lumiMain)
    exassetBtn = QtWidgets.QPushButton('Export Assets')
    bforaiBtn = QtWidgets.QPushButton('Arnold Swap Bitmap for Image')
    reobjpadBtn = QtWidgets.QPushButton('Rename Objs with padding')
    layout.addWidget(exassetBtn)
    layout.addWidget(bforaiBtn)
    layout.addWidget(reobjpadBtn)
    
    
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
    
    lumiMain.show()
    app.exec_()

if __name__=='__main__':
    main()
