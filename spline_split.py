import c4d
from c4d import gui
from c4d.gui import GetInputState
#splits a spline into its consitute elements, usually useful for prepping
# cloth panels for qualoth

def escape_pressed():
    bc = c4d.BaseContainer()
    rs = GetInputState(c4d.BFM_INPUT_KEYBOARD, c4d.KEY_ESC, bc)
    if rs and bc[c4d.BFM_INPUT_VALUE]:
        return True
    return False

def main():
    doc.StartUndo();
    doc.AddUndo(c4d.UNDO_OBJECT, op);
    c4d.CallCommand(12139); # Enter Point Mode
  
    if (op and isinstance(op,c4d.SplineObject)): # only spline objects allowed
  
        selection = op.GetPointS();
        selection.DeselectAll();
        c4d.EventAdd();
    
        pCount = op.GetPointCount();
        i = 0;
        
        while i < pCount:
            selection.Select(i);
            i += 1;
            selection.Select(i);
            c4d.CallCommand(14029); # disconnect
            selection.DeselectAll();
            pCount = op.GetPointCount();
            i += 1;
            escape_pressed();
      
    
    selection.DeselectAll();
    c4d.CallCommand(13316); # Explode Segments
    c4d.EventAdd();
    print("Spline Split: Created ", pCount/2, " splines.");
  
    doc.EndUndo();

if __name__=='__main__':
    main()
