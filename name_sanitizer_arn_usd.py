import c4d, loutils
from c4d import gui

# renames objects materials and poly selection tags so the names
# are consistent during export, if names have special characters
# or exact same names they can and will get mangled by the C4D
# export process, this is bad as we rely on exact same names for
# many of our tools in other programs

def main():
    loutils.name_sanitizer(doc, '_', False)

if __name__=='__main__':
    main()