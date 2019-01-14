import c4d, os, sys
from c4d import gui
import MaterialX as mx

# Initial Arnold support tests, will try to open an Arnold session
# and translate the materials live, will also loop through objects
# setting up property sets(Arnold Overrides), finally spits out a
# mtlx based on user selection

# global setup
PLUGIN_PATH = os.path.join(c4d.storage.GeGetStartupPath(), "plugins", "C4DtoA")
ARNOLD_PLUGIN_PATH = os.environ.get("ARNOLD_PLUGIN_PATH")
USE_RELATIVE_PATHS = True

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

ARNOLD_RENDER_COMMAND = 1038578

envPaths = []

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
    
    def GetNodeEntryOutputType(self):
        etype = ''
        aitype = AiNodeEntryGetOutputType(AiNodeGetNodeEntry(self.node))
        
        if aitype == AI_TYPE_RGB:
            etype = 'color3'
        if aitype == AI_TYPE_BYTE:
            etype = 'byte'
        if aitype == AI_TYPE_INT:
            etype = 'integer'
        #if paramType == AI_TYPE_UINT:
            #etype = 'uinteger'
        if aitype == AI_TYPE_BOOLEAN:
            etype = 'boolean'
        if aitype == AI_TYPE_FLOAT:
            etype = 'float'
        if aitype == AI_TYPE_VECTOR:
            etype = 'vector'
        if aitype == AI_TYPE_RGBA:
            etype = 'color4'
        if aitype == AI_TYPE_VECTOR2:
            etype = 'vector2'
        if aitype == AI_TYPE_STRING:
            etype = 'string'
        if aitype == AI_TYPE_ENUM:
            etype = 'integer'
            
        return etype
        
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

def getEnvList():
    global envPaths
    
    f = open('H:/Documents/asset_library/environment_vars/path_clean_list.txt', 'r')
    
    # Each line is an environment variable and a potenial path it points to
    line = f.readline()
    line = line.rstrip('\n')
    
    while line:
        envPaths.append(line.split(','))    
    
        line = f.readline()
        line = line.rstrip('\n')
        
    f.close()
    
def getParam(snode, pentry):
    global envPaths
    
    ptype = ''
    val = None
    
    param = AiParamGetName(pentry)
    paramType = AiParamGetType(pentry)
        
    if paramType == AI_TYPE_BYTE:
        ptype = 'byte'
        val = AiNodeGetByte(snode, param)
    if paramType == AI_TYPE_INT:
        ptype = 'integer'
        val = AiNodeGetInt(snode, param)
    #if paramType == AI_TYPE_UINT:
        #bInput = sRef.addBindInput(param, 'integer')
        #bInput.setValue(AiNodeGetUInt(shader.node, param))
    if paramType == AI_TYPE_BOOLEAN:
        ptype = 'boolean'
        val = AiNodeGetBool(snode, param)
    if paramType == AI_TYPE_FLOAT:
        ptype = 'float'
        val = AiNodeGetFlt(snode, param)
    if paramType == AI_TYPE_RGB:
        ptype = 'color3'
        rgb = AiNodeGetRGB(snode, param)
        val = mx.Color3(rgb.r, rgb.g, rgb.b)
    if paramType == AI_TYPE_VECTOR:
        ptype = 'vector'
        v = AiNodeGetVec(snode, param)
        val = mx.Vector3(v.x, v.y, v.z)
    if paramType == AI_TYPE_RGBA:
        ptype = 'color4'
        rgba = AiNodeGetRGBA(snode, param)
        val = mx.Color4(rgba.r, rgba.g, rgba.b, rgba.a)
    if paramType == AI_TYPE_VECTOR2:
        ptype = 'vector2'
        v = AiNodeGetVec2(snode, param)
        val = mx.Vector2(v.x, v.y)
    if paramType == AI_TYPE_STRING:
        ptype = 'string'
        val = AiNodeGetStr(snode, param)
        val = val.replace('\\', '/')
        # Arnold 5 supports env vars in the form [envname] we'll do a replace here if a matching path is found
        for path in envPaths:
            if path[1] in val:
                aivar = '[' + path[0] + ']'
                val = val.replace(path[1], aivar)
    if paramType == AI_TYPE_ENUM:
        ptype = 'integer'
        val = AiNodeGetInt(snode, param)
    """
    if paramType == AI_TYPE_MATRIX:
        matrix = AtMatrix()
        AiNodeGetMatrix(shader.node, param, matrix)
        v1 = c4d.Vector(matrix.a00, matrix.a01, matrix.a02) 
        v2 = c4d.Vector(matrix.a10, matrix.a11, matrix.a12)
        v3 = c4d.Vector(matrix.a20, matrix.a21, matrix.a22)
        off = c4d.Vector(matrix.a03, matrix.a13, matrix.a23)
        m = c4d.Matrix(off, v1, v2, v3)
        data.SetMatrix(paramId, m)

    """
    
    return ptype, val

def setNodeParams(nodegraph, shader, processed_shaders, root):
    oname = ''
    nodeEntry = shader.GetNodeEntry()
    nodeEntryName = shader.GetNodeEntryName()
    
    node = nodegraph.addNode(nodeEntryName, shader.GetName(), shader.GetNodeEntryOutputType())
    
    if root: # true if this is the output to a shader ref
        output = nodegraph.addOutput(shader.GetName() + '|output')
        output.setConnectedNode(node)
        oname = output.getName()
    
    # set parameters
    piter = AiNodeEntryGetParamIterator(nodeEntry)
    while not AiParamIteratorFinished(piter):
        pentry = AiParamIteratorGetNext(piter)
        param = AiParamGetName(pentry)
        paramType = AiParamGetType(pentry)
        if param != 'name': # let's just skip the name param, that's set already
            bitype, val = getParam(shader.node, pentry)
            
            if AiNodeIsLinked(shader.node, param) or val:
                nInput = node.addInput(param, bitype)
                if AiNodeIsLinked(shader.node, param): # this param is linked to a shader, let's make a recursive call to create it and its params
                    link = ArnoldNode(AiNodeGetLink(shader.node, param))
                    if link.IsValid():
                        #print 'shader link found: ' + link.GetName() + ',' + param
                        nInput.setNodeName(link.GetName())
                        
                        if link.GetName() not in processed_shaders:
                            processed_shaders.append(link.GetName())
                            setNodeParams(nodegraph, link, processed_shaders, False)
                elif val: # normal parameter, just set value
                    nInput.setValue(val)
                #else: # value not set becausde I haven't implemented it yet or some other reason
        
    return oname
    
def setShaderRef(mdoc, mat, shader, processed_shaders):
    if shader is None or mdoc is None: 
        return
    
    nodeEntry = shader.GetNodeEntry()
    nodeEntryName = shader.GetNodeEntryName()
    
    sRef = mat.addShaderRef("simple_srf", nodeEntryName)
    
    # if the shader ref is like the shading group or master beauty/disp port, the nodegraph 
    # is baiscally all other elements connected to that
    nGraph = mdoc.addNodeGraph(shader.GetName() + '|graph')
            
    # set parameters
    piter = AiNodeEntryGetParamIterator(nodeEntry)
    while not AiParamIteratorFinished(piter):
        pentry = AiParamIteratorGetNext(piter)
        param = AiParamGetName(pentry)
        paramType = AiParamGetType(pentry)
        
        if param != 'name': # let's just skip the name param, that's set already
            bitype, val = getParam(shader.node, pentry)       
            if AiNodeIsLinked(shader.node, param) or val:
                bInput = sRef.addBindInput(param, bitype)
                            
                if AiNodeIsLinked(shader.node, param): # this param is linked to a shader, let's make a recursive call to create it and it params
                    link = ArnoldNode(AiNodeGetLink(shader.node, param))
                    if link.IsValid():
                        #print 'shader link found: ' + link.GetName() + ',' + param
                        if link.GetName() not in processed_shaders:
                            processed_shaders.append(link.GetName())
                            oname = setNodeParams(nGraph, link, processed_shaders, True)
        
                            bInput.setNodeGraphString(nGraph.getName())
                            bInput.setOutputString(oname)
                elif val: # normal parameter, just set value
                    bInput.setValue(val)
                #else: # if val doesn't exist then I haven't implemented support for this param type yet
                        
                
def writeMatX(filepath):
    materials = []
    # Create a document.
    matxDoc = mx.createDocument()
    mx.prependXInclude(matxDoc, 'H:/Documents/asset_library/mtlx_defs/arn_nodedefs.mtlx')
    
    matXLook = matxDoc.addLook("base")
    
    aiNodeIterator = AiUniverseGetNodeIterator(AI_NODE_SHAPE)
    
    while not AiNodeIteratorFinished(aiNodeIterator):
        node = AiNodeIteratorGetNext(aiNodeIterator)
        
        PrintInfo("Process geometry %s" % AiNodeGetName(node))
        
        if AiNodeGetName(node) != '':
            # surface shader
            shaderArrayPtr = AiNodeGetArray(node, "shader")
            if shaderArrayPtr:
                shaderArray = NullToNone(shaderArrayPtr, POINTER(AtArray)).contents
                for i in range(0, AiArrayGetNumElements(shaderArray)):
                    aShader = ArnoldNode(AiArrayGetPtr(shaderArray, i))
                    if aShader.node:
                        print 'Adding assignment: ' + AiNodeGetName(node) + '|ma' + str(i) + ' With shader name: ' + aShader.GetName()
                        matXAssign = matXLook.addMaterialAssign(AiNodeGetName(node) + '|ma' + str(i), aShader.GetName())
                        matXAssign.setGeom(AiNodeGetName(node) + '/*')
                        
                        if aShader.GetName() not in materials:
                            # gather parameters and write out material
                            matXMaterial = matxDoc.addMaterial(aShader.GetName())
                            
                            setShaderRef(matxDoc, matXMaterial, aShader, materials)
                            # add to materials list so we don't create it again
                            materials.append(aShader.GetName())
                                
            # displacement
            if AiNodeIs(node, "polymesh"):              
                dispArrayPtr = AiNodeGetArray(node, "disp_map")
                if shaderArrayPtr and dispArrayPtr:
                    shaderArray = NullToNone(shaderArrayPtr, POINTER(AtArray)).contents
                    dispArray = NullToNone(dispArrayPtr, POINTER(AtArray)).contents

    AiNodeIteratorDestroy(aiNodeIterator)

    mx.writeToXmlFile(matxDoc, filepath)
    """
    matXMaterial = matxDoc.addMaterial(matname)

    matXMaterial.addShaderRef("c4d" + "|" + matname + "|" + destShaderName, "beauty");

    matXMaterial.addShaderRef("c4d" + "|" + matname + "|image", "displacement");
    
    nodeGraph = matxDoc.addNodeGraph()
    matXShader = nodeGraph.addNode("shader", "c4d" + "|" + matname + "|" + destShaderName, "standard_surface")
    
    matXShaderSrc = nodeGraph.addNode("shader", "c4d" + "|" + matname + "|" + srcShaderName, "ramp_rgb")
    
    coshader = matXShader.setConnectedNode(paramname, matXShaderSrc)
    
    """
        
    """
    # Create a node graph with a constant color output.
    nodeGraph = doc.addNodeGraph()
    shader = nodeGraph.addNode('shader')
    shader.setParameterValue('i_subsurfaceColor', mx.Color3(0.0, 0.0, 0.0))
    output = nodeGraph.addOutput()
    output.setConnectedNode(shader)
    
    # Create a simple shader interface.
    shader = doc.addNodeDef('shader1', 'surfaceshader', 'simpleSrf')
    diffColor = shader.addInput('diffColor', 'color3')
    specColor = shader.addInput('specColor', 'color3')
    roughness = shader.addParameter('roughness', 'float')
    
    # Create a material that instantiates the shader.
    material = doc.addMaterial()
    shaderRef = material.addShaderRef('shaderRef1', 'simpleSrf')
    
    # Bind the diffuse color input to the constant color output.
    bindInput = shaderRef.addBindInput('diffColor')
    bindInput.setConnectedOutput(output)
    """
    
    """        
    # Traverse the document tree in depth-first order.
    for elem in doc.traverseTree():
        #print elem.getName()
        if elem.isA(mx.Material, ''):
            print 'Material node', elem.getName()
        elif elem.isA(mx.Element, 'shader'):
            print '--Shader node', elem.getName()
            children = elem.getChildren()
            for child in children:
                if child.isA(mx.Element, 'coshader'):
                    print "----Param Link", child.getName()
                else:
                    print "----Param", child.getName()
        #elif elem.isA(mx.Node, 'image'):
            #print 'Image node', elem.getName()
    """

def main():
    getEnvList()
    
    filePath = c4d.storage.SaveDialog(c4d.FILESELECTTYPE_ANYTHING, "Export path...", "mtlx")
    
    # fire off the IPR to gather arnold nodes
    c4d.CallCommand(ARNOLD_RENDER_COMMAND, 1)
    
    if filePath != "":
        writeMatX(filePath)
    
    c4d.CallCommand(ARNOLD_RENDER_COMMAND, 0)
    
if __name__=='__main__':
    main()
