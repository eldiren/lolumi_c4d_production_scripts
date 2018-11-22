import c4d
from c4d import gui
#Welcome to the world of Python


def main():
    pnull = c4d.BaseObject(c4d.Onull)
    pnull.SetName("scene_nulls")
    doc.InsertObject(pnull)
    
    for i in range(op.GetPointCount()):
        null = c4d.BaseObject(c4d.Onull)
        null[c4d.NULLOBJECT_DISPLAY] = 2
        null[c4d.ID_BASEOBJECT_USECOLOR] = 2
        col = c4d.Vector(1, 0, 0)
        null[c4d.ID_BASEOBJECT_COLOR] = col
        pnt = op.GetPoint(i)
        pos = c4d.Vector(pnt.x, pnt.y, pnt.z)
        null.SetAbsPos(pos)
        doc.InsertObject(null, pnull)
        
    c4d.EventAdd()

if __name__=='__main__':
    main()
