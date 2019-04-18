import c4d, loutils
from c4d import gui
 
def IterateHierarchy(op):
    if op is None:
        return
 
    count = 0
  
    while op:
        count += 1
        print op.GetName()
        op = loutils.GetNextObject(op)
 
    return count

def main():
    IterateHierarchy(op);
    
if __name__=='__main__':
    main()
