import c4d
from c4d import gui
from c4d import storage
import alembic
from alembic.Abc import *
from alembic.AbcCoreAbstract import *
from alembic.AbcGeom import *
from imath import *
from pxr import Usd, UsdGeom

oarch = None
#Testing out write geo from C4D with Alembic and USD

def main():
    global oarch
    
    filename = storage.SaveDialog()
    if(filename != None):
        print filename
        stage = Usd.Stage.CreateNew(filename)
        xformPrim = UsdGeom.Xform.Define(stage, '/hello')
        spherePrim = UsdGeom.Sphere.Define(stage, '/hello/world')
        stage.GetRootLayer().Save()

        """
        CreateArchiveWithInfo(WriteArchive(), filename, "Temp Script", "")
        #oarch = OArchive('H:/Documents/lolumi/company_projects/test/alembic/exporttest_v01.abc')
    
        objs = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_0)
        for obj in objs:
            processObj(obj)
        """
        
def processObj(obj):
    print obj, "Type: ", obj.GetType()
    # BaseObjects in C4D could be anything, we check the deform cache first to see if the object has a deformed
    # state, then we check the regular cache, and then finally we can check if it's a spline, polygon, etc.
    # generators in turn may have many children in thier cache so we have to iterate through that too
    genObj = obj.GetDeformCache();
    if(genObj != None):
        processObj(obj)
    else:
        # check the cache
        genObj = obj.GetCache()
        if(genObj != None):
            processObj(genObj)
        else:
            if(obj.GetType() == c4d.Opolygon):
                print obj
                exportPoly(obj)
                
def exportPoly(obj):
    global oarch 
    
    xform = OXform(oarch.getTop(), obj.GetName())
    xsamp = XformSample()
    xsamp.setMatrix(M44d(1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1))
    #xsamp.setRotation(V3f(0,0,0))
    #xsamp.setScale(V3f(0,0,0))
    #xsamp.setTranslation(V3f(0,0,0))
    xform.getSchema().set(xsamp)
    
    shapeObj = OPolyMesh(oarch.getTop(), obj.GetName() + "Shape")
    points = V3fTPTraits.arrayType(len(obj.GetAllPoints()))
    i = 0
    for point in obj.GetAllPoints():
        points[i] = V3f(point.x, point.y, point.z)
        i = i + 1
        
    polys = obj.GetAllPolygons()
    
    faceIndices = []
    faceCounts = []
    for poly in obj.GetAllPolygons():
        faceIndices.append(poly.a)
        faceIndices.append(poly.b)
        faceIndices.append(poly.c)
        if(not poly.IsTriangle()):
            faceIndices.append(poly.d)
            faceCounts.append(4)
        else:
            faceCounts.append(3)        
    
    abcFaceIndices = Int32TPTraits.arrayType(len(faceIndices))
    print "Number of indices ", len(faceIndices)
    for i, indice in enumerate(faceIndices):
        abcFaceIndices[i] = indice
         
    abcFaceCounts = Int32TPTraits.arrayType(len(faceCounts))
    print "Number of face counts ", len(faceCounts)
    for i, count in enumerate(faceCounts):
        abcFaceCounts[i] = count
    
    shape_samp = OPolyMeshSchemaSample(points, abcFaceIndices, abcFaceCounts)
    shapeObj.getSchema().set(shape_samp)
    
    print shapeObj, " Mesh wrote out!"
    
if __name__=='__main__':
    main()
