# select the main character null and the mesh with pose morphs and the script
# creates userdata to bind the pose morphs on the null, as well as face controls
# you can then use this with Dynamixyz or other face tools

import c4d
import loutils
from c4d import gui

def constrainToCtrl(jnt, ctrl):
    ctag = jnt.MakeTag(1019364)
    #ctag[c4d.ID_CA_CONSTRAINT_TAG_PARENT] = True
    #ctag[c4d.ID_CA_CONSTRAINT_TAG_PARENT_MAINTAIN] = True
    #ctag[30001] = ctrl # parent target
    ctag[c4d.ID_CA_CONSTRAINT_TAG_PSR] = True
    ctag[c4d.ID_CA_CONSTRAINT_TAG_PSR_MAINTAIN] = True
    ctag[10001] = ctrl # psr target

def createCtrl(rig, child, type = 0, name = None, off = None):
    if type == 0 or type == 1:
        ctrl = c4d.BaseObject(c4d.Osplinecircle)
        ctrl[c4d.PRIM_CIRCLE_RADIUS] = .5
    else:
        ctrl = c4d.BaseObject(c4d.Ospline4side)
        ctrl[c4d.PRIM_4SIDE_A] = 2
        ctrl[c4d.PRIM_4SIDE_B] = 2

    if type == 1:
        ctrl[c4d.PRIM_CIRCLE_ELLIPSE] = 1
        ctrl[c4d.PRIM_CIRCLE_RADIUSY] = .15

    ctrl.InsertUnder(rig)
    if name:
        ctrl.SetName(name)
    else:
        ctrl.SetName(child.GetName() + '_CTRL')

    ctrl.SetMg(child.GetMg())

    res = c4d.utils.SendModelingCommand(command = c4d.MCOMMAND_MAKEEDITABLE,
                            list = [ctrl],
                            mode = c4d.MODELINGCOMMANDMODE_ALL,
                            doc = doc)

    if res:
        ctrl = res[0]
        ctrl.InsertUnder(rig)
        ctrl[c4d.ID_BASEOBJECT_USECOLOR] = 2

        pnts = ctrl.GetAllPoints()
        for i in xrange(len(pnts)):
            pnts[i].z -= 2

            if off:
                pnts[i] += off

        ctrl.SetAllPoints(pnts)

        if child.GetName()[0] == 'r':
            ctrl[c4d.ID_BASEOBJECT_COLOR] = c4d.Vector(1,0,0)
        elif child.GetName()[0] == 'l':
            ctrl[c4d.ID_BASEOBJECT_COLOR] = c4d.Vector(0,0,1)
        else:
            ctrl[c4d.ID_BASEOBJECT_COLOR] = c4d.Vector(0,1,0)
            
        ctrl.SetFrozenPos(ctrl.GetAbsPos())
        ctrl.SetFrozenRot(ctrl.GetAbsRot())
        ctrl.SetFrozenScale(ctrl.GetAbsScale())
        ctrl.SetRelPos(c4d.Vector(0))
        ctrl.SetRelRot(c4d.Vector(0))
        ctrl.SetRelScale(c4d.Vector(1))
        
        return ctrl

    return None

def main():
    objs = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_CHILDREN)
    if len(objs) < 2:
        print 'Must select main character null, and character body mesh'
        return

    fchild = objs[0].GetDown()
    if not fchild:
        return

    upperFaceRig = doc.SearchObject('upperFaceRig')
    lowerFaceRig = doc.SearchObject('lowerFaceRig')

    if upperFaceRig and lowerFaceRig:
        rig = c4d.BaseObject(c4d.Onull)

        rig.InsertBefore(fchild)
        rig.SetName('faceRig')

        doc.StartUndo()
        child = upperFaceRig.GetDown()
        leyelidupperCtrl = None
        leyelidlowerCtrl = None
        reyelidupperCtrl = None
        reyelidlowerCtrl = None

        if child:
            while(child):
                if 'rEyelidUpper' in child.GetName():
                    if reyelidupperCtrl:
                        constrainToCtrl(child, reyelidupperCtrl)
                    else:
                        reyelidupperCtrl = createCtrl(rig, child, 1, 'rEyelidUpper_CTRL', c4d.Vector(0,.5,0))
                        constrainToCtrl(child, reyelidupperCtrl)
                elif 'lEyelidUpper' in child.GetName():
                    if leyelidupperCtrl:
                        constrainToCtrl(child, leyelidupperCtrl)
                    else:
                        leyelidupperCtrl = createCtrl(rig, child, 1, 'lEyelidUpper_CTRL', c4d.Vector(0,.5,0))
                        constrainToCtrl(child, leyelidupperCtrl)
                elif 'rEyelidLower' in child.GetName():
                    if reyelidlowerCtrl:
                        constrainToCtrl(child, reyelidlowerCtrl)
                    else:
                        reyelidlowerCtrl = createCtrl(rig, child, 1, 'rEyelidLower_CTRL', c4d.Vector(0,-.5,0))
                        constrainToCtrl(child, reyelidlowerCtrl)
                elif 'lEyelidLower' in child.GetName():
                    if leyelidlowerCtrl:
                        constrainToCtrl(child, leyelidlowerCtrl)
                    else:
                        leyelidlowerCtrl = createCtrl(rig, child, 1, 'lEyelidLower_CTRL', c4d.Vector(0,-.5,0))
                        constrainToCtrl(child, leyelidlowerCtrl)
                elif 'lEyelidInner' in child.GetName():
                    ctrl = createCtrl(rig, child, off = c4d.Vector(1,0,0))
                    constrainToCtrl(child, ctrl)
                elif 'lEyelidOuter' in child.GetName():
                    ctrl = createCtrl(rig, child, off = c4d.Vector(-1,0,0))
                    constrainToCtrl(child, ctrl)
                elif 'rEyelidInner' in child.GetName():
                    ctrl = createCtrl(rig, child, off = c4d.Vector(1,0,0))
                    constrainToCtrl(child, ctrl)
                elif 'rEyelidOuter' in child.GetName():
                    ctrl = createCtrl(rig, child, off = c4d.Vector(-1,0,0))
                    constrainToCtrl(child, ctrl)
                else:
                    ctrl = createCtrl(rig, child)
                    constrainToCtrl(child, ctrl)

                child = child.GetNext()

        child = lowerFaceRig.GetDown()
        if child:
            # we want to create the jaw, lower face objects go underneath it
            lowerJaw = doc.SearchObject('lowerJaw')

            if lowerJaw:
                chin = doc.SearchObject('Chin') # it's in a similar position to the chin
                if chin:
                    chinPos = chin.GetAbsPos()
                    jawPos = lowerJaw.GetAbsPos()
                    cOff = chinPos - jawPos
                    cOff.y -= .8
                    cOff.z -= 1.5
                    jawCtrl = createCtrl(rig, lowerJaw, type = 2, off=cOff)
                    constrainToCtrl(lowerJaw, jawCtrl)

                    while(child):
                        ctrl = createCtrl(jawCtrl, child)
                        constrainToCtrl(child, ctrl)

                        child = child.GetNext()

        tag = objs[1].GetTag(c4d.Tposemorph)
        if tag:
            loutils.createUserDataLink(objs[0], 'mesh', val=objs[1])

            mCnt = tag.GetMorphCount()
            for i in range(mCnt):
                morph = tag.GetMorph(i)
                loutils.createUserDataFloatSlider(objs[0], morph.GetName())

            pTag = objs[0].MakeTag(c4d.Tpython)
            pTag[c4d.TPYTHON_CODE] = 'import c4d\r\n\r\ndef main():\r\n    obj = op.GetObject()\r\n    mesh = obj[c4d.ID_USERDATA, 1]\r\n    tag = mesh.GetTag(c4d.Tposemorph)\r\n    mCnt = tag.GetMorphCount()\r\n    for i in range(mCnt):\r\n        morph = tag.GetMorph(i)\r\n        uData = obj[c4d.ID_USERDATA, i+2]\r\n        tag[4000,1001+(100*(i))] = uData'

        doc.EndUndo()

        c4d.EventAdd()

if __name__=='__main__':
    main()