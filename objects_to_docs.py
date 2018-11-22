import c4d
from c4d import gui, utils

import json
# Takes selected objects, isolates them to seperate documents,
# and exports them as alembics

# in the file select it expects a path you want to dump the files
# to, the filename doesn't matter


ARNOLD_ASS_EXPORT = 1029993

C4DTOA_MSG_TYPE = 1000
C4DTOA_MSG_QUERY_SHADER_NETWORK = 1028
C4DTOA_MSG_RESP3 = 2013
C4DTOA_MSG_RESP4 = 2014

# from c4dtoa_symbols.h
ARNOLD_SHADER_NETWORK = 1033991
ARNOLD_PARAM_TAG = 1029989

# from aitag_polymesh.h
C4DAIP_POLYMESH_SUBDIV_TYPE = 363257074
C4DAIP_POLYMESH_DISP_HEIGHT = 1039494868
C4DAIP_POLYMESH_SUBDIV_ITERATIONS = 1150993202
C4DAIP_POLYMESH_DISP_ZERO_VALUE = 465261457
C4DAIP_POLYMESH_SUBDIV_ADAPTIVE_METRIC = 105511967
C4DAIP_POLYMESH_DISP_PADDING = 1635638890
C4DAIP_POLYMESH_SUBDIV_ADAPTIVE_ERROR = 1419435975
C4DAIP_POLYMESH_SUBDIV_SMOOTH_DERIVS = 67579894 # Also known as smooth tangents
C4DAIP_POLYMESH_SUBDIV_UV_SMOOTHING = 692060114
C4DAIP_POLYMESH_SUBDIV_ADAPTIVE_SPACE = 1435948073
C4DAIP_POLYMESH_OPAQUE = 408131505
C4DAIP_POLYMESH_MATTE = 1707214561
C4DAIP_POLYMESH_DISP_AUTOBUMP = 486485632
C4DAIP_POLYMESH_INVERT_NORMALS = 1481506281
C4DAIP_POLYMESH_RECEIVE_SHADOWS = 1195032865
C4DAIP_POLYMESH_SELF_SHADOWS = 2016658438
C4DAIP_POLYMESH_SMOOTHING = 1333877372
C4DAI_POLYMESH_SSS_SET_NAME = 1102

class AssignMaterial(object):
    def __init__(self, matname):
        self.matname = matname
        self.objects = []
        self.groups = []
        
def QueryNetwork(material):
    msg = c4d.BaseContainer()
    msg.SetInt32(C4DTOA_MSG_TYPE, C4DTOA_MSG_QUERY_SHADER_NETWORK)
    material.Message(c4d.MSG_BASECONTAINER, msg)
    return msg

def GetNextObject(op):
    if op==None:
        return None
  
    if op.GetDown():
        return op.GetDown()
  
    while not op.GetNext() and op.GetUp():
        op = op.GetUp()
  
    return op.GetNext()
 
 
def GetAllObjects(odoc):
    objects = []
    op = odoc.GetFirstObject()
    
    if op is None:
        return
  
    while op:
        objects.append(op)
        op = GetNextObject(op)
 
    return objects
    
# takes an object with poly selection and breaks it up so the 
# selection are children of the parent, also keeps child material
# assignments, useful in ARnold mtlx workflows, and packed disk
# workflows since we can't reach polygroups
def polyselectionbreak(bdoc, bobj):
    if not bobj: return
    
    obj = bobj # the modeling commands change the op so we need to store this
    gMatrix = bobj.GetMg()
    tag = obj.GetFirstTag()
    
    newChildren = []
    
    while tag:
        if tag.GetType() == c4d.Tpolygonselection:
            # deselect all polygons
            polyselection = obj.GetPolygonS()
            polyselection.DeselectAll()
            
            # select polygons from selection tag
            tagselection = tag.GetBaseSelect()
            tagselection.CopyTo(polyselection)
            
            #split: polygonselection to a new object
            sec = utils.SendModelingCommand(command=c4d.MCOMMAND_SPLIT, list=[obj], mode=c4d.MODELINGCOMMANDMODE_POLYGONSELECTION, doc=bdoc)
             
            if not sec:
                print 'split failed for ' + tag.GetName() 
                continue    
                               
            sec[0].SetName(tag.GetName())
            sec[0][c4d.ID_BASEOBJECT_REL_POSITION] = c4d.Vector(0,0,0)
            sec[0][c4d.ID_BASEOBJECT_REL_ROTATION] = c4d.Vector(0,0,0)
            
            # remove polyselections and textures from the split and find a material to keep
            secTag = sec[0].GetTag(c4d.Tpolygonselection)
            
            while secTag:
                secTag.Remove()
                secTag = sec[0].GetTag(c4d.Tpolygonselection)
                
            secTag = sec[0].GetFirstTag()
            
            while secTag:
                oldSecTag = None
                if secTag.GetType() == c4d.Ttexture:
                    if secTag[c4d.TEXTURETAG_RESTRICTION] == tag.GetName():
                        secTag[c4d.TEXTURETAG_RESTRICTION] = ''
                    else:
                        oldSecTag = secTag               
                    
                secTag = secTag.GetNext()
                if oldSecTag:
                    oldSecTag.Remove()
            
            # loop through tags and find any texture tags that have the selection and delete
            oldMatTag = None
            matTag = obj.GetFirstTag()
            while matTag:
                if matTag.GetType() == c4d.Ttexture:
                    if matTag[c4d.TEXTURETAG_RESTRICTION] == tag.GetName():
                        oldMatTag = matTag
                        
                matTag = matTag.GetNext()
                
                if oldMatTag: 
                    oldMatTag.Remove()     
                         
            newChildren.append(sec[0])
            #delete the polygons from selectiontag
            utils.SendModelingCommand(command=c4d.MCOMMAND_DELETE, list=[obj], mode=c4d.MODELINGCOMMANDMODE_POLYGONSELECTION, doc=bdoc)
            
            
        tag = tag.GetNext()
        
    # remove selection tags
    tag = obj.GetTag(c4d.Tpolygonselection)
            
    while tag:
        tag.Remove()
        tag = obj.GetTag(c4d.Tpolygonselection)  
    
    # Optimize in order to remove loose points
    options = c4d.BaseContainer()
    options[c4d.MDATA_OPTIMIZE_TOLERANCE] = 0.001
    options[c4d.MDATA_OPTIMIZE_POINTS] = True
    options[c4d.MDATA_OPTIMIZE_POLYGONS] = False
    options[c4d.MDATA_OPTIMIZE_UNUSEDPOINTS] = True
    utils.SendModelingCommand(c4d.MCOMMAND_OPTIMIZE, list = [obj], mode = c4d.MODELINGCOMMANDMODE_ALL, bc = options, doc = obj.GetDocument())
    
    if (obj.GetPolygonCount() == 0): # no more polys                           
        if (obj.GetChildren() > 0): # there are children remove this and replace with null then readd the children
            objNull = c4d.BaseObject(c4d.Onull)
            objNull.SetName(obj.GetName())
            objParent = obj.GetUp()
            obj.Remove()
        
            obj = objNull
            bdoc.InsertObject(obj, objParent)
            obj.SetMg(gMatrix)
        elif (obj.GetChildren() == 0): # No children, we don't want a parent remain so let's axe this
            objParent = obj.GetUp()
            obj.Remove()
            obj = objParent
        
    for child in newChildren:
        child.InsertUnder(obj)
        
    c4d.EventAdd()
    
def main():
    filePath = c4d.storage.SaveDialog(c4d.FILESELECTTYPE_ANYTHING, "Export path...", c4d.FILESELECT_SAVE)
    paths = filePath.rsplit('\\', 1)
    
    filePath = paths[0] + "/"
    
    objs = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_0)
    
    for obj in objs:
        bldgdoc = c4d.documents.IsolateObjects(doc, [obj])
        c4d.documents.InsertBaseDocument(bldgdoc)
        bldgdoc.SetDocumentName(obj.GetName())
        c4d.documents.SetActiveDocument(bldgdoc)
        
        mainparent = bldgdoc.GetFirstObject()
        
        # if this object has children then we'll delete the parent
        # so the pathing in the alembic is simpler, if it has no
        # children then it's the only object so we leave it alone
        if mainparent:
            if len(mainparent.GetChildren()) > 0:
                mainparent.SetBit(c4d.BIT_ACTIVE)
                c4d.CallCommand(1019951) # delete without children
        
        # next we loop though all the objects and break the polyselections
        # up if there are any
        objs = GetAllObjects(bldgdoc)
        
        for obj in objs:
            if obj.GetTag(c4d.Tpolygonselection):
                polyselectionbreak(bldgdoc, obj)
            
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
        options[c4d.ABCEXPORT_PARTICLES] = False
        options[c4d.ABCEXPORT_PARTICLE_GEOMETRY] = False
        options[c4d.ABCEXPORT_VISIBILITY] = False
        options[c4d.ABCEXPORT_UVS] = True
        options[c4d.ABCEXPORT_VERTEX_MAPS] = False
        options[c4d.ABCEXPORT_NORMALS] = True
        options[c4d.ABCEXPORT_POLYGONSELECTIONS] = True
        options[c4d.ABCEXPORT_VERTEX_COLORS] = False
        options[c4d.ABCEXPORT_POINTS_ONLY] = False
        options[c4d.ABCEXPORT_DISPLAY_COLORS] = False
        options[c4d.ABCEXPORT_MERGE_CACHE] = False
        options[c4d.ABCEXPORT_FRAME_START] = 0
        options[c4d.ABCEXPORT_FRAME_END] = 0
        options[c4d.ABCEXPORT_FRAME_STEP] = 1
        options[c4d.ABCEXPORT_SUBFRAMES] = 1
        
        fileName = filePath + obj.GetName() + ".abc"
        
        # Finally export the document
        if c4d.documents.SaveDocument(bldgdoc, fileName, c4d.SAVEDOCUMENTFLAGS_DONTADDTORECENTLIST, 1028082):
            print "Document successfully exported to:"
            print fileName
        else:
            print "Export failed!"
        
        c4d.EventAdd()
        
        # call material assign export
        material_assign_export(bldgdoc, filePath + obj.GetName() + ".json")
    
        # call arnold material export
        arnold_material_export(bldgdoc, filePath + obj.GetName() + ".ass")
    
    c4d.EventAdd()

def material_assign_export(matdoc, fileName):
    objects = []
    f = open(fileName, 'w')
    
    mat = matdoc.GetFirstMaterial()
    
    matcnt = matdoc.GetMaterials()
    
    amats = []
    while mat:
        mat.Message(c4d.MSG_UPDATE)
        mad = mat[c4d.ID_MATERIALASSIGNMENTS]
        amats.append(AssignMaterial(mat.GetName()))
        if mad == None:
            return
        
        #print mat.GetName()+ "," + str(mad.GetObjectCount())
        
        for i in range(mad.GetObjectCount()):
            atom = mad.ObjectFromIndex(matdoc, i)
            if atom == None: continue
            
            # we need to check if the texture tag has a selection,
            # if so we need to specify its a group, other programs
            # have different ways of handling these so we want to
            # notify them
            if atom.IsInstanceOf(c4d.Ttexture):
                if atom.GetObject() not in objects:
                    objects.append(atom.GetObject())
                    
                if atom[c4d.TEXTURETAG_RESTRICTION] != "":
                    amats[-1].groups.append(atom[c4d.TEXTURETAG_RESTRICTION])
                else:
                    amats[-1].objects.append(atom.GetObject().GetName())
            
        mat = mat.GetNext()
    #setup json data
    data = {"shaders" : {}, "overrides" : {}}
    
    # loop through objects get their overrides and write them out
    for obj in objects:
        tag = obj.GetTag(ARNOLD_PARAM_TAG)
        if tag:
            value = {}
            if tag[C4DAIP_POLYMESH_SUBDIV_TYPE] != 0 :
                value["subdiv_type"] = tag[C4DAIP_POLYMESH_SUBDIV_TYPE]
                value["disp_height"] = tag[C4DAIP_POLYMESH_DISP_HEIGHT]
                value["subdiv_iterations"] = tag[C4DAIP_POLYMESH_SUBDIV_ITERATIONS]
                value["disp_zero_value"] = tag[C4DAIP_POLYMESH_DISP_ZERO_VALUE]
                value["subdiv_adaptive_metric"] = tag[C4DAIP_POLYMESH_SUBDIV_ADAPTIVE_METRIC]
                value["disp_padding"] = tag[C4DAIP_POLYMESH_DISP_PADDING]
                value["subdiv_adaptive_error"] = tag[C4DAIP_POLYMESH_SUBDIV_ADAPTIVE_ERROR]
                value["subdiv_smooth_derivs"] = tag[C4DAIP_POLYMESH_SUBDIV_SMOOTH_DERIVS] 
                value["subdiv_uv_smoothing"] = tag[C4DAIP_POLYMESH_SUBDIV_UV_SMOOTHING]
                value["subdiv_adaptive_space"] = tag[C4DAIP_POLYMESH_SUBDIV_ADAPTIVE_SPACE]
                

            value["opaque"] = tag[C4DAIP_POLYMESH_OPAQUE]
            value["matte"] = tag[C4DAIP_POLYMESH_MATTE]
            value["disp_autobump"] = tag[C4DAIP_POLYMESH_DISP_AUTOBUMP]
            value["invert_normals"] = tag[C4DAIP_POLYMESH_INVERT_NORMALS]
            value["receive_shadows"] = tag[C4DAIP_POLYMESH_RECEIVE_SHADOWS]
            value["self_shadows"] = tag[C4DAIP_POLYMESH_SELF_SHADOWS]
            value["sss_setname"] = tag[C4DAI_POLYMESH_SSS_SET_NAME]
            value["smoothing"] = tag[C4DAIP_POLYMESH_SMOOTHING]
            
            data['overrides'][obj.GetName()] = value                               
                
    # loop through the assigned materials and write them out
    for amat in amats:
        data['shaders'][amat.matname] = { "geo" : amat.objects, "groups" : amat.groups }
    
    json.dump(data, f, indent=2)
    
    f.close()
    
def arnold_material_export(assdoc, fileName):
    matdoc = c4d.documents.BaseDocument()
    c4d.documents.InsertBaseDocument(matdoc)

    matdoc.SetDocumentName(fileName)
    mat = assdoc.GetFirstMaterial()
    
    while mat:
        newmat = mat.GetClone()
            
        matdoc.InsertMaterial(newmat)
        obj = c4d.BaseObject(c4d.Opolygon)
        obj.SetName(newmat.GetName())
        tag = c4d.BaseTag(c4d.Ttexture)
        tag[c4d.TEXTURETAG_MATERIAL] = newmat
        
        obj.InsertTag(tag)
        matdoc.InsertObject(obj)
        
        mat = mat.GetNext()
     
    options = c4d.BaseContainer()
    options.SetFilename(0, fileName.decode("utf-8"))
    options.SetInt32(6, 0)
    options.SetInt32(7, 0)
    matdoc.GetSettingsInstance(c4d.DOCUMENTSETTINGS_DOCUMENT).SetContainer(ARNOLD_ASS_EXPORT, options)
 
    c4d.CallCommand(ARNOLD_ASS_EXPORT)
    
    c4d.documents.KillDocument(matdoc)
    
if __name__=='__main__':
    main()
