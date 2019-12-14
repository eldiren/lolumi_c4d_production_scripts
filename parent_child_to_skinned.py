# select a joint root and this script will go through finding any polymesh
# children, renaming, and adding weight tags to make it into a skin based
# character, created for mechcanical style characters that typically are
# rigged via parent/child aninmation

import c4d, loutils
from c4d import gui

def main():
    boneRoot = doc.GetActiveObject()
    obj = boneRoot

    while obj:
        if obj.GetType() == 5100: # polymesh
            parent = obj.GetUp()
            while parent.GetType() != 1019362: #joint
                parent = parent.GetUp()

            # rename the object and add a weight tag using the found joint
            obj.SetName(parent.GetName() + '_mesh')
            wtag = obj.MakeTag(1019365) # weight tag
            idx = wtag.AddJoint(parent)
            
            # set weight of joint to 100%
            pntCnt = obj.GetPointCount()
            for num in range(0, pntCnt):
                wtag.SetWeight(idx, num, 1)

        obj = loutils.GetNextObject(obj, boneRoot)

    # insert the poly objects at the root of the document
    obj = boneRoot
    while obj:
        if obj.GetType() == 5100: #polymesh
            gMatrix = obj.GetMg()
            obj.Remove()
            doc.InsertObject(obj)
            obj.SetMg(gMatrix)
            skin = c4d.BaseObject(1019363)
            skin.InsertUnder(obj)
            # removing an object breaks the list causing an infinite loop, so we set it back
            # to the start here to begin fresh
            obj = boneRoot

        obj = loutils.GetNextObject(obj, boneRoot)

    c4d.EventAdd()

# Execute main()
if __name__=='__main__':
    main()