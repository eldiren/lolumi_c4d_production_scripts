import c4d, csv
from c4d import gui

color_data = [
('dark_skin',116,80,67),
('light_skin',196,149,129),
('blue_sky',91,122,155),
('foliage',88,109,67),
('blue_flower',128,127,175),
('bluish_green',90,190,169),
('orange',221,119,44),
('purplish_blue',71,90,164),
('moderate_red',198,81,98),
('purple',93,60,107),
('yellow_green',158,88,64),
('orange_yellow',234,161,49),
('blue',47,59,151),
('green',65,150,71),
('red',181,40,59),
('yellow',241,200,38),
('magenta',190,78,146),
('cyan',0,134,164),
('white',242,242,236),
('neutral',200,200,199),
('neutral2',159,160,159),
('neutral3',122,121,119),
('neutral4',84,84,84),
('black',53,53,53)
]

def main():
    plane = c4d.BaseObject(c4d.Oplane)
    plane[c4d.PRIM_AXIS] = 4
    plane[c4d.PRIM_PLANE_WIDTH] = 235
    plane[c4d.PRIM_PLANE_HEIGHT] = 150
    plane[c4d.PRIM_PLANE_SUBW] = 6
    plane[c4d.PRIM_PLANE_SUBH] = 4
    plane[c4d.ID_BASEOBJECT_REL_SCALE,c4d.VECTOR_X] = -1
    doc.InsertObject(plane)
    plane.MakeTag(1001001) # align to camera tag

    i = 0
    for color in color_data:
        mat = c4d.BaseMaterial(c4d.Mmaterial)
        mat.SetName(color[0])
        color = c4d.Vector(float(color[1])/255, float(color[2])/255, float(color[3])/255)

        mat[c4d.MATERIAL_COLOR_COLOR] = color

        doc.InsertMaterial(mat)

        stag = plane.MakeTag(c4d.Tpolygonselection)
        stag.SetName(str(color[0]) + '_sel')
        sel = stag.GetBaseSelect()
        sel.Select(i)

        tTag = plane.MakeTag(c4d.Ttexture)
        tTag[c4d.TEXTURETAG_RESTRICTION] = stag.GetName()
        tTag.SetMaterial(mat)

        i += 1

    c4d.EventAdd()

if __name__=='__main__':
    main()