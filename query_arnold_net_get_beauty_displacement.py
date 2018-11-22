import c4d
from c4d import gui
#Welcome to the world of Python

C4DTOA_MSG_TYPE = 1000
C4DTOA_MSG_QUERY_SHADER_NETWORK = 1028
C4DTOA_MSG_RESP3 = 2013
C4DTOA_MSG_RESP4 = 2014

def QueryNetwork(material):
    msg = c4d.BaseContainer()
    msg.SetInt32(C4DTOA_MSG_TYPE, C4DTOA_MSG_QUERY_SHADER_NETWORK)
    material.Message(c4d.MSG_BASECONTAINER, msg)
    return msg

def main():
    # query network
    network = QueryNetwork(newmat)
    # get beauty and displacement and add prefixs so we can identify them in
    # other programs
    beautyShader = network.GetLink(C4DTOA_MSG_RESP3)
    dispShader = network.GetLink(C4DTOA_MSG_RESP4)

if __name__=='__main__':
    main()
