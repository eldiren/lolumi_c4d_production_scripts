import c4d
from c4d import gui

DLG_MAIN = 1001
IDC_GRP_OVERRIDES = 1002
IDC_GRP_ALEMBICTREE = 1003
IDC_TRV_ALEMBICTREE = 1004
IDC_TXT_ITERATIONS = 1005
IDC_SLD_ITERATIONS = 1006
IDC_TXT_HEIGHT = 1007
IDC_NUM_HEIGHT = 1008
IDC_TXT_SUBD = 1009
IDC_TXT_SCALAR_ZERO = 1010
IDC_NUM_SCALAR_ZERO = 1011
IDC_TXT_OPAQUE = 1012
IDC_CHK_OPAQUE = 1013
IDC_MENU_SAVE_TEMPLATE = 1014
IDC_MENU_LOAD_TEMPLATE = 1015
IDC_LIST_SOURCE = 1016
IDC_LIST_TARGET = 1017
IDC_BTN_OVERWRITE = 1018
IDC_BTN_CREATE_RIG = 1019
IDC_COMBO_SOURCE = 1020
IDC_COMBO_SUBD_TYPE = 1021
IDC_EMPTY = 2001
#IDC_CHILD_SUBD_CATCLARK,
#IDC_CHILD_SUBD_LINEAR

class testTree(gui.TreeViewFunctions):
    def GetFirst(self, root, userdata):
      return root.GetFirstMaterial()
    
    def GetDown(self, root, userdata, obj):
      return None   
    
    def GetNext(self, root, userdata, obj):
      obj.GetNext()
    
class MyDialog(gui.GeDialog):
    def CreateLayout(self):
      data = c4d.BaseContainer()
      treeFunctions = testTree()
      self.GroupBegin(DLG_MAIN, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, 2,1)
      self.GroupBegin(IDC_GRP_OVERRIDES, c4d.BFH_LEFT | c4d.BFV_SCALEFIT, 2, 1, "", c4d.BFV_GRIDGROUP_EQUALROWS);
      self.GroupBorder(c4d.BORDER_IN)
      self.AddStaticText(IDC_TXT_OPAQUE, c4d.BFH_FIT , 0, 0, "Opaque");
      self.AddCheckbox(IDC_CHK_OPAQUE, c4d.BFH_FIT, 25, 0, "");
      self.AddStaticText(IDC_TXT_ITERATIONS, c4d.BFH_LEFT, 0, 0, "Iterations");
      self.AddEditSlider(IDC_SLD_ITERATIONS, c4d.BFH_SCALEFIT);
      self.SetInt32(IDC_SLD_ITERATIONS, 0, 0, 10);
      self.AddStaticText(IDC_TXT_HEIGHT, c4d.BFH_LEFT , 0, 0, "Height");
      self.AddEditNumberArrows(IDC_NUM_HEIGHT, c4d.BFH_FIT, 25, 0);
      self.SetInt32(IDC_NUM_HEIGHT, 100);
      self.AddStaticText(IDC_TXT_SCALAR_ZERO, c4d.BFH_LEFT , 0, 0, "Height");
      self.AddEditNumberArrows(IDC_NUM_SCALAR_ZERO, c4d.BFH_FIT, 25, 0);
      self.AddStaticText(IDC_TXT_SUBD, c4d.BFH_LEFT, 0, 0, "Suddivision Type");
      self.AddComboBox(IDC_COMBO_SUBD_TYPE, c4d.BFH_SCALEFIT, 300);
      self.AddChild(IDC_COMBO_SUBD_TYPE, 0, "Catclark");
      self.AddChild(IDC_COMBO_SUBD_TYPE, 1, "Linear");
      self.GroupEnd();
      
      self.GroupBegin(IDC_GRP_ALEMBICTREE, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, 2, 1, "", c4d.BFV_GRIDGROUP_EQUALROWS);
      treeGUI = self.AddCustomGui(IDC_TRV_ALEMBICTREE, c4d.CUSTOMGUI_TREEVIEW, "", c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, 0, 0)
      self.GroupEnd();
      
      self.GroupEnd();
      
      data.SetInt32(0, c4d.LV_TREE)
      treeGUI.SetLayout(1, data)
      treeGUI.SetRoot(doc, treeFunctions, None)
      return True; 
    
    def InitValues(self):
      return True
  
    def Command(self, id, msg):
      return True
        
def main():
    dialog = MyDialog()
    
    dialog.Open(c4d.DLG_TYPE_ASYNC)


if __name__=='__main__':
    main()
