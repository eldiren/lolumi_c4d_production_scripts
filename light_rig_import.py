import c4d, json
from c4d import gui

# from util/NodeIds.h

C4DAIN_CYLINDER_LIGHT = 1944046294
C4DAIN_DISK_LIGHT = 998592185
C4DAIN_DISTANT_LIGHT = 1381557517
C4DAIN_MESH_LIGHT = 804868393
C4DAIN_PHOTOMETRIC_LIGHT = 1980850506
C4DAIN_POINT_LIGHT = 381492518
C4DAIN_QUAD_LIGHT = 1218397465
C4DAIN_SKYDOME_LIGHT = 2054857832
C4DAIN_SPOT_LIGHT = 876943490

# exports selected lights into a light rig defintion as json for 
# quick import into other scenes

def main():
    renderer = 'arnold'
    c4dScale = 100
    
    filePath = c4d.storage.LoadDialog()
    
    f = open(filePath, 'r')
    
    data = json.load(f)  
    for lname in data:
        print lname
        light = data[lname]
        
        if(renderer == 'arnold'):
            c4dLight = c4d.BaseObject(1030424)
            c4dLight.SetName(lname)
            doc.InsertObject(c4dLight)
            
            objMatrix = c4d.Matrix()
            objMatrix.v1 = c4d.Vector(light['matrix'][0], light['matrix'][1], -light['matrix'][2])
            objMatrix.v2 = c4d.Vector(light['matrix'][4], light['matrix'][5], -light['matrix'][6])
            objMatrix.v3 = c4d.Vector(-light['matrix'][8], -light['matrix'][9], light['matrix'][10])
            objMatrix.off = c4d.Vector(light['matrix'][12], light['matrix'][13], -light['matrix'][14]) * c4dScale
            c4dLight.SetMg(objMatrix)
            
            c4dLight[2010942260] = c4d.Vector(light['color'][0], light['color'][1], light['color'][2])
            
            c4dLight[67722820] = light['intensity']
            c4dLight[1502846298] = light['normalize']
            
            c4dLight[1632353189] = light['soft_edge']
            c4dLight[1730825676] = light['spread']
            
            if light['type'] == 'point':
                c4dLight[c4d.C4DAI_LIGHT_TYPE] = 381492518
            elif light['type'] == 'spot':
                c4dLight[c4d.C4DAI_LIGHT_TYPE] = 876943490
            elif light['type'] == 'quad':
                c4dLight[c4d.C4DAI_LIGHT_TYPE] = 1218397465
                c4dLight[2034436501] = light['width'] * c4dScale
                c4dLight[2120286158] = light['height'] * c4dScale
                c4dLight[1641633270] = light['roundness']
            elif light['type'] == 'disk':
                c4dLight[c4d.C4DAI_LIGHT_TYPE] = 998592185           
            elif light['type'] == 'cylinder':
                c4dLight[c4d.C4DAI_LIGHT_TYPE] = 1944046294
        
    f.close()
    
    c4d.EventAdd()
    
if __name__=='__main__':
    main()  