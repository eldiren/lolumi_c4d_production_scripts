import c4d
from c4d import gui

# To Use: Select the group that contains the maya ctrl grps

# this script goes through ctrl groups imported from maya, attempts
# to find the same named joint in the C4D scene, and does a PSR
# constraint

# get the next object in a heriarchy, allows inclusive searches by using parent arg
def GetNextObject(obj, parent):
    # print("Getting next object...")
    if not obj: 
        return None
  
    if(obj.GetDown() != None):
        return obj.GetDown()
  
    while (not obj.GetNext() and obj.GetUp() and (obj.GetUp() != parent)):
        obj = obj.GetUp()
     
    return obj.GetNext()

def main():
    ctrl = op
    while GetNextObject(ctrl, op):
        if ctrl.GetName()[-8:] == "ctrl_grp":
            main_ctrl = ctrl.GetDown()
            if main_ctrl != None:
                c4d_jnt_name = main_ctrl.GetName()[:-5]
                #print "Control clean name" + c4d_jnt_name
                jnt = doc.SearchObject(c4d_jnt_name)
                if jnt != None:
                    print "Joint name:" + jnt.GetName()
                    cnstTag = jnt.MakeTag(1019364) # Constraint Tag
                    cnstTag[c4d.ID_CA_CONSTRAINT_TAG_PSR] = 1
                    cnstTag[10001] = main_ctrl
        
        ctrl = GetNextObject(ctrl, op)
            
if __name__=='__main__':
    main()
