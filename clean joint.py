import c4d
from c4d import gui, documents, plugins
#This script resizes a joint automatically

def main():
    def object():
        return doc.GetActiveObject()
    
    def tag():
        return doc.GetActiveTag()
    
    def renderdata():
        return doc.GetActiveRenderData()
    
    object()[c4d.ID_CA_JOINT_OBJECT_JOINT_SIZE_MODE]=0
    object()[c4d.ID_CA_JOINT_OBJECT_JOINT_SIZE]=0.15
    
    c4d.EventAdd()
    
if __name__=='__main__':
    main()
