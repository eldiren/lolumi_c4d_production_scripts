# takes Arnold Image nodes and sets thier color space to linear
# Houdini and Maya colorspaces look more correct and require less
# effort if the tx file are linear, this allow C4D to same the same 
# look

import c4d

C4DTOA_MSG_TYPE = 1000
C4DTOA_MSG_ADD_CONNECTION = 1031

C4DTOA_MSG_PARAM1 = 2001
C4DTOA_MSG_PARAM2 = 2002
C4DTOA_MSG_PARAM3 = 2003
C4DTOA_MSG_PARAM4 = 2004

C4DTOA_MSG_RESP1 = 2011
C4DTOA_MSG_RESP2 = 2012
C4DTOA_MSG_RESP3 = 2013
C4DTOA_MSG_RESP4 = 2014
C4DTOA_MSG_QUERY_SHADER_NETWORK = 1028
C4DTOA_MSG_ADD_SHADER = 1029

# from c4dtoa_symbols.h
ARNOLD_SHADER_NETWORK = 1033991
ARNOLD_SHADER_GV = 1033990
ARNOLD_C4D_SHADER_GV = 1034190

# from api/util/NodeIds.h
C4DAIN_IMAGE = 262700200

# from res/description/gvarnoldshader.h
C4DAI_GVSHADER_TYPE = 200

# from res/description/gvc4dshader.h
C4DAI_GVC4DSHADER_TYPE = 200

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

def QueryNetwork(material):
    msg = c4d.BaseContainer()
    msg.SetInt32(C4DTOA_MSG_TYPE, C4DTOA_MSG_QUERY_SHADER_NETWORK)
    material.Message(c4d.MSG_BASECONTAINER, msg)
    return msg
    
def CheckShader(mat, shader):
    if shader is None: return None
    
    data = shader.GetOpContainerInstance()
        
    if shader.GetOperatorID() == ARNOLD_SHADER_GV:
        nodeId = data.GetInt32(C4DAI_GVSHADER_TYPE)
        if nodeId == C4DAIN_IMAGE:
            print "Node ID: " + str(nodeId)
            data.SetString(868305056, 'linear')

    return None
        
def main():
    
    mat = doc.GetFirstMaterial()
    while mat:
        if mat.GetType() == ARNOLD_SHADER_NETWORK:
            # query network
            network = QueryNetwork(mat)
            # iterate over shaders
            numShaders = network.GetInt32(C4DTOA_MSG_RESP1)
            for i in range(0, numShaders):
                shader = network.GetLink(10000+i)
                CheckShader(mat, shader)
        
        mat = mat.GetNext()
        
if __name__=='__main__':
    main()
