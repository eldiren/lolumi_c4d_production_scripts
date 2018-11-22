import c4d
from c4d import gui

def main():
    matList = doc.GetActiveMaterials()
    prefix = "avengers_building_"
    suffix = "_arnold_mat"

    for mat in matList:
        print mat
        mat.SetName(prefix + mat.GetName() + suffix);
        
    c4d.EventAdd();

if __name__=='__main__':
    main()
