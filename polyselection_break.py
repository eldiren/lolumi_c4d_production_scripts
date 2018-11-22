import c4d
from c4d import gui, utils

# takes an object with poly selection and breaks it up so the 
# selection are children of the parent, also keeps child material
# assignments. created to address the current limitation of Arnold



def main():
    if not op: return
    
    obj = op # the modeling commands change the op so we need to store this
    gMatrix = op.GetMg()
    tag = obj.GetFirstTag()
    
    newChildren = []
    
    while tag:
        if tag.GetType() == c4d.Tpolygonselection:
            # deselect all polygons
            polyselection = obj.GetPolygonS()
            polyselection.DeselectAll()
            
            # select polygons from selection tag
            tagselection = tag.GetBaseSelect()
            tagselection.CopyTo(polyselection)
            
            #split: polygonselection to a new object
            sec = utils.SendModelingCommand(command=c4d.MCOMMAND_SPLIT, list=[obj], mode=c4d.MODELINGCOMMANDMODE_POLYGONSELECTION, doc=doc)
             
            if not sec:
                print 'split failed for ' + tag.GetName() 
                continue    
                               
            sec[0].SetName(tag.GetName())
            sec[0][c4d.ID_BASEOBJECT_REL_POSITION] = c4d.Vector(0,0,0)
            sec[0][c4d.ID_BASEOBJECT_REL_ROTATION] = c4d.Vector(0,0,0)
            
            # remove polyselections and textures from the split and find a material to keep
            secTag = sec[0].GetTag(c4d.Tpolygonselection)
            
            while secTag:
                secTag.Remove()
                secTag = sec[0].GetTag(c4d.Tpolygonselection)
                
            secTag = sec[0].GetFirstTag()
            
            while secTag:
                oldSecTag = None
                if secTag.GetType() == c4d.Ttexture:
                    if secTag[c4d.TEXTURETAG_RESTRICTION] == tag.GetName():
                        secTag[c4d.TEXTURETAG_RESTRICTION] = ''
                    else:
                        oldSecTag = secTag               
                    
                secTag = secTag.GetNext()
                if oldSecTag:
                    oldSecTag.Remove()
            
            # loop through tags and find any texture tags that have the selection and delete
            oldMatTag = None
            matTag = obj.GetFirstTag()
            while matTag:
                if matTag.GetType() == c4d.Ttexture:
                    if matTag[c4d.TEXTURETAG_RESTRICTION] == tag.GetName():
                        oldMatTag = matTag
                        
                matTag = matTag.GetNext()
                
                if oldMatTag: 
                    oldMatTag.Remove()     
                         
            newChildren.append(sec[0])
            #delete the polygons from selectiontag
            utils.SendModelingCommand(command=c4d.MCOMMAND_DELETE, list=[obj], mode=c4d.MODELINGCOMMANDMODE_POLYGONSELECTION, doc=doc)
            
            
        tag = tag.GetNext()
        
    # remove selection tags
    tag = obj.GetTag(c4d.Tpolygonselection)
            
    while tag:
        tag.Remove()
        tag = obj.GetTag(c4d.Tpolygonselection)  
    
    # Optimize in order to remove loose points
    options = c4d.BaseContainer()
    options[c4d.MDATA_OPTIMIZE_TOLERANCE] = 0.001
    options[c4d.MDATA_OPTIMIZE_POINTS] = True
    options[c4d.MDATA_OPTIMIZE_POLYGONS] = False
    options[c4d.MDATA_OPTIMIZE_UNUSEDPOINTS] = True
    utils.SendModelingCommand(c4d.MCOMMAND_OPTIMIZE, list = [obj], mode = c4d.MODELINGCOMMANDMODE_ALL, bc = options, doc = obj.GetDocument())
                                         
    if obj.GetPolygonCount() == 0: # no more polys, remove this and replace with null
        objNull = c4d.BaseObject(c4d.Onull)
        objNull.SetName(obj.GetName())
        objParent = obj.GetUp()
        obj.Remove()
        
        obj = objNull
        doc.InsertObject(obj, objParent)
        obj.SetMg(gMatrix)
        
    for child in newChildren:
        child.InsertUnder(obj)
        
    c4d.EventAdd()
    
if __name__=='__main__':
    main()
