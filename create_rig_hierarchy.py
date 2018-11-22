import c4d
from c4d import gui
#Welcome to the world of Python


def main():
    doc.StartUndo();
    doc.AddUndo(c4d.UNDOTYPE_CHANGE, op);
    baseGenesis = op;
    mainNull = c4d.BaseObject(c4d.Onull);
    mainNull.InsertAfter(baseGenesis);
    mainNull.SetName(baseGenesis.GetName());
    rigNull = c4d.BaseObject(c4d.Onull);
    rigNull.SetName("Rig");
    rigNull.InsertUnder(mainNull);
    genesisHip = baseGenesis.GetDown(); #first child is the hip
    genesisHip.Remove();
    genesisHip.InsertUnder(rigNull);
    genesisMesh = baseGenesis.GetDown(); #only child left is the mesh
    genesisMesh.InsertUnderLast(mainNull);
    baseGenesis.Remove();
    doc.EndUndo();
    
    c4d.EventAdd();
if __name__=='__main__':
    main()
