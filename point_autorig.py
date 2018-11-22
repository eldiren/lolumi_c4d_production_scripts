#Copyright (c) 2013, Curious Animal Limited
#All rights reserved.
#
#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions are met:
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of Curious Animal Limited nor the
#      names of its contributors may be used to endorse or promote products
#      derived from this software without specific prior written permission.
#
#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
#ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#DISCLAIMED. IN NO EVENT SHALL CURIOUS ANIMAL LIMITED BE LIABLE FOR ANY
#DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import c4d
import c4d.utils
from c4d import gui
#Welcome to the world of Python

#These multi-line strings are going to be put into our rig's Python tag later
pythontagcode_spline = """#pointrig tagcode
import c4d
#Welcome to the world of Python

def main():
    #We're going to loop through all the nulls and set our points to their positions
    spline = op.GetObject()
    children = spline.GetChildren()
    
    if spline.GetTangentCount() >= spline.GetPointCount():
        tangents = True
    else:
        tangents = False
    index = 0
    for child in children:
        #In case the user puts other stuff inside the object,
        #we're only going to check the nulls
        if child.GetType() == c4d.Onull:
            #if the user has changed the order of nulls, we make sure to add the current point index
            #at the end of the null's name to make it easier to tell what point we're manipulating
            suffix = str(index)
            currentname = child[c4d.ID_BASELIST_NAME]
            if (currentname[len(currentname)-len(suffix):] != suffix):
                #if we've already added a new point index, alter that rather than adding new numbers,
                #otherwise we'd get ever longer cumbersome names
                dashindex = currentname.rfind('--')
                if dashindex > -1:
                    currentname = currentname[:dashindex]
                child[c4d.ID_BASELIST_NAME] = currentname + '--' + suffix
                
            spline.SetPoint(index, child.GetAbsPos())
            #If there are tangents, use the tangent nulls to control them
            if tangents:
                pointmatrix = child.GetMl()
                pointmatrix.off = c4d.Vector()
                
                tangentleft = child.GetDown()
                tangentright = tangentleft.GetNext()                                
                spline.SetTangent(index, tangentleft.GetAbsPos() * pointmatrix, tangentright.GetAbsPos() * pointmatrix)
            index += 1
            #stop when we get to the last point
            if index >= spline.GetPointCount():
                break
    spline.Message(c4d.MSG_UPDATE)"""
pythontagcode = """#pointrig tagcode
import c4d
#Welcome to the world of Python

def main():
    #We're going to loop through all the nulls and set our points to their positions
    object = op.GetObject()
    children = object.GetChildren()
    
    index = 0
    for child in children:
        #In case the user puts other stuff inside the object,
        #we're only going to check the nulls
        if child.GetType() == c4d.Onull:
            #if the user has changed the order of nulls, we make sure to add the current point index
            #at the end of the null's name to make it easier to tell what point we're manipulating
            suffix = str(index)
            currentname = child[c4d.ID_BASELIST_NAME]
            if (currentname[len(currentname)-len(suffix):] != suffix):
                #if we've already added a new point index, alter that rather than adding new numbers,
                #otherwise we'd get ever longer cumbersome names
                dashindex = currentname.rfind('--')
                if dashindex > -1:
                    currentname = currentname[:dashindex]
                child[c4d.ID_BASELIST_NAME] = currentname + '--' + suffix
                
            object.SetPoint(index, child.GetAbsPos())
            index += 1
            #stop when we get to the last point
            if index >= object.GetPointCount():
                break
    object.Message(c4d.MSG_UPDATE)"""

#Add a new null in the same place as the point at 'index',
#if the point has a tangent (eg for Bezier splines), match the null's scale
#and rotation to match the tangent
def addHandle(index, object):
    #create a new null
    controlnull = c4d.BaseObject(c4d.Onull)        
    
    
    if object.GetType() == c4d.Ospline:
        #add nulls for the left and right tangents, add them to the main control null, and alter their appearance
        tangentleft = c4d.BaseObject(c4d.Onull)
        tangentright = c4d.BaseObject(c4d.Onull)
        tangentright.InsertUnder(controlnull)
        tangentleft.InsertUnder(controlnull)
        tangentleft[c4d.ID_BASELIST_NAME] = 'Left tangent'
        tangentright[c4d.ID_BASELIST_NAME] = 'Right tangent'
        tangentleft.SetAbsPos(c4d.Vector(0,0,controlnull[c4d.NULLOBJECT_RADIUS]))
        tangentright.SetAbsPos(c4d.Vector(0,0,-controlnull[c4d.NULLOBJECT_RADIUS]))
        tangentleft[c4d.NULLOBJECT_DISPLAY] = 4
        tangentright[c4d.NULLOBJECT_DISPLAY] = 4
        tangentleft[c4d.NULLOBJECT_RADIUS] = 5
        tangentright[c4d.NULLOBJECT_RADIUS] = 5
        #If there are tangents, use them to set the angle and scale of the main null, and the position of the tangent nulls.
        #We can control the tangents by rotating and scaling the main null (this will maintain the ratios of the
        #tangents, but we can change their lengths and orientation easily), as well as by moving the tangent nulls
        #within that null (giving us full control of the tangents if needed, allowing us to break them)
        if object.GetTangentCount() > index:
            tangent = object.GetTangent(index)['vl']
            newrot = c4d.utils.VectorToHPB(tangent)     
            controlnull.SetAbsRot(newrot)
            scale = tangent.GetLength() / controlnull[c4d.NULLOBJECT_RADIUS]
            newscale = c4d.Vector(1,1,1)
            newscale.z = tangent.GetLength() / controlnull[c4d.NULLOBJECT_RADIUS]
            controlnull.SetAbsScale(newscale)
            
            
            tangentleft.SetAbsPos(object.GetTangent(index)['vl'] * ~controlnull.GetMl())
            tangentright.SetAbsPos(object.GetTangent(index)['vr'] * ~controlnull.GetMl())
        
    #put the null where the object's point is
    newpos = object.GetPoint(index)                
    controlnull.SetAbsPos(newpos)
    #change the appearance of the null to make it easier to see where it is and how it's oriented
    controlnull[c4d.NULLOBJECT_DISPLAY] = 13
    controlnull[c4d.NULLOBJECT_ORIENTATION] = 1
    controlnull[c4d.ID_BASELIST_NAME] = object[c4d.ID_BASELIST_NAME] + '.Control.' + str(index)
        
    return controlnull

#Create a new rig from scratch
def new_rig(object):
    doc.StartUndo()
    doc.AddUndo(c4d.UNDOTYPE_CHANGE, object)          
        
    #create a Python tag and attach it to the first joint
    pythontag = c4d.BaseTag(c4d.Tpython)
    object.InsertTag(pythontag)
    doc.AddUndo(c4d.UNDOTYPE_NEW, pythontag)
    #set the Python code inside the tag - splines get their own code that deals with tangents
    if(object.GetType()==c4d.Ospline):
        pythontag[c4d.TPYTHON_CODE] = pythontagcode_spline
    else:
        pythontag[c4d.TPYTHON_CODE] = pythontagcode            
        
    pointcount = object.GetPointCount()
        
    prevlist = None
    #loop through all the points, adding nulls for each one
    for i in xrange(pointcount):
        controlnull = addHandle(i, object)
        #if this is the first null, stick it under the object we're rigging,
        #otherwise put it after the last null ('prevlist') - then put this null into 'prevlist'
        #so the next null knows where to go
        if prevlist==None:
            controlnull.InsertUnder(object)
        else:
            controlnull.InsertAfter(prevlist)
        prevlist = controlnull
        doc.AddUndo(c4d.UNDOTYPE_NEW, controlnull)
        
    doc.EndUndo()
    c4d.EventAdd(c4d.EVENT_FORCEREDRAW)
    
    print "Point rig added successfully!"

def getNullCount(object):
    children = object.GetChildren()
    
    nullcount = 0
    
    for child in children:
        if child.GetType() == c4d.Onull:
            nullcount += 1
            
    return nullcount

#Update an existing rig
def update_rig(object):    
    #Find how many handles are already in the Spline-IK tag
    nullcount = getNullCount(object)
            
    pointcount = object.GetPointCount()
    #if there are already enough nulls and handles, the rig is up to date and we don't need to do anything
    if nullcount >= pointcount:
        print "Point rig already up to date"
        return
            
    doc.StartUndo()
    
    prevlist = object.GetDownLast()
    #Add new handles and nulls to fill the difference between the current number of handles and the new
    #number of points
    for i in xrange(nullcount, pointcount):
        #the inside of this loop is the same as the loop inside the 'new_rig' function
        controlnull = addHandle(i, object)
        if prevlist==None:
            controlnull.InsertUnder(object)
        else:
            controlnull.InsertAfter(prevlist)
        prevlist = controlnull
        doc.AddUndo(c4d.UNDOTYPE_NEW, controlnull)
        
    doc.EndUndo()
    c4d.EventAdd(c4d.EVENT_FORCEREDRAW)
    
    print "Point rig updated successfully!"

def getTagsByType(tags, tagtype):
    newtags = []
    for tag in tags:
        if tag.GetType() == tagtype:
            newtags.append(tag)
    return newtags

def main():
    #Quit early if nothing is selected or if the selection isn't a spline, polygon or FFD
    if op==None:
        print 'Please apply the "point-autorig" script to an editable spline, polygon or FFD object.'
        gui.MessageDialog('Please apply the "point-autorig" script to an editable spline, polygon or FFD object.')
        return None
    if not (op.GetType() == c4d.Ospline or op.GetType() == c4d.Offd or op.GetType() == c4d.Opolygon):
        print 'Please apply the "point-autorig" script to an editable spline, polygon or FFD object.'
        gui.MessageDialog('Please apply the "point-autorig" script to an editable spline, polygon or FFD object.')
        return None
        
    #Test for existing rig - if there is one, update it (this allows us to keep any
    #existing animation, although you might have to manually change the order of nulls
    #depending on where your new points are)
    #The test looks for any Python tag starting with the teststring ("#pointrig tagcode") 
    pythontags = getTagsByType(op.GetTags(), c4d.Tpython)
    teststring = "#pointrig tagcode"
    for tag in pythontags:
        if tag[c4d.TPYTHON_CODE][:len(teststring)]==teststring:            
            update_rig(op)
            return
    
    #If there isn't already a rig, create one
    new_rig(op)

if __name__=='__main__':
    main()