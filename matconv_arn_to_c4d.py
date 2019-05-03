import c4d
from c4d import gui

def main():
    mats = doc.GetMaterials();
    
    for mat in mats:
        new_mat = c4d.BaseMaterial(c4d.Mmaterial); # create standard material
        new_mat[c4d.ID_BASELIST_NAME] = mat.GetName() +"_c4d";
        doc.InsertMaterial(new_mat,pred=None,checknames=True);
        
        # Transfer references of the old material to the new material
        mat.TransferGoal(new_mat, False);
        
    c4d.EventAdd();
    

if __name__=='__main__':
    main()
