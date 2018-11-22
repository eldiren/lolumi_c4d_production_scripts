import c4d
from c4d import gui

ID_LUMIERECACHEEXPORTER = 1039713

def main():
    #SetCachePath("/Cube")
    GetCachePath()
    
def GetCachePath():
    bc = op.GetData();
    print("USD Path: " + bc.GetData(ID_LUMIERECACHEEXPORTER));
    
def SetCachePath(pathStr):
    bc = op.GetData();
    bc.SetData(ID_LUMIERECACHEEXPORTER, pathStr);
    print(" - wrote USD Path: " + bc.GetData(ID_LUMIERECACHEEXPORTER))
    op.SetData(bc);

if __name__=='__main__':
    main()
