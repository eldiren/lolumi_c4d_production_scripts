import c4d
from c4d import utils

def main():
    
    #validate object and selectiontag
    if not op:return
    if not op.IsInstanceOf(c4d.Opolygon):return
    tags = op.GetTags()

    #deselect current polygonselection and store a backup to reselect
    polyselection = op.GetPolygonS()
    store = c4d.BaseSelect()
    polyselection.CopyTo(store)
    
    #define the name to search for
    name = "Polygon Selection"
        
        
    #loop through the tags and check if name and type fits
    #if so split 
    t = op.GetFirstTag()
    while t:
        if t.GetType() == c4d.Tpolygonselection:
            if name in t.GetName():

                #select polygons from selectiontag
                tagselection  =  t.GetBaseSelect()
                tagselection.CopyTo(polyselection)

                #split: polygonselection to a new object
                sec = utils.SendModelingCommand(command=c4d.MCOMMAND_SPLIT,
                                  list=[op],
                                  mode=c4d.MODELINGCOMMANDMODE_POLYGONSELECTION,
                                  doc=doc)
             
                if not sec: return
                print sec
                sec[0].InsertAfter(op)
            
            
        t = t.GetNext()
            
    
    store.CopyTo(polyselection)
    c4d.EventAdd()
        
if __name__=='__main__':
    main()