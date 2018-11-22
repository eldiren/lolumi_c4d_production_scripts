import c4d
from c4d import gui

#globals
count = 0;

def main():
  global count;

  # get the first object in the document
  first = doc.GetFirstObject();

  # if there is an object, check for the presence of the tag
  # also for any sibling and child objects
  if(first):
    doc.StartUndo();
    CheckObject(doc, first);
    doc.EndUndo();
    c4d.EventAdd();
    
  # tell the user how many tags were deleted
  gui.MessageDialog(str(count) + " texture tags were deleted by the script.");

def CheckTextureTag(doc, op):
  global count;
  
  # check to see if this object has a texture tag and if so, whether it has a material
  opTags = op.GetTags();
  
  if(opTags):
    for tag in opTags:
      if(tag.GetType() == c4d.Ttexture):   # texture tag
        if(not tag.GetMaterial()):
          # set an undo step in case the user changes their mind
          doc.AddUndo(c4d.UNDOTYPE_DELETE, tag);
          tag.Remove();
          count = count + 1;              # update the count of deleted tags
                
    #while (theTag): 
      #if(theTag.GetType() == c4d.Ttexture):   # texture tag
        #print theTag.GetMaterial();  
        # if there is no valid mat, delete the tag
        #if(not theTag.GetMaterial()):  
              
          # set an undo step in case the user changes their mind
          #doc.AddUndo(c4d.UNDOTYPE_DELETE, theTag);
          #theTag.Remove();
          #count = count + 1;              # update the count of deleted tags

def CheckObject(doc, op):
  
  # check the texture tags on this object
  while (op):
    CheckTextureTag(doc, op);
    op = GetNextObject(op);

# get the next object in a heriarchy
def GetNextObject(op):
  if(not op):
    return None;
  
  if(op.GetDown()):
    return op.GetDown();
  
  while( not op.GetNext() and op.GetUp() ):
    op = op.GetUp();
     
  return op.GetNext();

if __name__=='__main__':
    main()
