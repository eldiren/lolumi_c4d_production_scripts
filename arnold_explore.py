import c4d
from c4d import gui
#Welcome to the world of Python

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
        
def main():
    

if __name__=='__main__':
    main()
