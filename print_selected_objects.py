import c4d
from c4d import gui
#Welcome to the world of Python


def main():
    objs = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_CHILDREN)
    for obj in objs:
        print obj.GetName()

if __name__=='__main__':
    main()
