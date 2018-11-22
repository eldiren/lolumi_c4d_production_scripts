import c4d
import os
from c4d import gui

VrayAdvancedMaterial = 1020295
VrayShader = 1026701
VrayBitmap = 10
c4dMaterial = 5703
c4dBitmap = 5833

# from api/util/Constants.h
C4DTOA_MSG_TYPE = 1000
C4DTOA_MSG_PARAM1 = 2001
C4DTOA_MSG_PARAM2 = 2002
C4DTOA_MSG_PARAM3 = 2003
C4DTOA_MSG_PARAM4 = 2004
C4DTOA_MSG_RESP1 = 2011
C4DTOA_MSG_ADD_SHADER = 1029
C4DTOA_MSG_ADD_CONNECTION = 1031
C4DTOA_MSG_CONNECT_ROOT_SHADER = 1033

# from c4dtoa_symbols.h
ARNOLD_SHADER_NETWORK = 1033991
ARNOLD_SHADER_GV = 1033990

# from api/util/ArnolShaderNetworkUtil.h
ARNOLD_BEAUTY_PORT_ID = 537905099

# from api/util/NodeIds.h
C4DAIN_STANDARD = 1760354454
C4DAIN_IMAGE = 262700200
C4DAIN_BUMP2D = 184848913

# from res/description/ainode_standard.h
C4DAIP_STANDARD_KD_COLOR = 338192719
C4DAIP_STANDARD_KD = 1284763283
C4DAIP_STANDARD_OPACITY = 1721707107
C4DAIP_STANDARD_SPECULAR_FRESNEL = 242503183
C4DAIP_STANDARD_KS = 1284763298
C4DAIP_STANDARD_KS_COLOR = 1853957632
C4DAIP_STANDARD_SPECULAR_ROUGHNESS = 1998328352

# from res/description/ainode_bump2d.h
C4DAIP_BUMP2D_BUMP_MAP = 1722542866
C4DAIP_BUMP2D_BUMP_HEIGHT = 149592681
C4DAIP_BUMP2D_SHADER = 1367502316

# from res/description/ainode_image.h
C4DAIP_IMAGE_FILENAME = 1737748425

def CreateArnoldShader(material, nodeId, posx, posy):
    msg = c4d.BaseContainer()
    msg.SetInt32(C4DTOA_MSG_TYPE, C4DTOA_MSG_ADD_SHADER)
    msg.SetInt32(C4DTOA_MSG_PARAM1, ARNOLD_SHADER_GV)
    msg.SetInt32(C4DTOA_MSG_PARAM2, nodeId)
    msg.SetInt32(C4DTOA_MSG_PARAM3, posx)
    msg.SetInt32(C4DTOA_MSG_PARAM4, posy)
    material.Message(c4d.MSG_BASECONTAINER, msg)
    return msg.GetLink(C4DTOA_MSG_RESP1)

def AddConnection(material, srcNode, dstNode, dstPortId):
    msg = c4d.BaseContainer()
    msg.SetInt32(C4DTOA_MSG_TYPE, C4DTOA_MSG_ADD_CONNECTION)
    msg.SetLink(C4DTOA_MSG_PARAM1, srcNode)
    msg.SetInt32(C4DTOA_MSG_PARAM2, 0)
    msg.SetLink(C4DTOA_MSG_PARAM3, dstNode)
    msg.SetInt32(C4DTOA_MSG_PARAM4, dstPortId)
    material.Message(c4d.MSG_BASECONTAINER, msg)
    return msg.GetBool(C4DTOA_MSG_RESP1)

def SetRootShader(material, shader, rootPortId):
    msg = c4d.BaseContainer()
    msg.SetInt32(C4DTOA_MSG_TYPE, C4DTOA_MSG_CONNECT_ROOT_SHADER)
    msg.SetLink(C4DTOA_MSG_PARAM1, shader)
    msg.SetInt32(C4DTOA_MSG_PARAM2, 0)
    msg.SetInt32(C4DTOA_MSG_PARAM3, rootPortId)
    material.Message(c4d.MSG_BASECONTAINER, msg)
    return msg.GetBool(C4DTOA_MSG_RESP1)
    
def walker(obj):
    if not obj: return

    elif obj.GetDown():
        return obj.GetDown()
    while obj.GetUp() and not obj.GetNext():
        obj = obj.GetUp()
    return obj.GetNext()

def MatCreator(matName,dColor,dBright,dBitmap,sColor,sBright,sRough,sBitmap,vAlpha,bBitmap,bHeight):
    newmat = c4d.BaseMaterial(ARNOLD_SHADER_NETWORK)
    newmat.SetName(matName)
    
     # create root standard shaders
    standard = CreateArnoldShader(newmat, C4DAIN_STANDARD, 150, 100)
    if standard is None:
        raise Exception("Failed to create standard shader")
    standard.SetName("standard")
    SetRootShader(newmat, standard, ARNOLD_BEAUTY_PORT_ID)
    
    # set diffuse color and weight
    standard.GetOpContainerInstance().SetVector(C4DAIP_STANDARD_KD_COLOR, dColor)
    standard.GetOpContainerInstance().SetFloat(C4DAIP_STANDARD_KD, dBright)

    # set specular color, weight, and roughness
    standard.GetOpContainerInstance().SetVector(C4DAIP_STANDARD_KS_COLOR, sColor)
    standard.GetOpContainerInstance().SetFloat(C4DAIP_STANDARD_KS, sBright)
    standard.GetOpContainerInstance().SetFloat(C4DAIP_STANDARD_SPECULAR_ROUGHNESS, sRough)
        
    # set fresnel on
    standard.GetOpContainerInstance().SetBool(C4DAIP_STANDARD_SPECULAR_FRESNEL, True)
    
    if dBitmap != None:
         # image shader
        image = CreateArnoldShader(newmat, C4DAIN_IMAGE, 0, 50)
        if image is None:
            raise Exception("Failed to create image shader")
        
        # setup texture path
        texturePath = dBitmap
        if texturePath:
            image.GetOpContainerInstance().SetFilename(C4DAIP_IMAGE_FILENAME, texturePath)
            image.SetName("diff")
        
        # connect to standard diffuse color
        AddConnection(newmat, image, standard, C4DAIP_STANDARD_KD_COLOR)    
        
    if sBitmap != None:
         # image shader
        image = CreateArnoldShader(newmat, C4DAIN_IMAGE, 0, 50)
        if image is None:
            raise Exception("Failed to create image shader")
        
        # setup texture path
        texturePath = sBitmap
        if texturePath:
            image.GetOpContainerInstance().SetFilename(C4DAIP_IMAGE_FILENAME, texturePath)
            image.SetName("spec")
        
        # connect to standard specular color
        AddConnection(newmat, image, standard, C4DAIP_STANDARD_KS_COLOR)    

    if vAlpha != None:
         # image shader
        image = CreateArnoldShader(newmat, C4DAIN_IMAGE, 0, 50)
        if image is None:
            raise Exception("Failed to create image shader")
        
        # setup texture path
        texturePath = vAlpha
        if texturePath:
            image.GetOpContainerInstance().SetFilename(C4DAIP_IMAGE_FILENAME, texturePath)
            image.SetName("opac")
        
        # connect to standard opacity color
        AddConnection(newmat, image, standard, C4DAIP_STANDARD_OPACITY)        
    
    if bBitmap != None:
         # image shader
        image = CreateArnoldShader(newmat, C4DAIN_IMAGE, 0, 50)
        if image is None:
            raise Exception("Failed to create image shader")
        
        bump = CreateArnoldShader(newmat, C4DAIN_BUMP2D, 0, 50)
        bump.SetName("bump2d")
        SetRootShader(newmat, bump, ARNOLD_BEAUTY_PORT_ID)
        AddConnection(newmat, standard, bump, C4DAIP_BUMP2D_SHADER)
        
        # setup texture path
        texturePath = bBitmap
        if texturePath:
            image.GetOpContainerInstance().SetFilename(C4DAIP_IMAGE_FILENAME, texturePath)
            image.SetName("bump")
        
        # connect to bump map
        AddConnection(newmat, image, bump, C4DAIP_BUMP2D_BUMP_MAP)        

    doc.AddUndo(c4d.UNDOTYPE_NEW,newmat)
    doc.InsertMaterial(newmat)
    return newmat

def deleteVrayMats():
    materials = doc.GetMaterials()
    
    for material in reversed(materials):
        if material.GetType() == VrayAdvancedMaterial:
             material.Remove()
  
def MatLister(matList):
    
    for material in matList:
        dColor = c4d.Vector()
        dBright = 0.0
        dBitmap = None
        matName = ""
        vAlpha = None
        sBitmap = None
        sColor = c4d.Vector()
        sRough = 0.0
        sBright = 0.0
        bBitmap = None
        bHeight = 0.0
        
        if material.GetType() == VrayAdvancedMaterial:
            matName = material.GetName() + "_arnold_mat"
            dColor = material[c4d.VRAYMATERIAL_COLOR1_COLOR]
            dBright = material[c4d.VRAYMATERIAL_COLOR1_MULT]
            sColor = material[c4d.VRAYMATERIAL_SPECULAR1_COLOR]
            sRough = 1 - material[c4d.VRAYMATERIAL_SPECULAR1_HIGHLIGHTGLOSS] # Arnold is inverted from VRay
            sBright = material[c4d.VRAYMATERIAL_SPECULAR1_COLOR_MULT]
            bHeight = material[c4d.VRAYMATERIAL_BUMP_BUMPTEXMULT]
            
            if material[c4d.VRAYMATERIAL_COLOR1_SHADER]:
                # check if the shader is a C4D Bitmap
                if material[c4d.VRAYMATERIAL_COLOR1_SHADER].GetType() == c4d.Xbitmap:
                    dBitmap = material[c4d.VRAYMATERIAL_COLOR1_SHADER].GetDataInstance().GetFilename(c4d.BITMAPSHADER_FILENAME)
                
                # check if the shader is a VrayBitmap    
                if material[c4d.VRAYMATERIAL_COLOR1_SHADER].GetType() == VrayShader:
                    if material[c4d.VRAYMATERIAL_COLOR1_SHADER][c4d.VRAY_SHADERS_LIST] == VrayBitmap:
                        dBitmap = material[c4d.VRAYMATERIAL_COLOR1_SHADER][4999]
            
            if material[c4d.VRAYMATERIAL_SPECULAR1_SHADER]:
                # check if the shader is a C4D Bitmap
                if material[c4d.VRAYMATERIAL_SPECULAR1_SHADER].GetType() == c4d.Xbitmap:
                    sBitmap = material[c4d.VRAYMATERIAL_SPECULAR1_SHADER].GetDataInstance().GetFilename(c4d.BITMAPSHADER_FILENAME)
                
                # check if the shader is a VrayBitmap
                if material[c4d.VRAYMATERIAL_SPECULAR1_SHADER].GetType() == VrayShader:
                    if material[c4d.VRAYMATERIAL_SPECULAR1_SHADER][c4d.VRAY_SHADERS_LIST] == VrayBitmap:
                        sBitmap = material[c4d.VRAYMATERIAL_SPECULAR1_SHADER][4999]  
                        
            if material[c4d.VRAYMATERIAL_TRANSP_SHADER]:
                if material[c4d.VRAYMATERIAL_TRANSP_SHADER].GetType() == c4d.Xbitmap:
                    vAlpha = material[c4d.VRAYMATERIAL_TRANSP_SHADER].GetDataInstance().GetFilename(c4d.BITMAPSHADER_FILENAME)
                    
                if material[c4d.VRAYMATERIAL_TRANSP_SHADER].GetType() == VrayShader:   
                    if material[c4d.VRAYMATERIAL_TRANSP_SHADER][c4d.VRAY_SHADERS_LIST] == VrayBitmap:
                        vAlpha = material[c4d.VRAYMATERIAL_TRANSP_SHADER][4999]
                        
            if material[c4d.VRAYMATERIAL_BUMP_SHADER]:
                # check if the shader is a C4D Bitmap
                if material[c4d.VRAYMATERIAL_BUMP_SHADER].GetType() == c4d.Xbitmap:
                    bBitmap = material[c4d.VRAYMATERIAL_BUMP_SHADER].GetDataInstance().GetFilename(c4d.BITMAPSHADER_FILENAME)
                
                # check if the shader is a VrayBitmap    
                if material[c4d.VRAYMATERIAL_BUMP_SHADER].GetType() == VrayShader:
                    if material[c4d.VRAYMATERIAL_BUMP_SHADER][c4d.VRAY_SHADERS_LIST] == VrayBitmap:
                        bBitmap = material[c4d.VRAYMATERIAL_BUMP_SHADER][4999]
                        
            newMaterial = MatCreator(matName,dColor,dBright,dBitmap,sColor,sBright,sRough,sBitmap,vAlpha,bBitmap,bHeight)
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
    deleteVrayMats()
    c4d.EventAdd()
    doc.EndUndo()

if __name__=='__main__':
    main()
