# swap C4D Arnold Bitmap shaders for Arnold Image nodes

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
    
def GetTexturePath(mat, shader):
    if shader is None: return None
    
    data = shader.GetOpContainerInstance()
        
    if shader.GetOperatorID() == ARNOLD_C4D_SHADER_GV:
        nodeId = data.GetInt32(C4DAI_GVC4DSHADER_TYPE)
        print "Node ID: " + str(nodeId)
        if nodeId == c4d.Xbitmap:
            # the C4D shader is attached to the GV node
            c4d_shader = shader.GetFirstShader()
            if c4d_shader is not None:
               outports = shader.GetOutPorts(0)
               if outports[0]:    
                  if outports[0].GetNrOfConnections() > 0:
                     inport = outports[0].GetDestination()
                     connectedNode = inport[0].GetNode()
                     print "Connected shader: " + connectedNode.GetName()
               
                     image = CreateArnoldShader(mat, C4DAIN_IMAGE, 0, 50)
                     if image is None:
                        raise Exception("Failed to create image shader")
                     
                     imagepath = c4d_shader.GetDataInstance().GetFilename(c4d.BITMAPSHADER_FILENAME)
                     image.GetOpContainerInstance().SetFilename(C4DAIP_IMAGE_FILENAME, imagepath)
                     image.GetOpContainerInstance().SetString(868305056, 'linear')
                     AddConnection(mat, image, connectedNode, inport[0].GetMainID())
                     shader.Remove()

    return None
    
class TextureInfo:
    
    def __init__(self, mat, shader, texturePath):
        self.material = mat
        self.shader = shader
        self.path = texturePath
        
def main():
    textures = []
    
    # collect textures
    mat = doc.GetFirstMaterial()
    while mat:
        if mat.GetType() == ARNOLD_SHADER_NETWORK:
            # query network
            network = QueryNetwork(mat)
            # iterate over shaders
            numShaders = network.GetInt32(C4DTOA_MSG_RESP1)
            for i in range(0, numShaders):
                shader = network.GetLink(10000+i)
                texturePath = GetTexturePath(mat, shader)
                if texturePath:
                    texture = TextureInfo(mat, shader, texturePath)
                    textures.append(texture)
        
        mat = mat.GetNext()

    # print textures
    print "-----------------------"
    print "%d texture(s) found" % len(textures)
    i = 1
    for texture in textures:
        print " %d. %s.%s: %s" % (i, texture.material.GetName(), texture.shader.GetName(), texture.path)
        i += 1
        
if __name__=='__main__':
    main()
