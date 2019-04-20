# adds name to objects based on texture tags, in materialx/katana
# style workflows where collections and wildcard assignments are a
# thing this is incredibly useful, as it gives you a name to latch
# on to that's common

import c4d, loutils
from c4d import gui

def main():
    objRoot = doc.GetActiveObject()
    obj = objRoot

    while obj:
        if obj.GetType() == 5100: # polymesh
            tag = obj.GetTag(5616)
            if tag:
                origName = obj.GetName() 
                matName = tag.GetMaterial().GetName()
               
                obj.SetName(origName + '_' + matName)

        obj = loutils.GetNextObject(obj, objRoot)

    c4d.EventAdd()

if __name__=='__main__':
    main()