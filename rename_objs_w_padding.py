import c4d
from c4d import gui
# will rename objects with a number padding, comment the type of
# objs you don't want out, ActiveObjects gets the selected, GetChildren
# gets the children of the selected

def main():
    objs = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_0)
    #objs = op.GetChildren()
    i = 0
    for obj in objs:
        num = str(i)
        name = "monitor_speaker-" + num.zfill(3)
        obj.SetName(name)
        i += 1
        
    c4d.EventAdd()

if __name__=='__main__':
    main()
