import c4d
from c4d import gui

import math
# this script takes the selected objects and converts them into a 
# TP system with a matrix channel set as the global matrix, 
# the data is meant to be used in say Houdini to instance
# a sidecar file is create with the pid and the name of the object
# this is because c4d doesn't support strings as attributes in
# abc files currently

# the filename is expects is an .abc file, it will create a 
# sidecar text file right next to it

PARTICLE_GEO = 1001414

def GetMatrixDeterminant(m):
    m = m.GetNormalized()
    d = m.v1.x * (m.v2.y * m.v3.z - m.v2.z * m.v3.y) - m.v1.y * (m.v2.x * m.v3.z - m.v2.z * m.v3.x) + m.v1.z * (m.v2.x * m.v3.y - m.v2.y * m.v3.x)
    return math.copysign(1, d)

def main():
    filePath = c4d.storage.SaveDialog(c4d.FILESELECTTYPE_ANYTHING, "Export path...", c4d.FILESELECT_SAVE)
    paths = filePath.rsplit('\\', 1)
    
    filePath = paths[0] + "/"
    
    tokens = paths[1].split(".")
    
    fileName = tokens[0]
    
    objs = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_0)
    
    # we create a new doc because alembic exporting of a big
    # document can crash due to memory requirements, we only need
    # the particles
    partDoc = c4d.documents.BaseDocument()
    
    partDoc.ExecutePasses(None, True, True, True, c4d.BUILDFLAGS_0)

    tp = partDoc.GetParticleSystem()
    #tp.AddDataChannel(25, "fulltransform") # 25 is matrix
    partDoc.ExecutePasses(None, True, True, True, c4d.BUILDFLAGS_0)
    
    index = 0
    f = open(filePath + fileName + ".txt", 'w')
    
    #print len(objs)
    #f.write(str(len(objs)))
    #f.write("\n")
    
    pids = tp.AllocParticles(len(objs))
    
    for pid in pids:
        tp.SetPosition(pid, objs[index].GetMg().off)
        
        matx = objs[index].GetMg()
        sx = matx.v1.GetLength()
        sy = matx.v2.GetLength() #* GetMatrixDeterminant(matx)
        sz = matx.v3.GetLength()
    
        tp.SetScale(pid, c4d.Vector(sx, sy, sz))
        tp.SetAlignment(pid, objs[index].GetMg())
        #tp.SetPData(pid, 0, objMatrix)
        
        f.write(str(pid) + "," + objs[index].GetName())
        f.write("\n")
        
        index += 1
    
    
    f.close()
     
    partGeo = c4d.BaseObject(PARTICLE_GEO)
    partDoc.InsertObject(partGeo)
    
    # setup options and export alembic
    plug = c4d.plugins.FindPlugin(1028082, c4d.PLUGINTYPE_SCENESAVER)
    if plug is None:
        return
    
    export = {}
    if plug.Message(c4d.MSG_RETRIEVEPRIVATEDATA, export):
        if "imexporter" not in export:
            return
    
    options = export["imexporter"]
    if options is None:
        return
    
    options[c4d.ABCEXPORT_SELECTION_ONLY] = False
    options[c4d.ABCEXPORT_CAMERAS] = False
    options[c4d.ABCEXPORT_SPLINES] = False
    options[c4d.ABCEXPORT_HAIR] = False
    options[c4d.ABCEXPORT_XREFS] = False
    options[c4d.ABCEXPORT_GLOBAL_MATRIX] = False
    options[c4d.ABCEXPORT_HYPERNURBS] = False
    options[c4d.ABCEXPORT_SDS_WEIGHTS] = False
    options[c4d.ABCEXPORT_PARTICLES] = True
    options[c4d.ABCEXPORT_PARTICLE_GEOMETRY] = False
    options[c4d.ABCEXPORT_VISIBILITY] = False
    options[c4d.ABCEXPORT_UVS] = True
    options[c4d.ABCEXPORT_VERTEX_MAPS] = False
    options[c4d.ABCEXPORT_NORMALS] = True
    options[c4d.ABCEXPORT_POLYGONSELECTIONS] = True
    options[c4d.ABCEXPORT_VERTEX_COLORS] = False
    options[c4d.ABCEXPORT_POINTS_ONLY] = True
    options[c4d.ABCEXPORT_DISPLAY_COLORS] = False
    options[c4d.ABCEXPORT_MERGE_CACHE] = False
    options[c4d.ABCEXPORT_FRAME_START] = 0
    options[c4d.ABCEXPORT_FRAME_END] = 0
    options[c4d.ABCEXPORT_FRAME_STEP] = 1
    options[c4d.ABCEXPORT_SUBFRAMES] = 1
    
    # Finally export the document
    if c4d.documents.SaveDocument(partDoc, filePath + fileName + ".abc", c4d.SAVEDOCUMENTFLAGS_DONTADDTORECENTLIST, 1028082):
        print "Document successfully exported to:"
        print filePath + fileName + ".abc"
    else:
        print "Export failed!"
    
    c4d.EventAdd()

if __name__=='__main__':
    main()
