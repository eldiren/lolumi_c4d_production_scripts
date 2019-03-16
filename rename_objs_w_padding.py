import c4d
from c4d import gui
# will rename objects with a number padding, the fouth value of the
# function set to True will do the children fo the object instead

def main():
    name = "monitor_speaker-"
    loutils.renameObjsPadding(doc, name, 3)

if __name__=='__main__':
    main()