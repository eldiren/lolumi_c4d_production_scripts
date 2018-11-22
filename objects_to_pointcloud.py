import c4d
from c4d import gui
#Welcome to the world of Python


def main():
    objs = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_0)
    mypoly = c4d.BaseObject(c4d.Opolygon) #Create an empty polygon object
    mypoly.SetName("points")
    mypoly.ResizeObject(len(objs), 0) #New number of points, New number of polygons
    vrottag = c4d.VertexColorTag(mypoly.GetPointCount())
    vrottag.SetName("rot_vertex_map")
    vscaletag = c4d.VertexColorTag(mypoly.GetPointCount())
    vscaletag.SetName("scale_vertex_map")
    
    rotdata = vrottag.GetDataAddressW()
    scaledata = vscaletag.GetDataAddressW()
    
    i = 0
    for obj in objs:
        pos = obj.GetAbsPos()
        rot = obj.GetAbsRot()
        scale = obj.GetAbsScale()
        mypoly.SetPoint(i, c4d.Vector(pos.x, pos.y, pos.z))
        c4d.VertexColorTag.SetColor(rotdata, None, None, i, c4d.Vector(rot.x, rot.y, rot.z))
        c4d.VertexColorTag.SetColor(scaledata, None, None, i, c4d.Vector(scale.x, scale.y, scale.z))
        i = i + 1
 
    #mypoly.SetPolygon(0, c4d.CPolygon(0, 1, 2,3) ) #The Polygon's index, Polygon's points
    
    mypoly.InsertTag(vrottag)
    mypoly.InsertTag(vscaletag)
    
    doc.InsertObject(mypoly,None,None)
    mypoly.Message(c4d.MSG_UPDATE)
 
    c4d.EventAdd()

if __name__=='__main__':
    main()
