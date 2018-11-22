import c4d
from c4d import gui

GoZ_CONTAINER_ID = 2000000

def main():
    bc = op.GetData();
    print("ZBrushID: " + bc.GetData(GoZ_CONTAINER_ID));

if __name__=='__main__':
    main()
