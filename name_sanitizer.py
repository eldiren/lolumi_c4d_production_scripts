import c4d
from c4d import gui
import re # for regex

# renames objects materials and poly selection tags so the names
# are consistent during export, if names have special characters
# or exact same names they can and will get mangled by the C4D
# export process, this is bad as we rely on exact same names for
# many of our tools in other programs

index = 0
unique_names = []

def GetNextObject(op):
    if op == None:
        return None
  
    if op.GetDown():
        return op.GetDown()
  
    while not op.GetNext() and op.GetUp():
        op = op.GetUp()
  
    return op.GetNext()

def SanitizeEndNumber(name, symbol):
    # C4D Alembic mangles numbers at the end if they begin
    # with '_', so we check that and convert to '-'
    if(name.split(symbol)[-1].isdigit()):
        nname_parse = name.rsplit(symbol, 1)
        name = nname_parse[0] + '-' + nname_parse[1]
        print name
        
    return name 
         
def CompareName(name, symbol):
    # compares a name with a list of stored names and if it matches
    # creates a new unique name base on a acculated index
    global index
    global unique_names
    
    newname = None
    for cname in unique_names:
        if name == cname:
            newname = name + symbol + str(index)    
            
            newname = SanitizeEndNumber(newname, symbol)
            unique_names.append(newname)
            index += 1
            return newname
    
    name = SanitizeEndNumber(name, symbol)
    unique_names.append(name)
    
    return name

def sanitize_name(obj, symbol):
    # replaces invalid symbols in a name with the symbol specified
    # by the user, then compares it against the unique name list
    name = obj.GetName()
    
    newname = re.sub(r"[/\?\[\.|_\- \]#]", symbol, name)
    newname = newname.lower()
        
    newname = CompareName(newname, symbol)
    
    #print newname
    obj.SetName(newname)

def main():
    # sanitize objects
    obj = doc.GetFirstObject()
    
    if obj is None:
        return
    
    while obj:
        sanitize_name(obj, "_")
        
        tag = obj.GetFirstTag()
        while tag:
            if tag.GetType() == 5673: # poly selection
                # it's possible that a selection could have the
                # same name as another on a different object
                # this is a material conflict in other programs
                # also selections that begin with a number are a 
                # no go as well, so this works great
                
                old_sel_name = tag.GetName()
                
                tag.SetName(obj.GetName() + "_" + tag.GetName())
                
                sanitize_name(tag, "_")
                
                new_sel_name = tag.GetName()
                
                # Selection tags aren't linked, we have to go
                # the texture tags replacing the old name with the 
                #new one
                textag = obj.GetFirstTag()
                while textag:
                    if textag.GetType() == 5616: # texture tag
                        if old_sel_name == textag[c4d.TEXTURETAG_RESTRICTION]:
                            textag[c4d.TEXTURETAG_RESTRICTION] = new_sel_name
                            
                    textag = textag.GetNext()        
                
            tag = tag.GetNext()

        obj = GetNextObject(obj)
     
    c4d.EventAdd()
    
    # sanitize materials
    mat = doc.GetFirstMaterial()
    
    if mat is None:
        return
    
    while mat:
        sanitize_name(mat, "_")

        mat = mat.GetNext()
     
    c4d.EventAdd()

if __name__=='__main__':
    main()
