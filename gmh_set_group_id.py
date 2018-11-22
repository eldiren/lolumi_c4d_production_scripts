import c4d
from c4d import gui
#Welcome to the world of Python


def main():
    objs = op.GetChildren()
    index = 0;
    
    for obj in objs:
        tag = BaseTag(1033531); #GMH tag
        tag[c4d.GMH_GROUPID] = index;
        obj.InsertTag(tag);
        tag = obj.GetFirstTag();
        index += 1;
        
    c4d.EventAdd();
    print "done!";

if __name__=='__main__':
    main()
