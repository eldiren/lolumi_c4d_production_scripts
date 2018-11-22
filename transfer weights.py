import c4d
from c4d import gui, documents
from types import *
# this script copies weights from a genesis figure to the
# custom c4d genesis rig, point counts of both rigs need to
# match

global sourceWeights
global targetWeights
global meshPntCnt

class transferGenesisW(gui.GeDialog):
   
    def CreateLayout(self):
        #create the layout of the dialog
        self.SetTitle("Genesis Weight Transfer")
        self.GroupBegin(1001, c4d.BFH_SCALEFIT, 2, 3)
        self.AddStaticText(1002, flags=c4d.BFH_LEFT, initw=100, name="Source")
        self.sourceLink = self.AddCustomGui(1003, c4d.CUSTOMGUI_LINKBOX, "",
         c4d.BFH_SCALEFIT|c4d.BFV_SCALEFIT, 400, 0)
        self.AddStaticText(1003, flags=c4d.BFH_LEFT, initw=100, name="Target")
        self.targetLink = self.AddCustomGui(1004, c4d.CUSTOMGUI_LINKBOX, "",
         c4d.BFH_SCALEFIT|c4d.BFV_SCALEFIT, 400, 0)
         
        self.AddButton(1005, c4d.BFH_SCALE, name="Execute")
        self.GroupEnd()
        
        return True
   
    def InitValues(self):
        #initiate the gadgets with values
        return True
   
    def Command(self, id, msg):
        #handle user input
        if id==1005:
            self.TranferWeight()
        return True
    
    # transfer weights between source and target joint, takes the names
    # as args
    def JointTransfer(self, sJntName, tJntName):
        global sourceWeights
        global targetWeights
        global meshPntCnt
        
        sJntIndex = 0; #Setup the source joint index
        dJntIndex = 0; #Setup the destination joint index
        
        # we need the joint count so we can do a name match search
        # through all the joints in the weight tags
        jntCount = sourceWeights.GetJointCount()
        
        #quick loop to find source joint in the source genesis rig
        for i in range(0, jntCount): 
            jnt = sourceWeights.GetJoint(i, doc)
            if(type(jnt) != NoneType):
                if jnt.GetName() == sJntName:
                    sJntIndex = i
                    break
            
        #quick loop to find target joint in the destination genesis rig
        jntCount = targetWeights.GetJointCount()
        for i in range(0, jntCount):
            jnt = targetWeights.GetJoint(i, doc)
            if(type(jnt) != NoneType):
                if jnt.GetName() == tJntName:
                    dJntIndex = i
                    break
        
        # we are going to brute force this. we'll go through every vertex
        # on the mesh and check if this joint is weighted. if it is we'll
        # set the weight on our new mesh 
        for i in range(0, meshPntCnt):
            #Get the weight of the current vertex
            weight = sourceWeights.GetWeight(sJntIndex, i)
            
            #Set the weight to target mesh and joint
            targetWeights.SetWeight(dJntIndex, i, weight)
                
        return
    
    #Do the weight transfer
    def TranferWeight(self):
        global sourceWeights
        global targetWeights
        global meshPntCnt
        
        #Gets the link to the source weight tag
        sourceWeights = self.sourceLink.GetLink().GetTag(c4d.Tweights)
        
        #Get the link to the target weight tag
        targetWeights = self.targetLink.GetLink().GetTag(c4d.Tweights)
        
        #The mesh point count
        meshPntCnt = self.sourceLink.GetLink().GetPointCount()
        
        # use a custom function to transfer joints
        self.JointTransfer("abdomen", "abdomen_skn")
        self.JointTransfer("abdomen2", "abdomen2_skn")
        self.JointTransfer("chest", "chest_skn")
        self.JointTransfer("lPectoral", "l_Pectoral_skn")
        self.JointTransfer("rPectoral", "r_Pectoral_skn")
        self.JointTransfer("neck", "neck_skn")
        self.JointTransfer("head", "head_skn")
        self.JointTransfer("lEye", "l_Eye_skn")
        self.JointTransfer("rEye", "r_Eye_skn")
        self.JointTransfer("pelvis", "pelvis_skn")
        self.JointTransfer("lThigh", "l_Thigh_skn")
        self.JointTransfer("lShin", "l_Shin_skn")
        self.JointTransfer("lFoot", "l_Foot_skn")
        self.JointTransfer("lToe", "l_Toe_skn")
        self.JointTransfer("lBigToe", "l_BigToe_skn")
        self.JointTransfer("rThigh", "r_Thigh_skn")
        self.JointTransfer("rShin", "r_Shin_skn")
        self.JointTransfer("rFoot", "r_Foot_skn")
        self.JointTransfer("rToe", "r_Toe_skn")
        self.JointTransfer("rBigToe", "r_BigToe_skn")
        self.JointTransfer("lCollar", "l_Collar_skn")
        self.JointTransfer("lShldr", "l_Shldr_skn")
        self.JointTransfer("lForeArm", "l_ForeArm_skn")
        self.JointTransfer("lHand", "l_Hand_skn")
        self.JointTransfer("lThumb1", "l_Thumb1_skn")
        self.JointTransfer("lThumb2", "l_Thumb2_skn")
        self.JointTransfer("lThumb3", "l_Thumb3_skn")
        self.JointTransfer("lCarpal1", "l_Carpal1_skn")
        self.JointTransfer("lCarpal2", "l_Carpal2_skn")
        self.JointTransfer("lIndex1", "l_Index1_skn")
        self.JointTransfer("lIndex2", "l_Index2_skn")
        self.JointTransfer("lIndex3", "l_Index3_skn")
        self.JointTransfer("lMid1", "l_Mid1_skn")
        self.JointTransfer("lMid2", "l_Mid2_skn")
        self.JointTransfer("lMid3", "l_Mid3_skn")
        self.JointTransfer("lRing1", "l_Ring1_skn")
        self.JointTransfer("lRing2", "l_Ring2_skn")
        self.JointTransfer("lRing3", "l_Ring3_skn")
        self.JointTransfer("lPinky1", "l_Pinky1_skn")
        self.JointTransfer("lPinky2", "l_Pinky2_skn")
        self.JointTransfer("lPinky3", "l_Pinky3_skn")
        self.JointTransfer("rCollar", "r_Collar_skn")
        self.JointTransfer("rShldr", "r_Shldr_skn")
        self.JointTransfer("rForeArm", "r_ForeArm_skn")
        self.JointTransfer("rHand", "r_Hand_skn")
        self.JointTransfer("rThumb1", "r_Thumb1_skn")
        self.JointTransfer("rThumb2", "r_Thumb2_skn")
        self.JointTransfer("rThumb3", "r_Thumb3_skn")
        self.JointTransfer("rCarpal1", "r_Carpal1_skn")
        self.JointTransfer("rCarpal2", "r_Carpal2_skn")
        self.JointTransfer("rIndex1", "r_Index1_skn")
        self.JointTransfer("rIndex2", "r_Index2_skn")
        self.JointTransfer("rIndex3", "r_Index3_skn")
        self.JointTransfer("rMid1", "r_Mid1_skn")
        self.JointTransfer("rMid2", "r_Mid2_skn")
        self.JointTransfer("rMid3", "r_Mid3_skn")
        self.JointTransfer("rRing1", "r_Ring1_skn")
        self.JointTransfer("rRing2", "r_Ring2_skn")
        self.JointTransfer("rRing3", "r_Ring3_skn")
        self.JointTransfer("rPinky1", "r_Pinky1_skn")
        self.JointTransfer("rPinky2", "r_Pinky2_skn")
        self.JointTransfer("rPinky3", "r_Pinky3_skn")
                
        # update scene and object  
        self.targetLink.GetLink().Message(c4d.MSG_UPDATE)
        c4d.EventAdd()
       
        
        return True
   
dlg = transferGenesisW()
dlg.Open(c4d.DLG_TYPE_ASYNC, defaultw=300, defaulth=50)