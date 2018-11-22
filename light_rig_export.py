import c4d, json
from c4d import gui

# from /api/include/util/NodeIds.h

C4DAIN_CYLINDER_LIGHT = 1944046294
C4DAIN_DISK_LIGHT = 998592185
C4DAIN_DISTANT_LIGHT = 1381557517
C4DAIN_MESH_LIGHT = 804868393
C4DAIN_PHOTOMETRIC_LIGHT = 1980850506
C4DAIN_POINT_LIGHT = 381492518
C4DAIN_QUAD_LIGHT = 1218397465
C4DAIN_SKYDOME_LIGHT = 2054857832
C4DAIN_SPOT_LIGHT = 876943490

# from /res/description/ainode_point_light.h

C4DAIP_POINT_LIGHT_COLOR = 1458609997
C4DAIP_POINT_LIGHT_RADIUS = 319355460
C4DAIP_POINT_LIGHT_INTENSITY = 1920590149
C4DAIP_POINT_LIGHT_EXPOSURE = 240944143
C4DAIP_POINT_LIGHT_NORMALIZE = 939253669

# from /res/description/ainode_skydome_light.h

C4DAIP_SKYDOME_LIGHT_COLOR = 268620635
C4DAIP_SKYDOME_LIGHT_INTENSITY = 310602835
C4DAIP_SKYDOME_LIGHT_EXPOSURE = 100719935
C4DAIP_SKYDOME_LIGHT_NORMALIZE = 1745726313
C4DAIP_SKYDOME_LIGHT_FORMAT = 156927185

# from /res/description/ainode_quad_light.h

C4DAIP_QUAD_LIGHT_COLOR = 2010942260

# from /api/include/customgui/ArnoldShaderLinkCustomGui.h

C4DAI_SHADERLINK_CONTAINER = 9988000
C4DAI_SHADERLINK_TYPE = 101
C4DAI_SHADERLINK_VALUE = 102
C4DAI_SHADERLINK_TEXTURE = 103
C4DAI_SHADERLINK_SHADER_NETWORK = 104
 
C4DAI_SHADERLINK_TYPE__CONSTANT = 1
C4DAI_SHADERLINK_TYPE__TEXTURE = 2
C4DAI_SHADERLINK_TYPE__SHADER_NETWORK = 3

# exports selected lights into a light rig defintion as json for 
# quick import into other scenes

def ReadShaderLinkGui(node, id):
    color = (0,0,0)
    use_texture = 0
    texture = ''
    
    if node[c4d.C4DAI_LIGHT_COMMON_USE_TEMPERATURE]:
        color = (node[100102].x, node[100102].y, node[100102].z)    
    else:  
        shaderLinkData = node.GetDataInstance().GetContainer(C4DAI_SHADERLINK_CONTAINER).GetContainer(id)

        guiType = shaderLinkData[C4DAI_SHADERLINK_TYPE]
        
        # color
        if guiType == C4DAI_SHADERLINK_TYPE__CONSTANT:
            color = (node[id].x, node[id].y, node[id].z)
            
        # texture
        if guiType == C4DAI_SHADERLINK_TYPE__TEXTURE:
            shader = shaderLinkData.GetLink(C4DAI_SHADERLINK_TEXTURE, node.GetDocument())
            use_texture = 1
            texture = shader[c4d.BITMAPSHADER_FILENAME]
     
        # shader network
        if guiType == C4DAI_SHADERLINK_TYPE__SHADER_NETWORK:
            material = shaderLinkData.GetLink(C4DAI_SHADERLINK_SHADER_NETWORK, node.GetDocument())
            print "material: %s" % (material.GetName() if material is not None else "none")
    
    return color, use_texture, texture

def main():
    filePath = c4d.storage.SaveDialog(c4d.FILESELECTTYPE_ANYTHING, "Light rig json file...", c4d.FILESELECT_SAVE)
    paths = filePath.rsplit('.', 1)
    
    filePath = paths[0]
    
    f = open(filePath + '.json', 'w')
    
    objs = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_0)
    
    data = {}
    
    for obj in objs:
        value = {}
        guiType = 0
        value['use_texture'] = 0
        c4dScale = .01
        
        objMatrix = obj.GetMg()
        objMatrix.off = objMatrix.off * c4dScale
        objMatrix.v1 = objMatrix.v1.GetNormalized()
        objMatrix.v2 = objMatrix.v2.GetNormalized()
        objMatrix.v3 = objMatrix.v3.GetNormalized()
        value['matrix'] = (objMatrix.v1.x, objMatrix.v1.y, -objMatrix.v1.z, 0, objMatrix.v2.x, objMatrix.v2.y, -objMatrix.v2.z, 0, -objMatrix.v3.x, -objMatrix.v3.y, objMatrix.v3.z, 0, objMatrix.off.x, objMatrix.off.y, -objMatrix.off.z, 1)
        
        if obj.GetType() == 1034624: # Arnold Sky
            value['type'] = 'skydome'
            
            color, use_texture, texture = ReadShaderLinkGui(obj, C4DAIP_SKYDOME_LIGHT_COLOR)
               
            if use_texture:
                value['use_texture'] = use_texture
                value['texture'] = texture
            else:    
                value['color'] = color
                
            data[obj.GetName()] = value
        if obj.GetType() == 1030424: # Arnold Light 
            if obj[101] == C4DAIN_POINT_LIGHT:
                value['type'] = 'point'
                
                value['color'] = (obj[C4DAIP_POINT_LIGHT_COLOR].x, obj[C4DAIP_POINT_LIGHT_COLOR].y, obj[C4DAIP_POINT_LIGHT_COLOR].z)
                
                value['radius'] = obj[C4DAIP_POINT_LIGHT_RADIUS]
                value['normalize'] = obj[C4DAIP_POINT_LIGHT_NORMALIZE]
                value['intensity'] = obj[C4DAIP_POINT_LIGHT_INTENSITY] * 2 ** obj[C4DAIP_POINT_LIGHT_EXPOSURE] 
            if obj[101] == C4DAIN_SKYDOME_LIGHT:
                value['type'] = 'skydome'
                
                color, use_texture, texture = ReadShaderLinkGui(obj, C4DAIP_SKYDOME_LIGHT_COLOR)
               
                if use_texture:
                    value['use_texture'] = use_texture
                    value['texture'] = texture
                else:    
                    value['color'] = color
                    
                value['format'] = obj[C4DAIP_SKYDOME_LIGHT_FORMAT]
                value['intensity'] = obj[C4DAIP_SKYDOME_LIGHT_INTENSITY] * 2 ** obj[C4DAIP_SKYDOME_LIGHT_EXPOSURE] 
                value['normalize'] = obj[C4DAIP_SKYDOME_LIGHT_NORMALIZE]
                   
            if obj[101] == C4DAIN_QUAD_LIGHT:
                value['type'] = 'quad'

                color, use_texture, texture = ReadShaderLinkGui(obj, C4DAIP_QUAD_LIGHT_COLOR)
               
                if use_texture:
                    value['use_texture'] = use_texture
                    value['texture'] = texture
                else:    
                    value['color'] = color
                
                value['intensity'] = obj[67722820] * 2 ** obj[1655166224] 
                value['normalize'] = obj[1502846298]
                value['width'] = obj[2034436501] * c4dScale
                value['height'] = obj[2120286158] * c4dScale
                value['roundness'] = obj[1641633270]
                value['soft_edge'] = obj[1632353189]
                value['spread'] = obj[1730825676]
            
            data[obj.GetName()] = value
        
    json.dump(data, f, indent=2)
    
    f.close()
    
if __name__=='__main__':
    main()
