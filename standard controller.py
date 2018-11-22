import c4d
from c4d import gui, documents, plugins
#This script will take a null and make it look like
#a nice controller, namely a sphere

def main():
    def object():
        return doc.GetActiveObject()
    
    def tag():
        return doc.GetActiveTag()
    
    def renderdata():
        return doc.GetActiveRenderData()
    
    object()[c4d.NULLOBJECT_DISPLAY]=13 #change null to sphere
    object()[c4d.NULLOBJECT_ORIENTATION]=1 #change camera angle
    object()[c4d.NULLOBJECT_RADIUS]=0.5 #make the sphere a good size
    object()[c4d.ID_BASEOBJECT_USECOLOR]=2 #turn on the color in viewport
    c4d.EventAdd() #refresh the scene
    
if __name__=='__main__':
    main()
