import c4d
from c4d import gui
import os

def main():
    #os.environ["PXR_PLUGINPATH_NAME"] = "C:/Program Files/MAXON/CINEMA 4D R18/plugins/Lumiere Pipeline Tools/share/usd/plugins"
    print os.environ['PXR_PLUGINPATH_NAME']    

if __name__=='__main__':
    main()
