import c4d
from c4d import bitmaps, gui, plugins, documents
from types import *

#This script tranfers the animation from a set of nulls to IK controllers of the custom
#lumiere rig

MainDialog = 1001
TXT_SOURCE = 1002
TXT_TARGET = 1003
LNK_SOURCE = 1004
LNK_TARGET = 1005
BTN_EXCUTE = 1006

class transferAnimation(gui.GeDialog):
   
    def CreateLayout(self):
        #create the layout of the dialog
        self.SetTitle("Lolumi Animation Transfer")
        self.GroupBegin(MainDialog, c4d.BFH_SCALEFIT, 2, 3)
        self.AddStaticText(TXT_SOURCE, flags=c4d.BFH_LEFT, initw=100, name="Source")
        self.sourceLink = self.AddCustomGui(LNK_SOURCE, c4d.CUSTOMGUI_LINKBOX, "",
         c4d.BFH_SCALEFIT|c4d.BFV_SCALEFIT, 400, 0)
        self.AddStaticText(TXT_TARGET, flags=c4d.BFH_LEFT, initw=100, name="Target")
        self.targetLink = self.AddCustomGui(LNK_TARGET, c4d.CUSTOMGUI_LINKBOX, "",
         c4d.BFH_SCALEFIT|c4d.BFV_SCALEFIT, 400, 0)
         
        self.AddButton(BTN_EXCUTE, c4d.BFH_SCALE, name="Execute")
        self.GroupEnd()
        
        return True
   
    def InitValues(self):
        #initiate the gadgets with values
        return True
   
    def Command(self, id, msg):
        #handle user input
        if id==BTN_EXCUTE:
            self.TransferAnim()
        return True
    
    def TransferAnim(self):
        #Comparison list for Lumiere Rig Template

        ctrlCompList = {
            'hip_CTRL_FK_Dummy' : 'hip_CTRL',
            'r_shldr_CTRL_FK_Dummy' : 'r_shldr_CTRL',
            'l_shldr_CTRL_FK_Dummy' : 'l_shldr_CTRL',
            'r_elbow_CTRL_FK_Dummy' : 'r_elbow_CTRL',
            'l_elbow_CTRL_FK_Dummy' : 'l_elbow_CTRL',
            'l_hand_CTRL_FK_Dummy' : 'l_hand_CTRL',
            'r_hand_CTRL_FK_Dummy' : 'r_hand_CTRL',
            'r_Thumb_CTRL_FK_Dummy' : 'r_Thumb_CTRL',
            'l_Thumb_CTRL_FK_Dummy' : 'l_Thumb_CTRL',
            'r_Pinky_CTRL_FK_Dummy' : 'r_hand_CTRL',
            'l_Pinky_CTRL_FK_Dummy' : 'r_hand_CTRL',
            'r_Ring_CTRL_FK_Dummy' : 'r_hand_CTRL',
            'l_Ring_CTRL_FK_Dummy' : 'r_hand_CTRL'
            'r_Mid_CTRL_FK_Dummy' : 'r_hand_CTRL',
            'l_Mid_CTRL_FK_Dummy' : 'r_hand_CTRL',
            'r_Index_CTRL_FK_Dummy' : 'r_hand_CTRL',
            'l_Index_CTRL_FK_Dummy' : 'r_hand_CTRL',
            'chest_CTRL_FK_Dummy' : 'chest_CTRL',
            'neck_CTRL_FK_Dummy' : 'neck_CTRL',
            'head_CTRL_FK_Dummy' : 'head_CTRL',
            'r_toe_CTRL_FK_Dummy' : 'r_toe_CTRL',
            'l_toe_CTRL_FK_Dummy' : 'l_toe_CTRL',
            'r_ball_CTRL_FK_Dummy' : 'r_ball_CTRL',
            'l_ball_CTRL_FK_Dummy' : 'l_ball_CTRL',
            'r_Knee_CTRL_FK_Dummy' : 'r_Knee_CTRL',
            'l_Knee_CTRL_FK_Dummy' : 'l_Knee_CTRL',
            'r_Foot_CTRL_FK_Dummy' : 'r_Foot_CTRL',
            'l_Foot_CTRL_FK_Dummy' : 'l_Foot_CTRL',
            'r_heel_CTRL_FK_Dummy' : 'r_heel_CTRL',
            'l_heel_CTRL_FK_Dummy' : 'l_heel_CTRL',
            'COG_CTRL_FK_Dummy' : 'COG_CTRL'
            }

        # Get active doc
        doc = c4d.documents.GetActiveDocument()

        # Get project current start and end frames
        startFrameValue = int(doc.GetMinTime().GetFrame(doc.GetFps()))
        endFrameValue = int(doc.GetMaxTime().GetFrame(doc.GetFps()))

        #Get the soucre and target children, we want to iterate through these lists in order to pull
        #out the exact Nulls we need to work with, we also need the counts for out for loops
        sourceChildren = self.sourceLink.GetLink().GetChildren()
        targetChildren = self.targetLink.GetLink().GetChildren()
        sourceChildCnt = len(sourceChildren)
        targetChildCnt = len(targetChildren)

        # deslect all objects, the script set keys on the selected object, so we only want objects active
        # that we make active
        c4d.CallCommand(100004767)

        # loop through the animation as defined by C4D's start and end times in this document, and record a
        # key for every frame
        for frame in range(startFrameValue, endFrameValue):
            # Set the docs current time to the correct frame so we can capture the key
            doc.SetTime(c4d.BaseTime(float(frame)/doc.GetFps()))
            doc.ExecutePasses(None, True, True, True, 0);
            c4d.GeSyncMessage(c4d.EVMSG_TIMECHANGED)

            # loop through the source's children, once we find one of our dummy Nulls we need to then loop
            # through the target children for the coresponding IK controller, finally well animate the power
            # slider and record the dummy's global positions and rotations into the IK as keys
            for i in range(0, sourceChildCnt):
                if(sourceChildren[i].GetName() in ctrlCompList):
                    sourceObj = sourceChildren[i]
                    for j in range(0, targetChildCnt):
                        if(targetChildren[j].GetName() == ctrlCompList[sourceObj.GetName()]):
                            targetObj = targetChildren[j]
                            targetObj.SetBit(c4d.BIT_ACTIVE) #Set target Null active so it can receive keys
                            
                            # get the world postion and rotation of the source dummy Null and apply it the the target IK/FK CTRL
                            #targetObj.SetAbsPos(sourceObj.GetAbsPos()) 
                            #targetObj.SetAbsRot(sourceObj.GetAbsRot())
                            targetObj.SetMg(sourceObj.GetMg())

                            c4d.CallCommand(12410) #Records a key on active object
                            
                            targetObj.DelBit(c4d.BIT_ACTIVE)
                            break


        c4d.EventAdd()
    
if __name__=='__main__':
    dlg = transferAnimation()
    dlg.Open(c4d.DLG_TYPE_ASYNC, defaultw=300, defaulth=50)
