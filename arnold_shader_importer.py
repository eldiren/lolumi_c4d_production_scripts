###########################################
# C4D script to read shaders from an ASS file
# and create Arnold Shader Network materials.
#
# Copyright 2016 Solid Angle. All Rights Reserved.
###########################################

import os, sys, ctypes, string
import c4d
from c4d import gui

# global setup
PLUGIN_PATH = os.path.join(c4d.storage.GeGetStartupPath(), "plugins", "C4DtoA")
ARNOLD_PLUGIN_PATH = os.environ.get("ARNOLD_PLUGIN_PATH")
USE_RELATIVE_PATHS = True
BEAUTY_ROOT_POSX = 250
BEAUTY_ROOT_POSY = 150
DISPLACEMENT_ROOT_POSX = 250
DISPLACEMENT_ROOT_POSY = 300
POSX_OFFSET = 200
POSY_OFFSET = 50

# load Arnold python modules
arnoldPythonPath = os.path.join(PLUGIN_PATH, "arnold", "python")
sys.path.append(arnoldPythonPath)
from arnold import *

# from c4dtoa_symbols.h
ARNOLD_SHADER_NETWORK = 1033991
ARNOLD_SHADER_GV = 1033990
ARNOLD_SCENE_HOOK = 1032309

# from api/util/Constants.h
C4DTOA_MSG_TYPE = 1000
C4DTOA_MSG_PARAM1 = 2001
C4DTOA_MSG_PARAM2 = 2002
C4DTOA_MSG_PARAM3 = 2003
C4DTOA_MSG_PARAM4 = 2004
C4DTOA_MSG_RESP1 = 2011
C4DTOA_MSG_RESP2 = 2012
C4DTOA_MSG_RESP3 = 2013
C4DTOA_MSG_RESP4 = 2014

C4DTOA_MSG_ADD_SHADER = 1029
C4DTOA_MSG_ADD_CONNECTION = 1031
C4DTOA_MSG_CONNECT_ROOT_SHADER = 1033
C4DTOA_MSG_COLOR_CORRECTION = 1035
C4DTOA_MSG_AIBEGIN = 1036
C4DTOA_MSG_AIEND = 1037

# from api/util/ArnolShaderNetworkUtil.h
ARNOLD_BEAUTY_PORT_ID = 537905099
ARNOLD_DISPLACEMENT_PORT_ID = 537905100

###
# Class to represent an Arnold node. Makes AtNode pointer hashable.
###
class ArnoldNode:
    
    def __init__(self, n):
        self.node = None
        self.nodePtr = 0
        if not n: return

        if hasattr(n, "contents"):
            self.node = n
            self.nodePtr = ctypes.addressof(n.contents)
        else:
            self.nodePtr = n
            self.node = NullToNone(n, POINTER(AtNode))
            
        if self.node:
            self.node = self.node.contents
    
    def IsValid(self):
        return self.node is not None
    
    def GetNodeEntry(self):
        return AiNodeGetNodeEntry(self.node)
    
    def GetNodeEntryName(self):
        return AiNodeEntryGetName(self.GetNodeEntry())
    
    def GetName(self):
        return AiNodeGetName(self.node)
        
    def __hash__(self):
        return self.nodePtr
    
    def  __eq__(self, other):
        return isinstance(other, ArnoldNode) and self.nodePtr == other.nodePtr

    def  __ne__(self, other):
        return not self.__eq__(other)
    
    def  __cmp__(self, other):
        if not isinstance(other, ArnoldNode): return -1
        if self.nodePtr == other.nodePtr: return 0
        if self.nodePtr < other.nodePtr: return -1
        return 1
    
###
# Class to represent a link between shaders.
###    
class ShaderLink:
    
    def __init__(self, param, link):
        self.param = param
        self.link = link

###
# Prints an error message to the console.
# If critical is True the script will stop.
###
def PrintError(msg, critical=False):
    print "ArnoldShaderImporter | [ERROR] %s" % msg
    if critical:
        raise Exception(msg)

###
# Prints a warning message to the console.
###
def PrintWarning(msg):
    print "ArnoldShaderImporter | [WARNING] %s" % msg
   
###
# Prints an info message to the console.
###   
def PrintInfo(msg):
    print "ArnoldShaderImporter | %s" % msg

###
# Hash function to generate C4D ids.
###
def hashid(name):
    if name is None: return 0
     
    h = 5381
    for c in name:
        h = (h << 5) + h + ord(c)
    h = ctypes.c_int32(h).value
    if h < 0: h = -h
    return h

###
# Corrects the given color by the C4D input color profile.
###
def ColorCorrection(inputColor):
    inputColorProfile = doc.GetSettingsInstance(c4d.DOCUMENTSETTINGS_DOCUMENT).GetInt32(c4d.DOCUMENT_COLORPROFILE)
    if inputColorProfile == c4d.DOCUMENT_COLORPROFILE_LINEAR:
        return inputColor

    arnoldSceneHook = doc.FindSceneHook(ARNOLD_SCENE_HOOK)
    if not arnoldSceneHook:
        return inputColor
    
    msg = c4d.BaseContainer()
    msg.SetInt32(C4DTOA_MSG_TYPE, C4DTOA_MSG_COLOR_CORRECTION)
    msg.SetVector(C4DTOA_MSG_PARAM1, inputColor)
    msg.SetInt32(C4DTOA_MSG_PARAM2, c4d.DOCUMENT_COLORPROFILE_LINEAR)
    msg.SetInt32(C4DTOA_MSG_PARAM3, c4d.DOCUMENT_COLORPROFILE_SRGB)
    arnoldSceneHook.Message(c4d.MSG_BASECONTAINER, msg)
    
    return msg.GetVector(C4DTOA_MSG_RESP1)

###
# Opens the Arnold universe.
###
def Begin():
    arnoldSceneHook = doc.FindSceneHook(ARNOLD_SCENE_HOOK)
    if not arnoldSceneHook:
        return
    
    msg = c4d.BaseContainer()
    msg.SetInt32(C4DTOA_MSG_TYPE, C4DTOA_MSG_AIBEGIN)
    arnoldSceneHook.Message(c4d.MSG_BASECONTAINER, msg)

###
# Closes the Arnold universe.
###
def End():
    arnoldSceneHook = doc.FindSceneHook(ARNOLD_SCENE_HOOK)
    if not arnoldSceneHook:
        return
    
    msg = c4d.BaseContainer()
    msg.SetInt32(C4DTOA_MSG_TYPE, C4DTOA_MSG_AIEND)
    arnoldSceneHook.Message(c4d.MSG_BASECONTAINER, msg)

RAMP_FLOAT_ID = hashid("ramp_float")
RAMP_RGB_ID = hashid("ramp_rgb")

###
# Custom import logic of the ramp_float shader.
###
def SetupRampFloat(shaderNode, arnoldShader):
    # from ainode_ramp_float.h
    C4DAI_RAMP_FLOAT_SPLINE = 1100

    if shaderNode is None or arnoldShader is None:
        return

    valueArrayPtr = AiNodeGetArray(arnoldShader.node, "value")
    positionArrayPtr = AiNodeGetArray(arnoldShader.node, "position")
    if valueArrayPtr is None or positionArrayPtr is None:
        return

    valueArray = NullToNone(valueArrayPtr, POINTER(AtArray)).contents
    positionArray = NullToNone(positionArrayPtr, POINTER(AtArray)).contents

    spline = c4d.SplineData()
    spline.DeleteAllPoints()
    for i in range(0, positionArray.nelements):
        value = AiArrayGetFlt(valueArray, i)
        position = AiArrayGetFlt(positionArray, i)
        spline.InsertKnot(position, value)

    shaderNode.GetOpContainerInstance().SetData(C4DAI_RAMP_FLOAT_SPLINE, spline)

###
# Custom import logic of the ramp_rgb shader.
###
def SetupRampRgb(shaderNode, arnoldShader):
    # from ainode_ramp_rgb.h
    C4DAI_RAMP_RGB_GRADIENT = 1100

    if shaderNode is None or arnoldShader is None:
        return

    colorArrayPtr = AiNodeGetArray(arnoldShader.node, "color")
    positionArrayPtr = AiNodeGetArray(arnoldShader.node, "position")
    if colorArrayPtr is None or positionArrayPtr is None:
        return

    colorArray = NullToNone(colorArrayPtr, POINTER(AtArray)).contents
    positionArray = NullToNone(positionArrayPtr, POINTER(AtArray)).contents

    gradient = c4d.Gradient()
    gradient.FlushKnots()
    for i in range(0, positionArray.nelements):
        rgb = AiArrayGetRGB(colorArray, i)
        r = float(int(rgb.r * 255.0 + 0.5)) / 255.0
        g = float(int(rgb.g * 255.0 + 0.5)) / 255.0
        b = float(int(rgb.b * 255.0 + 0.5)) / 255.0
        shader_gamma = AiNodeGetFlt(AiUniverseGetOptions(), "shader_gamma")
        if shader_gamma == 1.0:
            color = ColorCorrection(c4d.Vector(r, g, b))
        else:           
            color = c4d.Vector(r, g, b)
        position = AiArrayGetFlt(positionArray, i)
        gradient.InsertKnot(color, 1.0, position)

    shaderNode.GetOpContainerInstance().SetData(C4DAI_RAMP_RGB_GRADIENT, gradient)

###
# Creates a shader in the network by the given Arnold node.
# Sets all parameters.
###
def CreateShader(material, shader, posx, posy):
    if shader is None: 
        return None

    nodeEntry = shader.GetNodeEntry()
    nodeEntryName = shader.GetNodeEntryName()
    nodeId = hashid(nodeEntryName)
    
    msg = c4d.BaseContainer()
    msg.SetInt32(C4DTOA_MSG_TYPE, C4DTOA_MSG_ADD_SHADER)
    msg.SetInt32(C4DTOA_MSG_PARAM1, ARNOLD_SHADER_GV)
    msg.SetInt32(C4DTOA_MSG_PARAM2, nodeId)
    msg.SetInt32(C4DTOA_MSG_PARAM3, posx)
    msg.SetInt32(C4DTOA_MSG_PARAM4, posy)
    material.Message(c4d.MSG_BASECONTAINER, msg)
    shaderNode = msg.GetLink(C4DTOA_MSG_RESP1)
    
    if shaderNode is None:
        return None
    
    # set name
    name = shader.GetName()
    if name:
        name = name.split('|')[-1]
        shaderNode.SetName(name)
    
    # set parameters
    data = shaderNode.GetOpContainerInstance()
    piter = AiNodeEntryGetParamIterator(nodeEntry)
    while not AiParamIteratorFinished(piter):
        pentry = AiParamIteratorGetNext(piter)
        param = AiParamGetName(pentry)
        paramId = hashid("%s.%s" % (nodeEntryName, param))
        paramType = AiParamGetType(pentry)
        
        if paramType == AI_TYPE_BYTE:
            data.SetInt32(paramId, AiNodeGetByte(shader.node, param))
        if paramType == AI_TYPE_INT:
            data.SetInt32(paramId, AiNodeGetInt(shader.node, param))
        if paramType == AI_TYPE_UINT:
            data.SetInt32(paramId, AiNodeGetUInt(shader.node, param))
        if paramType == AI_TYPE_BOOLEAN:
            data.SetBool(paramId, AiNodeGetBool(shader.node, param))
        if paramType == AI_TYPE_FLOAT:
            v = AiNodeGetFlt(shader.node, param)
            c4dGuiType = ctypes.c_int(-1)
            AiMetaDataGetInt(nodeEntry, param, "c4d.gui_type", c4dGuiType)
            c4dGuiType = c4dGuiType.value
            # meter
            if c4dGuiType == 10:
                data.SetFloat(paramId, v*100.0)
            else:
                data.SetFloat(paramId, v)
        if paramType == AI_TYPE_RGB:
            rgb = AiNodeGetRGB(shader.node, param)
            r = float(int(rgb.r * 255.0 + 0.5)) / 255.0
            g = float(int(rgb.g * 255.0 + 0.5)) / 255.0
            b = float(int(rgb.b * 255.0 + 0.5)) / 255.0
            shader_gamma = AiNodeGetFlt(AiUniverseGetOptions(), "shader_gamma")
            if shader_gamma == 1.0:
               data.SetVector(paramId, ColorCorrection(c4d.Vector(r, g, b)))
            else:           
               data.SetVector(paramId, c4d.Vector(r, g, b))
        if paramType == AI_TYPE_RGBA:
            rgba = AiNodeGetRGBA(shader.node, param)
            r = float(int(rgba.r * 255.0 + 0.5)) / 255.0
            g = float(int(rgba.g * 255.0 + 0.5)) / 255.0
            b = float(int(rgba.b * 255.0 + 0.5)) / 255.0            
            shader_gamma = AiNodeGetFlt(AiUniverseGetOptions(), "shader_gamma")
            if shader_gamma == 1.0:
                data.SetVector(paramId, ColorCorrection(c4d.Vector(r, g, b)))
            else:
               data.SetVector(paramId, c4d.Vector(r, g, b))
        if paramType == AI_TYPE_VECTOR:
            v = AiNodeGetVec(shader.node, param)
            data.SetVector(paramId, c4d.Vector(v.x, v.y, v.z))
        if paramType == AI_TYPE_VECTOR2:
            v = AiNodeGetPnt2(shader.node, param)
            data.SetVector(paramId, c4d.Vector(v.x, v.y, 0))
        if paramType == AI_TYPE_STRING:
            v = AiNodeGetStr(shader.node, param)
            c4dGuiType = ctypes.c_int(-1)
            AiMetaDataGetInt(nodeEntry, param, "c4d.gui_type", c4dGuiType)
            c4dGuiType = c4dGuiType.value
            # filename
            if c4dGuiType in (0,1,2,3):
                if USE_RELATIVE_PATHS:
                    v = os.path.basename(v)
                data.SetFilename(paramId, v)
            else:
                data.SetString(paramId, v)
        if paramType == AI_TYPE_MATRIX:
            matrix = AtMatrix()
            AiNodeGetMatrix(shader.node, param, matrix)
            v1 = c4d.Vector(matrix.a00, matrix.a01, matrix.a02) 
            v2 = c4d.Vector(matrix.a10, matrix.a11, matrix.a12)
            v3 = c4d.Vector(matrix.a20, matrix.a21, matrix.a22)
            off = c4d.Vector(matrix.a03, matrix.a13, matrix.a23)
            m = c4d.Matrix(off, v1, v2, v3)
            data.SetMatrix(paramId, m)
        if paramType == AI_TYPE_ENUM:
            data.SetInt32(paramId, AiNodeGetInt(shader.node, param))
    
    ##
    # shaders with custom export logic
    ##

    # ramp_float
    if nodeId == RAMP_FLOAT_ID:
        SetupRampFloat(shaderNode, shader)
    # ramp_rgb
    elif nodeId == RAMP_RGB_ID:
        SetupRampRgb(shaderNode, shader)

    return shaderNode

###
# Connects the given shaders.
###
def AddConnection(material, srcNode, dstNode, dstParamUniqueName):
    dstPortId = hashid(dstParamUniqueName)

    msg = c4d.BaseContainer()
    msg.SetInt32(C4DTOA_MSG_TYPE, C4DTOA_MSG_ADD_CONNECTION)
    msg.SetLink(C4DTOA_MSG_PARAM1, srcNode)
    msg.SetInt32(C4DTOA_MSG_PARAM2, 0)
    msg.SetLink(C4DTOA_MSG_PARAM3, dstNode)
    msg.SetInt32(C4DTOA_MSG_PARAM4, dstPortId)
    material.Message(c4d.MSG_BASECONTAINER, msg)
    return msg.GetBool(C4DTOA_MSG_RESP1)

###
# Connects the given shader to a root port (beauty or displacement).
###
def SetRootShader(material, shader, rootPortId):
    msg = c4d.BaseContainer()
    msg.SetInt32(C4DTOA_MSG_TYPE, C4DTOA_MSG_CONNECT_ROOT_SHADER)
    msg.SetLink(C4DTOA_MSG_PARAM1, shader)
    msg.SetInt32(C4DTOA_MSG_PARAM2, 0)
    msg.SetInt32(C4DTOA_MSG_PARAM3, rootPortId)
    material.Message(c4d.MSG_BASECONTAINER, msg)
    return msg.GetBool(C4DTOA_MSG_RESP1)

###
# Collects shader links of the given Arnold node
# and stores them in the given map.
###
def CollectLinks(node, links):
    if not node.IsValid():
        return
    
    # skip when already processed
    if node in links:
        return
    
    PrintInfo("collecting links of %s (%s)" % (node.GetName(), node.GetNodeEntryName()))
    
    # check parameters
    shaderLinks = []
    
    piter = AiNodeEntryGetParamIterator(node.GetNodeEntry())
    while not AiParamIteratorFinished(piter):
        pentry = AiParamIteratorGetNext(piter)
        param = AiParamGetName(pentry)
        if AiNodeIsLinked(node.node, param):
            link = ArnoldNode(AiNodeGetLink(node.node, param))
            if link.IsValid():
                shaderLinks.append(ShaderLink(param, link))
                PrintInfo("store link: %s -> %s.%s" % (link.GetName(), node.GetName(), param))
            
            # recursive call
            CollectLinks(link, links)
            
    links[node] = shaderLinks
                            
###
# Collects all shader networks assigned to shapes.
###
def ReadShaderNetworks(assPath, rootShaders, displacements, links):
    if not os.path.exists(assPath):
        PrintError("ASS file not found: %s" % assPath, True)
    if not assPath.endswith(".ass"):
        PrintError("Invalid ASS file: %s" % assPath, True)
                
    # read ass file
    AiASSLoad(assPath)

    aiNodeIterator = AiUniverseGetNodeIterator(AI_NODE_SHAPE)
    while not AiNodeIteratorFinished(aiNodeIterator):
        node = AiNodeIteratorGetNext(aiNodeIterator)
        
        #PrintInfo("Process geometry %s" % AiNodeGetName(node))
      
        # surface shader
        shaderArrayPtr = AiNodeGetArray(node, "shader")
        if shaderArrayPtr:
            shaderArray = NullToNone(shaderArrayPtr, POINTER(AtArray)).contents
            for i in range(0, AiArrayGetNumElements(shaderArray)):
                aShader = ArnoldNode(AiArrayGetPtr(shaderArray, i))
                if aShader.node:
                    rootShaders.add(aShader)

                # links
                CollectLinks(aShader, links)
                
        # displacement
        if AiNodeIs(node, "polymesh"):              
            dispArrayPtr = AiNodeGetArray(node, "disp_map")
            if shaderArrayPtr and dispArrayPtr:
                shaderArray = NullToNone(shaderArrayPtr, POINTER(AtArray)).contents
                dispArray = NullToNone(dispArrayPtr, POINTER(AtArray)).contents
                for i in range(0, AiArrayGetNumElements(dispArray)):
                    aShader = ArnoldNode(AiArrayGetPtr(shaderArray, i))
                    aDisp = ArnoldNode(AiArrayGetPtr(dispArray, i))
                    if aShader.IsValid() and aDisp.IsValid():
                        displacements[aShader] = aDisp

                    # links
                    CollectLinks(aDisp, links)

    AiNodeIteratorDestroy(aiNodeIterator)

    PrintInfo("%d shader networks with %d displacements collected" % (len(rootShaders), len(displacements)))

###
# Creates connections in the shader network.
###
def CreateLinks(mat, shader, links, shaderMap, posx, posy, upward=True):
    shaderLinks = links[shader]
    if not shaderLinks:
        return
    
    shaderNodeEntryName = shader.GetNodeEntryName()
    shaderNode = shaderMap.get(shader)

    linkedShaders = []
    
    for sindex, shaderLink in enumerate(shaderLinks):
        linkedShader = shaderLink.link
        if not linkedShader.IsValid(): continue
        linkedShaderType = linkedShader.GetNodeEntryName()
        linkedShaderName = linkedShader.GetName()

        # create linked shader
        linkedShaderNode = shaderMap.get(linkedShader)
        if linkedShaderNode is None:
            linkedposx = posx - POSX_OFFSET
            linkedposy = posy - sindex*POSY_OFFSET if upward else posy + sindex*POSY_OFFSET
            linkedShaderNode = CreateShader(mat, linkedShader, linkedposx, linkedposy)
            if not linkedShaderNode:
                PrintError("Failed to create shader: %s (%s)", linkedShaderName, linkedShaderType)
                continue
            shaderMap[linkedShader] = linkedShaderNode
            
            linkedShaders.append(linkedShader)

        # create connection
        paramUniqueName = "%s.%s" % (shaderNodeEntryName, shaderLink.param)
        AddConnection(mat, linkedShaderNode, shaderNode, paramUniqueName)


    # create links
    for linkedShader in linkedShaders:
        CreateLinks(mat, linkedShader, links, shaderMap, posx - POSX_OFFSET, posy, upward)

###
# Creates Arnold Shader Network materials.
# Creates all beauty and displacement shaders in a network,
# sets all parameters and connects the shaders.
###
def CreateMaterials(rootShaders, displacements, links):
    # {ArnoldNode: GvNode}
    shaderMap = {}

    for i, rootShader in enumerate(rootShaders):
        if not rootShader or not rootShader.IsValid(): continue
        rootShaderType = rootShader.GetNodeEntryName()
        rootShaderName = rootShader.GetName()
        PrintInfo("Create material for %s (%s)" % (rootShaderName, rootShaderType))

        # create material
        mat = c4d.BaseMaterial(ARNOLD_SHADER_NETWORK)
        if mat is None:
            PrintError("Failed to create material")
            continue
        mat.SetName("ASN_%02d" % (i+1));
        doc.InsertMaterial(mat)

        # create root shader
        rootShaderNode = shaderMap.get(rootShader)
        if rootShaderNode is None:
            rootShaderNode = CreateShader(mat, rootShader, BEAUTY_ROOT_POSX, BEAUTY_ROOT_POSY)
            if rootShaderNode is None:
                PrintError("Failed to create shader %s (%s)" % (rootShaderName, rootShaderType))
                continue
            shaderMap[rootShader] = rootShaderNode

        SetRootShader(mat, rootShaderNode, ARNOLD_BEAUTY_PORT_ID)

        # create links
        CreateLinks(mat, rootShader, links, shaderMap, BEAUTY_ROOT_POSX, BEAUTY_ROOT_POSY, True)

        # displacement root
        dispRootShader = displacements.get(rootShader)
        if dispRootShader and dispRootShader.IsValid():
            dispRootShaderType = dispRootShader.GetNodeEntryName()
            dispRootShaderName = dispRootShader.GetName()
            PrintInfo("Add displacement")

            dispRootShaderNode = shaderMap.get(dispRootShader)
            if dispRootShaderNode is None:
                dispRootShaderNode = CreateShader(mat, dispRootShader, DISPLACEMENT_ROOT_POSX, DISPLACEMENT_ROOT_POSY)
                if dispRootShaderNode is None:
                    PrintError("Failed to create displacement shader %s (%s)" % dispRootShaderName, dispRootShaderType)
                    continue
                shaderMap[dispRootShader] = dispRootShaderNode
            
            SetRootShader(mat, dispRootShaderNode, ARNOLD_DISPLACEMENT_PORT_ID)

            # displacement links
            CreateLinks(mat, dispRootShader, links, shaderMap, DISPLACEMENT_ROOT_POSX, DISPLACEMENT_ROOT_POSY, False)

###
# Console logger.
###
def LogToConsole(mask, severity, message, tabs):
    severityStr = ""
    if severity == AI_SEVERITY_WARNING:
        severityStr = " WARNING"
    elif severity == AI_SEVERITY_ERROR:
        severityStr = "   ERROR"
    elif severity == AI_SEVERITY_FATAL:
        severityStr = "   FATAL"
   
    print "Arnold | %s %s" % (severityStr, message)
    
logfn = AtMsgCallBack(LogToConsole)

###
# Main function.
###
def main():
    print "---------------------------------------------"
    
    # open the file browser
    assPath = c4d.storage.LoadDialog()
    if not assPath: 
        return

    if AiUniverseIsActive():
        PrintError("Arnold render is already runnning. Please stop the render first.", True)

    try:
        Begin()
        
        # setup logging
        # FIXME no messages displayed in the console
        AiMsgSetCallback(logfn)
        AiMsgSetConsoleFlags(AI_LOG_WARNINGS | AI_LOG_ERRORS)
        
        shaderFolders = []
        # C4DtoA shaders folder
        shadersPath = os.path.join(PLUGIN_PATH, "shaders")
        shaderFolders.append(shadersPath)
        # Arnold plugin path
        if ARNOLD_PLUGIN_PATH:
            for path in string.split(ARNOLD_PLUGIN_PATH, os.pathsep):
                shaderFolders.append(shadersPath)

        # load plugins
        for path in shaderFolders:
            PrintInfo("Loading plugins from %s" % path)
            AiLoadPlugins(path)
        # load meta data
        path = os.path.join(PLUGIN_PATH, "c4dtoa.mtd")
        PrintInfo("Loading mtd %s" % path)
        AiMetaDataLoadFile(path)
        for path in shaderFolders:
            for f in os.listdir(shadersPath):
                if f.endswith(".mtd"):
                    path = os.path.join(shadersPath, f)
                    PrintInfo("Loading mtd %s" % path)
                    AiMetaDataLoadFile(path)
                
        # read shader networks
        # set(ArnoldNode)
        rootShaders = set()
        # {ArnoldNode, ArnoldNode}
        displacements = {}
        # {ArnoldNode, [ShaderLink]}
        links = {}
        PrintInfo("-------------------- Read ASS file")
        ReadShaderNetworks(assPath, rootShaders, displacements, links)
    
        # build C4D materials
        PrintInfo("-------------------- Build materials")
        CreateMaterials(rootShaders, displacements, links)
    finally:
        End()
      
    # redraw
    c4d.EventAdd(c4d.EVENT_FORCEREDRAW)
   
if __name__=='__main__':
    try:
        main()
    except Exception,e:
        gui.MessageDialog(e)
        import traceback
        traceback.print_exc(e)        

