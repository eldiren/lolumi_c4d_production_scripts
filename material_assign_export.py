import c4d
from c4d import gui
#Welcome to the world of Python

class AssignMaterial(object):
    def __init__(self, matname):
        self.matname = matname
        self.objects = []
        self.groups = []
        
def main():
    fileName = c4d.storage.LoadDialog(c4d.FILESELECTTYPE_ANYTHING, "Select export file...", c4d.FILESELECT_SAVE)
    f = open(fileName, 'w')
    
    mat = doc.GetFirstMaterial()
    
    matcnt = doc.GetMaterials()
    
    #print len(matcnt)
    f.write(str(len(matcnt)))
    f.write("\n")
    
    amats = []
    while mat:
        mad = mat[c4d.ID_MATERIALASSIGNMENTS]
        amats.append(AssignMaterial(mat.GetName()))
        if mad == None:
            return
        
        #print mat.GetName()+ "," + str(mad.GetObjectCount())
        
        for i in range(mad.GetObjectCount()):
            atom = mad.ObjectFromIndex(doc, i)
            if atom == None: continue
            
            # we need to check if the texture tag has a selection,
            # if so we need to specify its a group, other programs
            # have different ways of handling these so we want to
            # notify them
            if atom.IsInstanceOf(c4d.Ttexture):
                if atom[c4d.TEXTURETAG_RESTRICTION] != "":
                    amats[-1].groups.append(atom[c4d.TEXTURETAG_RESTRICTION])
                else:
                    amats[-1].objects.append(atom.GetObject().GetName())
            
        mat = mat.GetNext()
        
    # loop through the assigned materials and write them out
    for amat in amats:
        f.write(amat.matname + "," + str(len(amat.objects)) + "," + str(len(amat.groups)))
        f.write("\n")
        for obj in amat.objects:
            f.write(obj)
            f.write("\n")
        
        for grp in amat.groups:
            f.write(grp)
            f.write("\n")
                
if __name__=='__main__':
    main()
