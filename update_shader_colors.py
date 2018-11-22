import c4d
import os, sys, ctypes
# load Arnold modules
PLUGIN_PATH = os.path.join(c4d.storage.GeGetStartupPath(), "plugins", "C4DtoA")
arnoldPythonPath = os.path.join(PLUGIN_PATH, "arnold", "python")
sys.path.append(arnoldPythonPath)
from arnold import *

C4DTOA_MSG_TYPE = 1000
C4DTOA_MSG_RESP1 = 2011
C4DTOA_MSG_QUERY_SHADER_NETWORK = 1028

ARNOLD_SHADER_GV = 1033990
ARNOLD_C4D_SHADER_GV = 1034190
ARNOLD_SHADER_NETWORK = 1033991
ARNOLD_PREFERENCES = 1036062

PARNOLD_SHADER_COLORS = 3000
C4DAI_GVSHADER_TYPE = 200

def QueryNetwork(material):
    msg = c4d.BaseContainer()
    msg.SetInt32(C4DTOA_MSG_TYPE, C4DTOA_MSG_QUERY_SHADER_NETWORK)
    material.Message(c4d.MSG_BASECONTAINER, msg)
    return msg
    
def hashid(name):
    if name is None: return 0
     
    h = 5381
    for c in name:
        h = (h << 5) + h + ord(c)
    h = ctypes.c_int32(h).value
    if h < 0: h = -h
    return h
    
nodeEntryMap = {}

def InitNodeEntryMap():
    it = AiUniverseGetNodeEntryIterator(AI_NODE_SHADER)
    while not AiNodeEntryIteratorFinished(it):
        nentry = AiNodeEntryIteratorGetNext(it)
        name = AiNodeEntryGetName(nentry)
        
        nodeId = ctypes.c_int(-1)
        AiMetaDataGetInt(nentry, None, "c4d.node_id", nodeId)

        if nodeId.value > -1:
            nodeEntryMap[nodeId.value] = nentry
        else:
            nodeEntryMap[hashid(name)] = nentry
    AiNodeEntryIteratorDestroy(it)

def GetNodeEntry(shader):
    if shader.GetOperatorID() == ARNOLD_SHADER_GV:
        nodeId = shader.GetOpContainerInstance().GetInt32(C4DAI_GVSHADER_TYPE)
    else:
        nodeId = shader.GetOperatorID()

    return nodeEntryMap.get(nodeId)

def GetShaderColor(shader):
    preferences = c4d.GetWorldContainerInstance().GetContainerInstance(ARNOLD_PREFERENCES)
    shaderColors = preferences.GetContainerInstance(PARNOLD_SHADER_COLORS)
    
    if shader.GetOperatorID() == ARNOLD_C4D_SHADER_GV:
        return shaderColors.GetVector(101)
    
    nentry = GetNodeEntry(shader)
    menuPath = AtString("")
    if nentry:
        AiMetaDataGetStr(nentry, None, "c4d.menu", menuPath)
    
    if menuPath.value:
        colorIdStr = "ai/" + menuPath.value
        colorId = hashid(colorIdStr)
        return shaderColors.GetVector(colorId, c4d.Vector(97.0/255.0, 98.0/255.0, 100.0/255.0))

    return c4d.Vector(97.0/255.0, 98.0/255.0, 100.0/255.0)
    
def UpdateShaderColors(material):
    if not material: 
        return

    if material.GetType() != ARNOLD_SHADER_NETWORK:
        return

    print "Update shaders of %s" % material.GetName()
    
    network = QueryNetwork(material)
    
    numNodes = network.GetInt32(C4DTOA_MSG_RESP1)
    for i in range(0, numNodes):
        shader = network.GetLink(10000+i)
        
        # set title color
        color = GetShaderColor(shader)
        #gedata = c4d.GeData(color)
        #descid = c4d.DescID()
        shader.SetParameter(c4d.ID_GVBASE_COLOR, color, c4d.DESCFLAGS_SET_0)
    
def UpdateAllShaderColors():
    mat = doc.GetFirstMaterial()
    while mat is not None:
        UpdateShaderColors(mat)
        mat = mat.GetNext()
    
def main():
    AiBegin()
    
    shaderFolders = []
    # C4DtoA shaders folder
    shadersPath = os.path.join(PLUGIN_PATH, "shaders")
    shaderFolders.append(shadersPath)
    # Arnold plugin path
    ARNOLD_PLUGIN_PATH = os.environ.get("ARNOLD_PLUGIN_PATH")
    if ARNOLD_PLUGIN_PATH:
        for path in ARNOLD_PLUGIN_PATH.split(os.pathsep):
            shaderFolders.append(shadersPath)

    # load plugins
    for path in shaderFolders:
        print "Loading plugins from %s" % path
        AiLoadPlugins(path)
    # meta data
    path = os.path.join(PLUGIN_PATH, "c4dtoa.mtd")
    print "Loading mtd %s" % path
    AiMetaDataLoadFile(path)
    for path in shaderFolders:
        for f in os.listdir(shadersPath):
            if f.endswith(".mtd"):
                path = os.path.join(shadersPath, f)
                print "Loading mtd %s" % path
                AiMetaDataLoadFile(path)

    InitNodeEntryMap()

    print "-------------------"
    
    mat = doc.GetActiveMaterial()
    UpdateShaderColors(mat)
    
    #UpdateAllShaderColors()

    c4d.EventAdd()
        
    AiEnd()    
        
if __name__=='__main__':
    main()
