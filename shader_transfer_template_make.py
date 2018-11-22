import c4d
from c4d import gui

APARAMETERS_TAG = 1029989

def main():
    # get all selected objects
    objs = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_CHILDREN);
    
    # traverse the list in reverse so the deletes don't throw things off
    for obj in reversed(objs):
        nullObj = c4d.BaseObject(c4d.Onull);
        nullObj.SetName(obj.GetName());
        doc.InsertObject(nullObj);
        objTags = obj.GetTags();
        # need to go through the tags in reverse order for them to be in
        # correct order in the object manager
        for tag in reversed(objTags):
            if tag.GetType() == APARAMETERS_TAG or tag.GetType() == c4d.Ttexture or tag.GetType() == c4d.Tpolygon:
                nullObj.InsertTag(tag);
            
        obj.Remove();
    
    c4d.EventAdd();
    
if __name__=='__main__':
    main()
