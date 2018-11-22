import c4d
from c4d import gui
#Welcome to the world of Python


def main():
    objList = op.GetChildren();
    objDel = objList[::2];
    
    doc.StartUndo();
    
    for obj in objDel:
        obj.Remove();
    
    doc.EndUndo();    
    c4d.EventAdd();

if __name__=='__main__':
    main()
