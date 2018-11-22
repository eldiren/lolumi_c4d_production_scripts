import c4d
from c4d import gui
#Welcome to the world of Python

def GetNextObject(op):
    if op==None:
        return None
  
    if op.GetDown():
        return op.GetDown()
  
    while not op.GetNext() and op.GetUp():
        op = op.GetUp()
  
    return op.GetNext()
 
 
def IterateHierarchy(op):
    if op is None:
        return
 
    count = 0
  
    while op:
        count += 1
        print op.GetName()
        op = GetNextObject(op)
 
    return count

def main():
    IterateHierarchy(op);
    
if __name__=='__main__':
    main()
