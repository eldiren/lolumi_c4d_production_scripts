import c4d
from c4d import gui
#Welcome to the world of Python
VrayAdvancedMaterial = 1020295
VrayShader = 1026701
VrayBitmap = 10
c4dMaterial = 5703
c4dBitmap = 5833

def walker(obj):
        if not obj: return

        elif obj.GetDown():
            return obj.GetDown()
        while obj.GetUp() and not obj.GetNext():
            obj = obj.GetUp()
        return obj.GetNext()

def MatCreator(matName,dColor,dBright,dBitmap,vAlpha):
    newmat = c4d.BaseMaterial(c4dMaterial)
    newmat.SetName(matName)
    newmat[c4d.MATERIAL_COLOR_COLOR] = dColor
    newmat[c4d.MATERIAL_COLOR_BRIGHTNESS] = dBright
    if dBitmap != None:
        newmat[c4d.MATERIAL_USE_COLOR]
        dShader = c4d.BaseShader(c4dBitmap)
        dShader[c4d.BITMAPSHADER_FILENAME] = dBitmap
        newmat[c4d.MATERIAL_COLOR_SHADER] = dShader
        newmat.InsertShader(dShader)
    if vAlpha != None:
        newmat[c4d.MATERIAL_ALPHA_INVERT] = 1
        newmat[c4d.MATERIAL_USE_ALPHA] = 1
        aShader = c4d.BaseShader(c4dBitmap)
        aShader[c4d.BITMAPSHADER_FILENAME] = vAlpha
        newmat[c4d.MATERIAL_ALPHA_SHADER] = aShader
        newmat.InsertShader(aShader)

    doc.AddUndo(c4d.UNDOTYPE_NEW,newmat)
    doc.InsertMaterial(newmat)
    return newmat

def MatLister(matList):
    
    for material in matList:
        dColor = c4d.Vector()
        dBright = 0.0
        dBitmap = None
        matName = ""
        vAlpha = None
        if material.GetType() == VrayAdvancedMaterial:
            matName = "c4d." + material.GetName()
            dColor = material[c4d.VRAYMATERIAL_COLOR1_COLOR]
            dBright = material[c4d.VRAYMATERIAL_COLOR1_MULT]
            
            if material[c4d.VRAYMATERIAL_COLOR1_SHADER]:
                if material[c4d.VRAYMATERIAL_COLOR1_SHADER].GetType() == VrayShader:
                    if material[c4d.VRAYMATERIAL_COLOR1_SHADER][c4d.VRAY_SHADERS_LIST] == VrayBitmap:
                        dBitmap = material[c4d.VRAYMATERIAL_COLOR1_SHADER][4999]
            
            if material[c4d.VRAYMATERIAL_TRANSP_SHADER]:
                if material[c4d.VRAYMATERIAL_TRANSP_SHADER].GetType() == VrayShader:   
                    if material[c4d.VRAYMATERIAL_TRANSP_SHADER][c4d.VRAY_SHADERS_LIST] == VrayBitmap:
                        vAlpha = material[c4d.VRAYMATERIAL_TRANSP_SHADER][4999]
            newMaterial = MatCreator(matName,dColor,dBright,dBitmap,vAlpha)
            obj = doc.GetFirstObject()
            while obj:
                tags = obj.GetTags()
                for tag in tags:
                    if tag.GetType() == 5616:
                        if tag[c4d.TEXTURETAG_MATERIAL] == material:
                            doc.AddUndo(c4d.UNDOTYPE_CHANGE,tag)
                            tag[c4d.TEXTURETAG_MATERIAL] = newMaterial

                obj = walker(obj)


def main():
    doc.StartUndo()
    materials = doc.GetMaterials()
    MatLister(materials)
    c4d.EventAdd()
    doc.EndUndo()

if __name__=='__main__':
    main()
