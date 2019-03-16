import c4d, json, re
from c4d import gui, utils

ARNOLD_ASS_EXPORT = 1029993

C4DTOA_MSG_TYPE = 1000
C4DTOA_MSG_QUERY_SHADER_NETWORK = 1028
C4DTOA_MSG_RESP3 = 2013
C4DTOA_MSG_RESP4 = 2014

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

C4DTOA_MSG_TYPE = 1000
C4DTOA_MSG_ADD_CONNECTION = 1031

C4DTOA_MSG_PARAM1 = 2001
C4DTOA_MSG_PARAM2 = 2002
C4DTOA_MSG_PARAM3 = 2003
C4DTOA_MSG_PARAM4 = 2004

C4DTOA_MSG_RESP1 = 2011
C4DTOA_MSG_RESP2 = 2012
C4DTOA_MSG_RESP3 = 2013
C4DTOA_MSG_RESP4 = 2014
C4DTOA_MSG_QUERY_SHADER_NETWORK = 1028
C4DTOA_MSG_ADD_SHADER = 1029

# from c4dtoa_symbols.h
ARNOLD_SHADER_NETWORK = 1033991
ARNOLD_SHADER_GV = 1033990
ARNOLD_C4D_SHADER_GV = 1034190
ARNOLD_PARAM_TAG = 1029989

# from api/util/NodeIds.h
C4DAIN_IMAGE = 262700200

# from res/description/gvarnoldshader.h
C4DAI_GVSHADER_TYPE = 200

# from res/description/gvc4dshader.h
C4DAI_GVC4DSHADER_TYPE = 200

# from res/description/ainode_image.h
C4DAIP_IMAGE_FILENAME = 1737748425

class AssignMaterial(object):
    def __init__(self, matname):
        self.matname = matname
        self.objects = []
        self.groups = []

class TextureInfo:
    def __init__(self, mat, shader, texturePath):
        self.material = mat
        self.shader = shader
        self.path = texturePath                

def CreateArnoldShader(material, nodeId, posx, posy):
    msg = c4d.BaseContainer()
    msg.SetInt32(C4DTOA_MSG_TYPE, C4DTOA_MSG_ADD_SHADER)
    msg.SetInt32(C4DTOA_MSG_PARAM1, ARNOLD_SHADER_GV)
    msg.SetInt32(C4DTOA_MSG_PARAM2, nodeId)
    msg.SetInt32(C4DTOA_MSG_PARAM3, posx)
    msg.SetInt32(C4DTOA_MSG_PARAM4, posy)
    material.Message(c4d.MSG_BASECONTAINER, msg)
    return msg.GetLink(C4DTOA_MSG_RESP1)

def AddConnection(material, srcNode, dstNode, dstPortId):
    msg = c4d.BaseContainer()
    msg.SetInt32(C4DTOA_MSG_TYPE, C4DTOA_MSG_ADD_CONNECTION)
    msg.SetLink(C4DTOA_MSG_PARAM1, srcNode)
    msg.SetInt32(C4DTOA_MSG_PARAM2, 0)
    msg.SetLink(C4DTOA_MSG_PARAM3, dstNode)
    msg.SetInt32(C4DTOA_MSG_PARAM4, dstPortId)
    material.Message(c4d.MSG_BASECONTAINER, msg)
    return msg.GetBool(C4DTOA_MSG_RESP1)

def SetRootShader(material, shader, rootPortId):
    msg = c4d.BaseContainer()
    msg.SetInt32(C4DTOA_MSG_TYPE, C4DTOA_MSG_CONNECT_ROOT_SHADER)
    msg.SetLink(C4DTOA_MSG_PARAM1, shader)
    msg.SetInt32(C4DTOA_MSG_PARAM2, 0)
    msg.SetInt32(C4DTOA_MSG_PARAM3, rootPortId)
    material.Message(c4d.MSG_BASECONTAINER, msg)
    return msg.GetBool(C4DTOA_MSG_RESP1)

def QueryNetwork(material):
    msg = c4d.BaseContainer()
    msg.SetInt32(C4DTOA_MSG_TYPE, C4DTOA_MSG_QUERY_SHADER_NETWORK)
    material.Message(c4d.MSG_BASECONTAINER, msg)
    return msg
 
def GetTexturePath(mat, shader):
    if shader is None: return None
    
    data = shader.GetOpContainerInstance()
        
    if shader.GetOperatorID() == ARNOLD_C4D_SHADER_GV:
        nodeId = data.GetInt32(C4DAI_GVC4DSHADER_TYPE)
        print "Node ID: " + str(nodeId)
        if nodeId == c4d.Xbitmap:
            # the C4D shader is attached to the GV node
            c4d_shader = shader.GetFirstShader()
            if c4d_shader is not None:
               outports = shader.GetOutPorts(0)
               if outports[0]:    
                  if outports[0].GetNrOfConnections() > 0:
                     inport = outports[0].GetDestination()
                     connectedNode = inport[0].GetNode()
                     print "Connected shader: " + connectedNode.GetName()
               
                     image = CreateArnoldShader(mat, C4DAIN_IMAGE, 0, 50)
                     if image is None:
                        raise Exception("Failed to create image shader")
                     
                     imagepath = c4d_shader.GetDataInstance().GetFilename(c4d.BITMAPSHADER_FILENAME)
                     image.GetOpContainerInstance().SetFilename(C4DAIP_IMAGE_FILENAME, imagepath)
                     image.GetOpContainerInstance().SetString(868305056, 'linear')
                     AddConnection(mat, image, connectedNode, inport[0].GetMainID())
                     shader.Remove()

    return None

# swap C4D Arnold Bitmap shaders for Arnold Image nodes
def swapC4DBitmapforArnoldImage(doc):
    textures = []
    
    # collect textures
    mat = doc.GetFirstMaterial()
    while mat:
        if mat.GetType() == ARNOLD_SHADER_NETWORK:
            # query network
            network = QueryNetwork(mat)
            # iterate over shaders
            numShaders = network.GetInt32(C4DTOA_MSG_RESP1)
            for i in range(0, numShaders):
                shader = network.GetLink(10000+i)
                texturePath = GetTexturePath(mat, shader)
                if texturePath:
                    texture = TextureInfo(mat, shader, texturePath)
                    textures.append(texture)
        
        mat = mat.GetNext()

    # print textures
    print "-----------------------"
    print "%d texture(s) found" % len(textures)
    i = 1
    for texture in textures:
        print " %d. %s.%s: %s" % (i, texture.material.GetName(), texture.shader.GetName(), texture.path)
        i += 1
                        
# will rename the selected objects with a number padding
def renameObjsPadding(doc, name, fill, c=False):
    objs = None
    if c:
        aObj = doc.GetActiveObject()
        if aObj:
            objs = aObj.GetChildren()
    else:
        objs = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_0)
    
    if objs:
        i = 0
        for obj in objs:
            num = str(i)
            name = name + num.zfill(fill)
            obj.SetName(name)
            i += 1
            
        c4d.EventAdd()

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
    
# takes an object with poly selection and breaks it up so the selections are children of the parent, also keeps child material
# assignments, useful in ARnold mtlx workflows, and packed disk workflows since we can't reach polygroups
def polyselectionbreak(bdoc, bobj):
    if not bobj: return
    
    obj = bobj # the modeling commands change the bobj so we need to store this
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
    
# Takes selected objects, isolates them to seperate documents, and exports them as alembics
# in the file select it expects a path you want to dump the files to, the filename doesn't matter    
def exportAssets(doc):
    filePath = c4d.storage.SaveDialog(c4d.FILESELECTTYPE_ANYTHING, "Export path...", c4d.FILESELECT_SAVE)
    paths = filePath.rsplit('\\', 1)
    
    filePath = paths[0] + "/"
    
    objs = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_0)
    
    for obj in objs:
        bldgdoc = c4d.documents.IsolateObjects(doc, [obj])
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
        
        c4d.documents.KillDocument(bldgdoc)
    
    c4d.EventAdd()

def SanitizeEndNumber(name, symbol):
    # C4D Alembic mangles numbers at the end if they begin
    # with '_', so we check that and convert to '-'
    if(name.split(symbol)[-1].isdigit()):
        nname_parse = name.rsplit(symbol, 1)
        name = nname_parse[0] + '-' + nname_parse[1]
        print name

    return name

# compares a name with a list of stored names and if it matches creates a new unique name
def CompareName(name, symbol, unique_names):
    # if the name is not unique we'll keep trying indexes here till we find a name 
    # that's unique
    if name in unique_names:
        newname = None
        index = 0

        while(1):            
            newname = name + symbol + str(index)
            newname = SanitizeEndNumber(newname, symbol)

            if newname in unique_names:
                index += 1
            else:
                unique_names.append(newname)
                return newname         
            

    # if we make it here just sanitize the numbers on the passed in name
    name = SanitizeEndNumber(name, symbol)
    unique_names.append(name)

    return name

def sanitize_name(obj, symbol, unique_names):
    # replaces invalid symbols in a name with the symbol specified
    # by the user, then compares it against the unique name list
    name = obj.GetName()

    newname = re.sub(r"[/\?\[\.|_\- \]#]", symbol, name)
    newname = newname.lower()

    newname = CompareName(newname, symbol, unique_names)

    #print newname
    obj.SetName(newname)

# renames objects materials and poly selection tags so the names
# are consistent during export, if names have special characters
# or exact same names they can and will get mangled by the C4D
# export process, this is bad as we rely on exact same names for
# many of our tools in other programs
def name_sanitizer(doc):
    unique_names = []

    # sanitize objects
    obj = doc.GetFirstObject()

    if obj is None:
        return

    while obj:
        sanitize_name(obj, "_", unique_names)

        tag = obj.GetFirstTag()
        while tag:
            if tag.GetType() == 5673: # poly selection
                # it's possible that a selection could have the
                # same name as another on a different object
                # this is a material conflict in other programs
                # also selections that begin with a number are a
                # no go as well, so this works great

                old_sel_name = tag.GetName()

                tag.SetName(obj.GetName() + "_" + tag.GetName())

                sanitize_name(tag, "_", unique_names)

                new_sel_name = tag.GetName()

                # Selection tags aren't linked, we have to go
                # the texture tags replacing the old name with the
                #new one
                textag = obj.GetFirstTag()
                while textag:
                    if textag.GetType() == 5616: # texture tag
                        if old_sel_name == textag[c4d.TEXTURETAG_RESTRICTION]:
                            textag[c4d.TEXTURETAG_RESTRICTION] = new_sel_name

                    textag = textag.GetNext()

            tag = tag.GetNext()

        obj = GetNextObject(obj)

    c4d.EventAdd()

    # sanitize materials
    mat = doc.GetFirstMaterial()

    if mat is None:
        return

    while mat:
        sanitize_name(mat, "_", unique_names)

        mat = mat.GetNext()

    c4d.EventAdd()