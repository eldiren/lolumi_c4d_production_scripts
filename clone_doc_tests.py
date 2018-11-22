import c4d
from c4d import gui
#Welcome to the world of Python


def main():
    #manual current state code
    newdoc = doc.GetClone()
    newdoc.ExecutePasses(None, True, True, True, c4d.BUILDFLAGS_EXTERNALRENDERER | c4d.BUILDFLAGS_0) 

    c4d.documents.InsertBaseDocument(newdoc)
    c4d.documents.SetActiveDocument(newdoc)
    objs = newdoc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_0)
    
    for obj in objs:
        if obj.GetInfo() & c4d.OBJECT_GENERATOR): #obj.GetBit(c4d.BIT_CONTROLOBJECT):
            print "Generator or controled by one: ", obj
            #c4d.utils.SendModelingCommand(c4d.MCOMMAND_CURRENTSTATETOOBJECT, [obj], c4d.MODELINGCOMMANDMODE_ALL, c4d.BaseContainer(), newdoc)[0]
            if obj.GetDown():
                child = obj.GetDown()
                while child:
                    if obj.GetInfo() & c4d.OBJECT_GENERATOR:
                        print "Is a generator", child
                    
                    if obj.GetInfo() & c4d.OBJECT_INPUT:
                        print "Controled by a generator!"
                    
                    child = child.GetNext()
                    
    
    #build render passes code
    #newdoc = doc.GetClone()
    #newdoc.ExecutePasses(None, True, True, True, c4d.BUILDFLAGS_EXTERNALRENDERER) 
    #polydoc = newdoc.Polygonize(keepanimation=True)
    #c4d.documents.KillDocument(newdoc)
    #c4d.documents.InsertBaseDocument(polydoc)
    #c4d.documents.SetActiveDocument(polydoc)
        
    #Polygonize code
    #newdoc = doc.Polygonize(keepanimation=True)
    #c4d.documents.InsertBaseDocument(newdoc)
    #c4d.documents.SetActiveDocument(newdoc)
    #c4d.EventAdd()

if __name__=='__main__':
    main()
