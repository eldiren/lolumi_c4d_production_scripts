# this script adds beauty and displacement prefixs to root materials
# in arnold shading networks and then exports the material in
# Arnold Scene Source format, this script is superceded by Objects
# To Documents

import c4d
from c4d import gui

ARNOLD_ASS_EXPORT = 1029993

C4DTOA_MSG_TYPE = 1000
C4DTOA_MSG_QUERY_SHADER_NETWORK = 1028
C4DTOA_MSG_RESP3 = 2013
C4DTOA_MSG_RESP4 = 2014

# from c4dtoa_symbols.h
ARNOLD_SHADER_NETWORK = 1033991

def QueryNetwork(material):
    msg = c4d.BaseContainer()
    msg.SetInt32(C4DTOA_MSG_TYPE, C4DTOA_MSG_QUERY_SHADER_NETWORK)
    material.Message(c4d.MSG_BASECONTAINER, msg)
    return msg

def main():
    matdoc = c4d.documents.BaseDocument()
    c4d.documents.InsertBaseDocument(matdoc)

    fileName = c4d.storage.LoadDialog(c4d.FILESELECTTYPE_ANYTHING, "Select export file...", c4d.FILESELECT_SAVE)
    matdoc.SetDocumentName(fileName)
    mat = doc.GetFirstMaterial()
    
    while mat:
        newmat = mat.GetClone()
        if newmat.GetType() == ARNOLD_SHADER_NETWORK:
            # query network
            network = QueryNetwork(newmat)
            # get beauty and displacement and add prefixs so we can identify them in
            # other programs
            beautyShader = network.GetLink(C4DTOA_MSG_RESP3)
            dispShader = network.GetLink(C4DTOA_MSG_RESP4)
            if beautyShader:
                beautyShader.SetName("beauty|" + beautyShader.GetName())
            
            if dispShader:
                dispShader.SetName("displacement|" + dispShader.GetName() )
            
        matdoc.InsertMaterial(newmat)
        obj = c4d.BaseObject(c4d.Opolygon)
        obj.SetName(newmat.GetName())
        tag = c4d.BaseTag(c4d.Ttexture)
        tag[c4d.TEXTURETAG_MATERIAL] = newmat
        
        obj.InsertTag(tag)
        matdoc.InsertObject(obj)
        
        mat = mat.GetNext()
     
    options = c4d.BaseContainer()
    options.SetFilename(0, fileName.decode("utf-8"))
    options.SetInt32(6, 0)
    options.SetInt32(7, 0)
    matdoc.GetSettingsInstance(c4d.DOCUMENTSETTINGS_DOCUMENT).SetContainer(ARNOLD_ASS_EXPORT, options)
 
    c4d.CallCommand(ARNOLD_ASS_EXPORT)
        
    c4d.documents.SetActiveDocument(matdoc)
    c4d.EventAdd()
    
    c4d.documents.KillDocument(matdoc)
                           
if __name__=='__main__':
    main()
