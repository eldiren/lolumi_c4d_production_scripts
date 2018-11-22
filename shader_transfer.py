import c4d
from c4d import gui

def main():
    fname = c4d.storage.LoadDialog();
    if not fname: 
        return; 
    
    temp = c4d.documents.LoadDocument(fname, c4d.SCENEFILTER_OBJECTS|c4d.SCENEFILTER_MATERIALS)
    
    # get all the materials and insert them into the current doc
    mats = temp.GetMaterials()
    for mat in mats:
        # the material must be removed from the previous doc first
        mat.Remove();
        doc.InsertMaterial(mat);
        
    # now we'll go through all the objects in the shading template
    # find any matches in our document and transfer the tags over
    objs = temp.GetObjects()
    for obj in objs:
        currObj = doc.SearchObject(obj.GetName())
        if currObj:
            objTags = obj.GetTags();
            for tag in reversed(objTags):
                tag.Remove();
                currObj.InsertTag(tag);    
    
    c4d.documents.KillDocument(temp);    
    c4d.EventAdd();
    
if __name__=='__main__':
    main()
