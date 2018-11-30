import c4d, os, sys, json, requests, loutils

import MaterialX as mx
from Qt import QtWidgets

# load Arnold python modules

PLUGIN_PATH = os.path.join(c4d.storage.GeGetStartupPath(), "plugins", "C4DtoA")
ARNOLD_PLUGIN_PATH = os.environ.get("ARNOLD_PLUGIN_PATH")
USE_RELATIVE_PATHS = True

arnoldPythonPath = os.path.join(PLUGIN_PATH, "arnold", "python")
sys.path.append(arnoldPythonPath)
from arnold import *

# other globals
ID_LUMIEREALEMBICEDITOR = 1039161

LUMI_OVERRIDES =               4001
LUMI_SHADERASSIGNATION =       4002
LUMI_DISPLACEMENTASSIGNATION = 4003
ARNOLD_SHADER_NETWORK       = 1033991
ARNOLD_PARAM_TAG = 1029989

ARNOLD_RENDER_COMMAND = 1038578

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
       
MAX_OBJECTS = 5000

oarch = None

def main():
    loutils.renameObjsPadding(doc, 'test', 3)
    
# quick test to see a Qt program running in C4D    
def runQt():
    resp = requests.get('https://todolist.example.com/tasks/')
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication(sys.argv)
    
    app.setQuitOnLastWindowClosed(True)
    x = QtWidgets.QWidget(windowTitle='Lumiere Editor')
    x.show()
    app.exec_()
   
# Process a materialx document gathering shaders    
def materialxread():
    matxPath = c4d.storage.LoadDialog()
    if not matxPath: 
        return
    
    doc = mx.createDocument()
    mx.readFromXmlFile(doc, matxPath)
    
    # Iterate through materials.
    for material in doc.getMaterials():
        # For each shader parameter, compute its value in the context of this material.
        print material.getName()
        print material.getPrimaryShaderParameters()

# Test get scale vector
def testscalevector():
    obj = doc.GetActiveObject()
    matx = obj.GetMg()
    x = matx.v1.GetLength()
    y = matx.v2.GetLength()
    z = matx.v3.GetLength()
    
    print str(x) + "," + str(y) + "," + str(z) 
    scalevec = c4d.Vector(x, y, z)

# Test Arnold iteration
def arnolditerationtests():
    # fire off the IPR to gather arnold nodes
    c4d.CallCommand(ARNOLD_RENDER_COMMAND, 1)
    
    # next we go though the shaders themselves picking up all root shaders and making networks
    aiNodeIterator = AiUniverseGetNodeIterator(AI_NODE_SHADER)
    
    while not AiNodeIteratorFinished(aiNodeIterator):
        node = AiNodeIteratorGetNext(aiNodeIterator)
        
        if AiNodeGetName(node) != '':
            print AiNodeGetName(node)
            

    c4d.CallCommand(ARNOLD_RENDER_COMMAND, 0)

def jsontester():
    with open("H:/Documents/asset_library/evermotion/archinteriors_vol_32/scene_10/alembic/ai32_scene10_main.json") as f:
        data = json.load(f)
       
    for entry in data["shaders"]:
        shader = data["shaders"][entry]
        for geo in shader['geo']:
            print geo

def material_assign_export_json_test():
    objects = []
    mat = doc.GetFirstMaterial()
    
    matcnt = doc.GetMaterials()
    
    amats = []
    while mat:
        mat.Message(c4d.MSG_UPDATE)
        mad = mat[c4d.ID_MATERIALASSIGNMENTS]
        amats.append(AssignMaterial(mat.GetName()))
        if mad == None:
            return
        
        #print mat.GetName()+ "," + str(mad.GetObjectCount())
        
        for i in range(mad.GetObjectCount()):
            atom = mad.ObjectFromIndex(doc, i)
            if atom == None: continue
            
            # we need to check if the texture tag has a selection,
            # if so we need to specify its a group, other programs
            # have different ways of handling these so we want to
            # notify them
            if atom.GetObject() not in objects:
                objects.append(atom.GetObject())
                    
            if atom.IsInstanceOf(c4d.Ttexture):
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
    
    print json.dumps(data, indent=2)
        
def gettpchanneltype():
    tp = doc.GetParticleSystem()
    print tp.DataChannelType(0)
    
def gathermaterials():
    mat = doc.GetFirstMaterial()
    
    matcnt = doc.GetMaterials()
    
    print len(matcnt)
    
    while mat:
        mad = mat[c4d.ID_MATERIALASSIGNMENTS]
        if mad == None:
            return
        
        print mat.GetName()+ "," + str(mad.GetObjectCount())
        for i in range(mad.GetObjectCount()):
            atom = mad.ObjectFromIndex(doc, i)
            if atom == None: continue
            
            if atom.IsInstanceOf(c4d.Ttexture):
                tag = atom
                obj = tag.GetObject()
                print obj.GetName()
                
            
        mat = mat.GetNext()
    
def vertexcolortest():
    # since c4d only allows 0-1 color values well have to store
    # our heierarchy ID as a normalized value for a certain max
    # number of objects
    tag = op.GetTag(c4d.Tvertexcolor)
    data = tag.GetDataAddressW()
    objid = 1
    white = c4d.Vector(objid/MAX_OBJECTS)
    pointCount = op.GetPointCount()
    
    for idx in xrange(pointCount):
        c4d.VertexColorTag.SetColor(data, None, None, idx, white)

    c4d.EventAdd()
    
# testing setting index data in basecontainers
def setbasecontainerindex():
    bc = op.GetDataInstance()
    bcindex = c4d.BaseContainer()
    for i in range(0,10):
        bcindex.SetIndexData(i, i*2)
    bc.SetData(4001, bcindex)
    
def getbasecontainerindex():
    bc = op.GetData()
    bc2 = bc.GetData(4001)
    print bc2
    #print bc2.GetIndexData(0)
    #print "index " + str(0) + ": " + str()
    #for j in range(0,10):
        
    
# simple test to see whether copying a tag container from one
# tag to another tag of the same type copied all the values
# The answer: yes it does!
def tagbasecontainercopy():
    objs = op.GetChildren()
    
    tag = objs[0].GetFirstTag()
    bc = tag.GetData()
    
    tag2 = objs[1].GetFirstTag()
    tag2.SetData(bc, add=False)
    
    c4d.EventAdd()

# trying to create a new material with the same Basecontainer
# as the old one
def matbasecontainercopy():
    mat = doc.GetActiveMaterial()
    bc = mat.GetData()
    
    newmat = c4d.BaseMaterial(ARNOLD_SHADER_NETWORK)
    newmat.SetData(bc, add=False)
    
    doc.InsertMaterial(newmat)
    c4d.EventAdd()
    
# test to create a simple no points poly object    
def pointobjtest():
    obj = c4d.BaseObject(c4d.Opolygon)
    doc.InsertObject(obj)
    
# testing api path fuctions
def apppaths():
    print c4d.storage.GeGetStartupPath()
    
# converts all the selected objects children to spheres
def convert_to_spheres():
    objs = op.GetChildren()
    
    for obj in objs:
        name = obj.GetName()
        newObj = c4d.BaseObject(c4d.Osphere)
        newObj.SetName(name)
        newObj.SetMg(obj.GetMg())
        newObj[c4d.PRIM_SPHERE_RAD] = .3
        doc.InsertObject(newObj, op)    

# check the assignation string containers of the Lumiere Alembic
# object    
def CheckAssignations():
    print "---Assignations---"
    objbc = op.GetDataInstance()
    
    lumibc = objbc.GetContainer(ID_LUMIEREALEMBICEDITOR)
    
    print "Overrides: " + lumibc.GetString(LUMI_OVERRIDES)
    print "Shaders: " + lumibc.GetString(LUMI_SHADERASSIGNATION)
    print "Displacements: " + lumibc.GetString(LUMI_DISPLACEMENTASSIGNATION)
    
# testing object flipping by inverting z per point
def FlipPolyTest():
    for i in range(op.GetPointCount()):
        point = op.GetPoint(i)
        point.z = point.z * -1
        op.SetPoint(i, point)
    
    op.Message(c4d.MSG_UPDATE)
    
def MatrixTest():
    CheckCache()
    
    # mat mul
    """
    offsetMat = c4d.Matrix(c4d.Vector(0, 0, 0), c4d.Vector(1, 0, 0), c4d.Vector(0, 1, 0), c4d.Vector(0, 0, -1))
    op.SetMg(op.GetMg() * offsetMat)
    """
    
def UVTest():
    tag = op.GetTag(c4d.Tuvw)
    print tag.GetDataCount()
    
def CheckCache():
    genObj = op.GetCache()
    print genObj.GetPointCount()
    print genObj.GetType()
    
    print genObj.GetMl()
    c4d.EventAdd()
    
def CheckPath():
    #os.environ["PXR_PLUGINPATH_NAME"] = "C:/Program Files/MAXON/CINEMA 4D R18/plugins/Lumiere Pipeline Tools/share/usd/plugins"
    print os.environ['PXR_PLUGINPATH_NAME']   

if __name__=='__main__':
    main()
